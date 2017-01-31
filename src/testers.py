# -*- coding: utf-8 -*-
import pymongo
from tools import decode_to_string
import time
from functools import reduce


class Tester(object):
    """
    Tester
    Args:
      cred (dict(str: str)): credentials
      tests (Test[]): tests to run
    """

    def __init__(self, cred, tests):
        self.cred = cred
        self.tests = map(lambda t: Test(**t), tests)
        self.conn = self.get_connection()
        self.info = self.get_info()

    def run(self, each, end):
        """
        Args:
          each (): function to call before each test runs (used to update and redraw the screen)
          end (function): function to call when all the tests have finished running
        """
        result = []
        for test in self.tests:
            each(test)
            res = test.run(self)
            result.append(res)
            time.sleep(0.5)
            if test.breaks == bool(res['result']):
                break

        if len(result) < len(self.tests):
            result = result + map(
                lambda x: {
                    'name': x.name,
                    'severity': x.severity,
                    'title': x.title,
                    'caption': x.caption,
                    'message': 'This test was omitted',
                    'extra_data': None,
                    'result': 3},
                self.tests[len(result): len(self.tests)])

        self.conn.close()
        end(result)

    def get_connection(self):
        """
        Returns:
          pymongo.MongoClient: a client that uses as arguments the fqdn and the port of the credentials

        """
        fqdn, port = self.cred['nodelist'][0]
        return pymongo.MongoClient(fqdn, port, serverSelectionTimeoutMS=1)

    def get_info(self):
        """
        Returns:
          dict() or None: Get information about the MongoDB server we’re connected to.
        Note:
          https://docs.mongodb.com/v3.2/reference/command/buildInfo/#dbcmd.buildInfo
        """
        try:
            info = self.conn.server_info()
            return info
        except pymongo.errors.ConnectionFailure:
            return None

    def get_db(self):
        """
        Authenticates to database
        Returns:
          pymongo.database.Database or False: authenticates and returns the database(singleton) or false if authentication fails
        """
        if hasattr(self, 'db'):
            return self.db
        try:
            db = self.conn[self.cred['database']]
            db.authenticate(self.cred['username'], self.cred['password'])
            self.db = db
            return self.db
        except (pymongo.errors.OperationFailure, ValueError, TypeError):
            return False


class Test(object):

    def __init__(self, test_name, severity, title, caption, message, breaks=None):
        """
        Args:
          name (str): test name
          severity (str):
          title (str):
          caption (str):
          message (str[] or function): messages to display when the test is completed
          breaks (bool): True if the test suite should stop False otherwise

        Notes:
          message should contain an array with the messages for the different results that the test can return
          if message is a function it should return a str[]
        """
        self.name, self.severity, self.title, self.caption, self.message, self.breaks = test_name, severity, title, caption, message, breaks

    def run(self, tester):
        """
        Args:
          cred (dict(str:str)): parsed MongoDB URI
        Returns:
          tuple(int, str): test result value and message
        """
        self.tester = tester
        result = test_functions[self.name](self)
        message = self.message

        if isinstance(result, list):
            value = result[0]
            extra_data = result[1]
        else:
            value = result
            extra_data = None
        return {'name': self.name, 'severity': self.severity, 'title': self.title, 'caption':
                self.caption, 'message': message[value], 'result': value, 'extra_data': extra_data}


import socket


def try_socket(test, forced_port=None):
    fqdn, port = test.tester.cred['nodelist'][0]
    try:
        socket.create_connection((fqdn, forced_port or port), 5)
    except:
        return True
    else:
        return False


def try_authorization(test):
    try:
        test.tester.conn.database_names()
    except pymongo.errors.OperationFailure:
        return True
    else:
        return False


def try_credentials(test):
    """
    verify if the credentials are valid
    """
    return bool(test.tester.get_db())


def try_javascript(test):
    """
    Check if javascript is enabled in MongoDB
    """
    try:
        db = test.tester.get_db()
        db.test.find_one({"$where": "function() { return true;}"})
    except pymongo.errors.OperationFailure:
        return True
    else:
        return False


