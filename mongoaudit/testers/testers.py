# -*- coding: utf-8 -*-
import socket
import ssl
import time

import pymongo

from .cve import alerts_dec012015, alerts_mar272015, alerts_mar252015, \
    alerts_feb252015, alerts_jun172014, alerts_may052014, alerts_jun202013, alerts_jun052013, \
    alerts_mar062014, alerts_oct012013, alerts_aug152013
from .roles import try_roles
from .tls import available as tls_available, enabled as tls_enabled, valid as tls_valid
from .utils import decode_to_string
from . import TestResult, SUCCESS, ERROR, OMITTED, decorators

OMITTED_MESSAGE = ('This test was omitted because of a missing requirement (e.g.: it depends '
                   'on a previous test that failed).')


class Tester(object):
    """
    Tester
    Args:
      cred (dict(str: str)): credentials
      tests (Test[]): tests to run
    """

    def __init__(self, cred, tests):
        self.retries = 0
        self.cred = cred
        self.tests = [Test(t, self) for t in tests]
        self.conn = self.get_connection()
        self.info = self.get_info()
        self.database = None

    def run(self, each, end):
        """
        Args:
          each (): function to call before each test runs (used to update and redraw the screen)
          end (function): function to call when all the tests have finished running
        """
        result = []
        for test in self.tests:
            each(test)
            res = test.run()
            result.append(res)
            time.sleep(0.5)
            if test.breaks == bool(res['result']):
                break

        if len(result) < len(self.tests):
            result += [{
                'name': x.test_name,
                'severity': x.severity,
                'title': x.title,
                'caption': x.caption,
                'message': OMITTED_MESSAGE,
                'extra_data': None,
                'result': OMITTED
            } for x in self.tests[len(result): len(self.tests)]]

        self.conn.close()
        end(result)

    def get_connection(self):
        """
        Get the most secure kind of connection available.
        Returns:
          pymongo.MongoClient instance

        """
        fqdn, port = self.cred['nodelist'][0]
        if hasattr(self, 'conn'):
            self.conn.close()
            return Tester.get_plain_connection(fqdn, port)
        else:
            return Tester.get_tls_connection(fqdn, port)

    @staticmethod
    def get_tls_connection(fqdn, port):
        """
        Creates an encrypted TLS/SSL connection.
        Returns:
          pymongo.MongoClient instance
        """
        return pymongo.MongoClient(
            fqdn, port, ssl=True, ssl_cert_reqs=ssl.CERT_NONE,
            serverSelectionTimeoutMS=1000)

    @staticmethod
    def get_plain_connection(fqdn, port):
        """
        Creates a cleartext (unencrypted) connection.
        Returns:
          pymongo.MongoClient instance
        """
        return pymongo.MongoClient(fqdn, port, serverSelectionTimeoutMS=1000)

    def get_info(self):
        """
        Returns:
          dict() or None: Get information about the MongoDB server we’re connected to.
        Note:
          https://docs.mongodb.com/v3.2/reference/command/buildInfo/#dbcmd.buildInfo
        """
        if self.retries > 2:
            return None
        if hasattr(self, 'info'):
            return self.info
        try:
            info = self.conn.server_info()
            self.info = info
            return self.info
        except pymongo.errors.ConnectionFailure:
            self.retries += 1
            self.conn.close()
            self.conn = self.get_connection()
            return self.get_info()

    def get_db(self):
        """
        Authenticates to database
        Returns:
          pymongo.database.Database or False:  database(singleton) or false if authentication fails
        """
        if bool(self.database):
            return self.database
        try:
            database = self.conn[self.cred['database']]
            database.authenticate(self.cred['username'], self.cred['password'])
            self.database = database
            return self.database
        except (pymongo.errors.OperationFailure, ValueError, TypeError):
            return False

    def get_roles(self):
        data_base = self.get_db()
        return data_base.command('usersInfo', self.cred['username'])['users'][0]


