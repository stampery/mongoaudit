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
        self.tests = tests
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
                    'severity': x.severity,
                    'title': x.title,
                    'caption': x.caption,
                    'message': 'This test was omitted',
                    'result': 3},
                self.tests[len(result) : len(self.tests)])

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

    def __init__(self, fn, severity, title, caption, message, breaks=None):
        """
        Args:
          fn ():
          severity (str):
          title (str):
          caption (str):
          message (str[] or function): messages to display when the test is completed
          breaks (bool): True if the test suite should stop False otherwise

        Notes:
          message should contain an array with the messages for the different results that the test can return
          if message is a function it should return a str[]
        """
        self.fn, self.severity, self.title, self.caption, self.message, self.breaks = fn, severity, title, caption, message, breaks

    def run(self, tester):
        """
        Args:
          cred (dict(str:str)): parsed MongoDB URI
        Returns:
          tuple(int, str): test result value and message
        """
        self.tester = tester
        result = self.fn(self)
        message = self.message
        value = result[0] if isinstance(result, list) else result
        # if the message is a function then the test result must be of the type [int or bool, str]
        # where result[0] must be a boolean or an int  with the value 0 for false, 1 true or 2 for custom
        # result[1] must be a string with the data to display in the message
        if callable(message):
            message = message(result[1])
        message = message[value]

        return {'severity': self.severity, 'title': self.title, 'caption':
                self.caption, 'message': message, 'result': value}


import socket


def try_address(test):
    fqdn, _port = test.tester.cred['nodelist'][0]
    try:
        socket.gethostbyname_ex(fqdn)
    except socket.gaierror:
        return False
    else:
        return True


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
    message = ""
    try:
        validated = validate_role(roles)
    except pymongo.errors.OperationFailure:
        # if the users doesn't have permission to run the command 'rolesInfo'
        validated = basic_validation(roles)
        if bool(validated['valid']):
            message = 'You user permissions ' + \
                decode_to_string(
                    validated['valid']) + ' didn\'t allow us to do an exhaustive check'
            return [2, message]
    if bool(validated['invalid']):
        message = decode_to_string(validated['invalid'])
    elif decode_to_string(validated['custom']):
        message = 'Your user’s roles set ' + decode_to_string(
            validated['valid']) + ' seem to be ok, but we couldn\'t do an exhaustive check.'
    else:
        message = decode_to_string(validated['valid'])
    return [
        False if bool(
            validated['invalid']) else [
            True, 2][
                bool(
                    validated['custom'])], message]


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

basic_tests = [
    Test(
        try_address,
        0,
        'Domain exists',
        'The FQDN must exist in order to perform the test.',
        ['The provided domain name does not exist.',
         'The provided domain name does exist.', ],
        breaks=False
    ),
    Test(
        lambda test: not(test.tester.cred['nodelist'][0][
                         1] == 27017 and bool(test.tester.info)),
        2,
        'MongoDB listens on a port different to default one',
        'Using the default MongoDB port makes it too easy for potential attackers to locate and target your server.',
        ['Your server is listening on default port 27017. Please read this guide on how to change the listening port.',
         'Your server is listening in a non-obvious port. Well done.', ],
    ),

    Test(
        try_socket,
        1,
        'Server only allows connecting from intended hosts / networks',
        'Best practice is to only listen to incoming connections whose originating IP belongs to the applications or systems that are intended to use the database. This protects your server from denial-of-service attacks and some other vulnerabilities that may be present on other services running on the same device. ',
        ['Your server allows connections from unauthorized hosts. Read this guide on how to block unauthorized hosts.',
         'Your server does not allow connection from unauthorized hosts. Well done.', ],
        breaks=True
    ),
    Test(
        lambda test: try_socket(test, 28017),
        0,
        'MongoDB HTTP status interface is not accessible on port 28017',
        'HTTP status interface should be disabled in production environments to prevent potential data exposure and vulnerability to attackers.',
        ['HTTP interface is enabled. Please read this guide on how to disable MongoDB HTTP status interface.',
         'HTTP interface is disabled. Well done.', ],
    ),
    Test(
        lambda test: bool(hasattr(test.tester.info, 'version')),
        0,  # TODO update number
        'MongoDB is not exposing its version number',
        'Publicly exposing the version number makes it too easy for potential attackers to immediately exploit known vulnerabilities.',
        ['MongoDB version number is exposed. This could be solved using a reverse proxy.',
            'MongoDB is hiding its version number. Well done.'],
    ),
    Test(
        lambda test: [test.tester.info['version'] >
                      "2.4", str(test.tester.info['version'])],
        0,  # TODO update number
        'MongoDB version is newer than 2.4',
        'MongoDB versions prior to 2.4 allow usage of the “db” object inside “$where” clauses in your queries. This is a huge security flaw that allows attackers to inject and run arbitrary code in your database.',
        lambda message: ['You are running MongoDB version ' + message + '. Well done.',
                         'You are running MongoDB version ' + message + '.', ],
    ),
    Test(
        lambda test: test.tester.info['openssl']['running'] != 'disabled',
        0,  # TODO update number
        'Encryption is enabled',
        'Enable TLS/SSL to encrypt communications between your Mongo client and Mongo server to avoid eavesdropping, tampering and “man in the middle” attacks.',
        ['Encryption is disabled.',
         'TLS/SSL is enabled. Well done.', ],

    ),
    Test(
        try_authorization,
        0,  # TODO update number
        'Authentication is enabled',
        'Enable access control and specify the authentication mechanism, Authentication requires that all clients and servers provide valid credentials before they can connect to the system. In clustered deployments, enable authentication for each MongoDB server.',
        ['Authentication is disabled.', 'Authentication is enabled. Well done.', ],
    ),
]

advanced_tests = [
    # these tests require credentials
    Test(
        lambda test: bool(test.tester.get_db()),
        0,  # TODO update number
        'Valid credentials',
        'To continue testing the provided credentials must be valid.',
        ['Invalid credentials',
            'Credentials are valid', ],
        breaks=False
    ),

    Test(
        try_javascript,
        0,  # TODO update number
        'Javascript is not allowed in queries',
        'Running Javascript inside queries makes MongoDB powerful but also vulnerable to injection and denial-of-service attacks. Javascript should be always disabled unless it is strictly needed by your application.',
        ['Usage of Javascript is allowed inside queries.',
         'Usage of Javascript is not allowed inside queries. Well done.', ],
    ),

    Test(
        try_roles,
        0,  # TODO update number
        'Role granted to the provided user only permits CRUD operations',
        'Your user should only be allowed to perform CRUD (create, replace, update and delete) operations. Granting database administration roles such as “dbAdmin”, “dbOwner” or “userAdmin” is a huge risk for data integrity.',
        lambda message: ['Your user’s roles set has a too high permissions profile ' + message + '. Please read this guide to learn how to create a readWrite user in MongoDB.',
                         'Your user’s roles set ' + message + ' ???. Well done.',
                         message],
    ),

    Test(
        try_dedicated_user,
        0,  # TODO update number
        'Run MongoDB with a dedicated user',
        'Run MongoDB processes with a dedicated operating system user account. Ensure that the account has permissions to access data but no unnecessary permissions.',
        lambda message: ['Your user account has permissions for ' + message + ' databases.',
                         'No unnecessary permissions are given, your user account only has permissions over ' + message + ' database. Well done.', ],
    ),
]