def try_roles(test):
    """
    Verify that the user roles are not administrative
    Returns:
      [bool or 2 , str ]: True Valid role, False invalid role, 2 custome role ,
    """

    def valid_role(role):
        """
        Args:
          role (str): name of a role
        Returns:
          Bool: True if the role is not administrative
        """
        return not role in [
            'userAdminAnyDatabase',
            'dbAdminAnyDatabase'
            'dbAdmin',
            'dbOwner',
            'userAdmin',
            'clusterAdmin']

    def result_default_value():
        """

        Returns:
          dict(set()): returns an empty dictionary that contains 3 empty sets where valid, invalid and custom roles are stored
        """
        return {'invalid': set([]), 'valid': set([]), 'custom': set([])}

    def combine_result(a, b):
        """
        Args:
          a (dict(set())): result_default_value
          b (dict(set())): result_default_value
        Returns:
          dict(set()): the union of 2 default values
        """
        return {
            'invalid': a['invalid'].union(
                b['invalid']), 'valid': a['valid'].union(
                b['valid']), 'custom': a['custom'].union(
                b['custom'])}

    def reduce_roles(roles):
        """
        Validate and combine a list of roles
        Args:
         roles (list(dict())): roles
        Returns:
          result_default_value: with the roles sorted by valid, invalid, custom
        """
        return reduce(
            lambda x, y: combine_result(
                x, y), map(
                lambda r: validate_role(r), roles))

    def basic_validation(role):
        """
        Basic validation in case validate role fails due to lack of permissions
        Returns:
          result_default_value
        """
        validated = result_default_value()
        for role in roles['roles']:
            if valid_role(role['role']):
                validated['valid'].add(role['role'])
            else:
                validated['invalid'].add(role['role'])
        return validated

    def validate_role(role):
        """
        Recursively process the different roles that a role implements or inherits
        Args:
          role (list or dict): value returned by db.command 'usersInfo' or 'rolesInfo'
        """
        if isinstance(role, list) and bool(role):
            return reduce_roles(role)
        elif isinstance(role, dict):
            if 'role' in role and 'isBuiltin' in role:
                result = result_default_value()
                is_valid_role = valid_role(role['role'])
                if is_valid_role and role['isBuiltin']:
                    result['valid'].add(role['role'])
                elif is_valid_role:
                    result['custom'].add(role['role'])
                else:
                    result['invalid'].add(role['role'])
                inherited = validate_role(
                    role['inheritedRoles']) if 'inheritedRoles' in role else result_default_value()
                other_roles = validate_role(
                    role['roles']) if 'roles' in role else result_default_value()
                return combine_result(
                    result, combine_result(
                        inherited, other_roles))
            if 'role' in role:
                return validate_role(db.command('rolesInfo', role)['roles'])
            if 'roles' in role and bool(role['roles']):
                return validate_role(role['roles'])
            else:
                raise Exception('Non exhaustive type case')
        elif isinstance(role, list):
            # empty list
            return result_default_value()
        else:
            raise Exception('Non exhaustive type case')

    # get the database
    db = test.tester.get_db()
    roles = db.command('usersInfo', test.tester.cred['username'])['users'][0]
    validated = {}

    def get_message(state, text1, text2):
        return text1 + decode_to_string(validated[state]) + text2

    try:
        validated = validate_role(roles)
    except pymongo.errors.OperationFailure:
        # if the users doesn't have permission to run the command 'rolesInfo'
        validated = basic_validation(roles)
        if bool(validated['valid']):
            message = get_message('valid', 'You user permission ', ' didn\'t allow us to do an exhaustive check')
            return [2, message]

    # when user has permission to run 'rolesInfo'
    if bool(validated['invalid']):
        # if the profile is invalid
        return [False, decode_to_string(validated['invalid'])]
    elif bool(validated['custom']):
        # if the profile has custom permissions
        message = get_message('valid', 'Your user\'s role set ', ' seem to be ok, but we couldn\'t do an exhaustive check.') 
        return [2, message]
    # if everything seems to be ok
    return [True, decode_to_string(validated['valid'])]


def try_dedicated_user(test):
    """
    Verify that the role only applies to one database
    """
    db = test.tester.get_db()
    roles = db.command('usersInfo', test.tester.cred['username'])['users'][0]
    user_role_dbs = set()
    for role in roles['roles']:
        user_role_dbs.add(role['db'])

    return [bool(len(user_role_dbs)), decode_to_string(user_role_dbs)]


def try_scram(test):
    try:
        conn = test.tester.get_connection()
        cred = test.tester.cred
        return conn[cred["database"]].authenticate(cred["username"], cred["password"], mechanism='SCRAM-SHA-1')
    except (pymongo.errors.OperationFailure, ValueError, TypeError):
        return False

# the following functions are for https://www.mongodb.com/alerts security related
def version_in_range(version, min, max):
    return version >= min and version <= max

def alerts_d012015(test):
    if "modules" in test.tester.info:
        enterprise = "enterprise" in test.tester.info["modules"]
        version = test.tester.info["version"]
        return not(version_in_range(version, "3.0.6", "3.0.6"))
    else:
        return True


test_functions = {
    "1": lambda test: not(test.tester.cred['nodelist'][0][1] == 27017 and bool(test.tester.info)),
    "2": try_socket,
    "3": lambda test: try_socket(test, 28017),
    "4": lambda test: not "version" in test.tester.info,
    "5": lambda test: [test.tester.info["version"] > "2.4", str(test.tester.info["version"])],
    "6": lambda test: bool(test.tester.info["OpenSSLVersion"]) if ("OpenSSLVersion" in test.tester.info) else test.tester.info["openssl"]["running"] != "disabled",
    "7": try_authorization,
    "8": lambda test: bool(test.tester.get_db()),
    "9": try_javascript,
    "10": try_roles,
    "11": try_dedicated_user,
    "12": try_scram,
    "13": alerts_d012015,

}