class Test(object):
    def __init__(self, test, tester):
        """
        Args:
          test dict():
          tester Tester:

        Notes:
          messages should contain an array with the messages for the different results that
          the test can return, if messages is a function it should return a str[]
        """
        self.__dict__.update(test)
        self.breaks = test['breaks'] if 'breaks' in test else None
        self.tester = tester

    def run(self):
        """
        Returns:
          dict(): test result
        """
        test_result = TEST_FUNCTIONS[self.test_name](self)

        severity = test_result.severity
        custom_message = test_result.message
        message = OMITTED_MESSAGE

        if severity in [SUCCESS, ERROR]:
            message = self.messages[severity]
        elif custom_message:
            message = custom_message

        return {
            'name': self.test_name,
            'severity': self.severity,
            'title': self.title,
            'caption': self.caption,
            'message': message,
            'result': severity,
            'extra_data': custom_message
        }


def try_socket(test, forced_port=None):
    fqdn, port = test.tester.cred['nodelist'][0]
    try:
        socket.create_connection((fqdn, forced_port or port), 5)
    except socket.error:
        return TestResult(success=True)
    else:
        return TestResult(success=False)


def try_authorization(test):
    try:
        test.tester.conn.database_names()
    except (pymongo.errors.OperationFailure, pymongo.errors.ServerSelectionTimeoutError):
        return TestResult(success=True)
    else:
        return TestResult(success=False)


def try_credentials(test):
    """
    verify if the credentials are valid
    """
    return TestResult(success=bool(test.tester.get_db()))


def try_javascript(test):
    """
    Check if javascript is enabled in MongoDB
    """
    try:
        database = test.tester.get_db()
        database.test.find_one({"$where": "function() { return true;}"})
    except pymongo.errors.OperationFailure:
        return TestResult(success=True)
    else:
        return TestResult(success=False)


def try_dedicated_user(test):
    """
    Verify that the role only applies to one database
    """
    roles = test.tester.get_roles()
    user_role_dbs = set()
    for role in roles['roles']:
        user_role_dbs.add(role['db'])

    return TestResult(success=bool(len(user_role_dbs)), message=decode_to_string(user_role_dbs))


def try_scram(test):
    try:
        clean_up_connection(test)
        cred = test.tester.cred
        return TestResult(success=test.tester.conn[cred["database"]]
                          .authenticate(cred["username"],
                                        cred["password"],
                                        source=cred["database"],
                                        mechanism='SCRAM-SHA-1'))
    except (pymongo.errors.OperationFailure, ValueError, TypeError):
        return TestResult(success=False)


def clean_up_connection(test):
    test.tester.conn.close()
    del test.tester.conn
    test.tester.conn = test.tester.get_connection()
    test.tester.get_info()


@decorators.requires_userinfo
def version_newer_than(test):
    return TestResult(success=test.tester.info["version"] > "2.4",
                      message=str(test.tester.info["version"]))


@decorators.requires_userinfo
def version_exposed(test):
    return TestResult(success="version" not in test.tester.info)


TEST_FUNCTIONS = {
    "1": lambda test: TestResult(success=not (test.tester.cred['nodelist'][0][1] == 27017
                                              and bool(test.tester.info))),
    "2": try_socket,
    "3": lambda test: TestResult(success=try_socket(test, 28017)),
    "4": version_exposed,
    "5": version_newer_than,
    "tls_available": tls_available,
    "tls_enabled": tls_enabled,
    "tls_valid": tls_valid,
    "7": try_authorization,
    "8": lambda test: TestResult(success=bool(test.tester.get_db())),
    "9": try_javascript,
    "10": try_roles,
    "11": try_dedicated_user,
    "12": try_scram,
    "13": alerts_dec012015,
    "14": alerts_mar272015,
    "15": alerts_mar252015,
    "16": alerts_feb252015,
    "17": alerts_jun172014,
    "18": alerts_may052014,
    "19": alerts_jun202013,
    "20": alerts_jun052013,
    "21": alerts_mar062014,
    "22": alerts_oct012013,
    "23": alerts_aug152013
}
