# -*- coding: utf-8 -*-
import pymongo
class Tester(object):

  def __init__(self, cred, tests):
    self.cred = cred
    self.tests = tests
    self.conn = self.get_connection()
    self.info = self.get_info()

  def run(self, each, end):
    for test in self.tests:
      each(test)
      res = test.run(self)
      if test.breaks == res.result:
        break
    #TODO uncomment the next line and remove the test line in order to return only the results
    # end(self.tests)
    self.conn.close()
    end(self) # delete me

  def get_connection(self):
    fqdn, port = self.cred['nodelist'][0]
    return pymongo.MongoClient(fqdn, port, serverSelectionTimeoutMS=1)

  def get_info(self):
    try:
      info = self.conn.server_info()
      return info
    except pymongo.errors.ConnectionFailure:
      return None

  def get_db(self):
    if hasattr(self, 'db'):
      return self.db
    try:
      # raise Exception("mine " + str(self.cred))
      db = self.conn[self.cred['database']]
      db.authenticate(self.cred['username'], self.cred['password'])
      self.db = db
      return self.db
    except (pymongo.errors.OperationFailure, ValueError, TypeError):
      return False


class Test(object):
  def __init__(self, fn, severity, title, caption, yes, no, breaks=None):
    """
    Args:
      fn ():
      severity (str):
      title (str):
      caption (str):
      yes ():
      no ():
      breaks ():
    """
    self.fn, self.severity, self.title, self.caption, self.yes, self.no, self.breaks = fn, severity, title, caption, yes, no, breaks
    self.result = None

  def run(self, tester):
    """
    Args:
      cred (dict(str:str)): parsed MongoDB URI
    """
    self.tester = tester
    self.result = self.fn(self)
    if self.result and callable(self.yes):
      self.yes = self.yes(self)
    elif callable(self.no):
      self.no = self.no(self)

    return self


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
  return bool(test.tester.get_db())

def try_javascript(test):
  try:
    db = test.tester.get_db()
    db.test.find_one({"$where": "function() { return true;}"})
  except pymongo.errors.OperationFailure:
    return True
  else:
    return False

def try_roles(test):
  db = test.tester.get_db()
  roles = db.command("usersInfo", test.tester.cred['username'])['users'][0]['roles']
  for role in roles:
    if role['role'] in ['userAdminAnyDatabase', 'dbAdminAnyDatabase' 'dbAdmin', 'dbOwner', 'userAdmin', 'clusterAdmin' ]:
      test.message = role['role']
      return False
  return True

tests = [
  Test(
    try_address,
    0,
    'Domain exists',
    'The FQDN must exist in order to perform the test.',
    'The provided domain name does exist.',
    'The provided domain name does not exist.',
    breaks=False
  ),
  Test(
    lambda test:  test.tester.cred['nodelist'][0][1] != 27017,
    2,
    'MongoDB listens on a port different to default one',
    'Using the default MongoDB port makes it too easy for potential attackers to locate and target your server.',
    'Your server is listening in a non-obvious port. Well done.',
    'Your server is listening on default port 27017. Please read this guide on how to change the listening port.',
    breaks=False
  ),

  Test(
    try_socket,
    1,
    'Server only allows connecting from intended hosts / networks',
    'Best practice is to only listen to incoming connections whose originating IP belongs to the applications or systems that are intended to use the database. This protects your server from denial-of-service attacks and some other vulnerabilities that may be present on other services running on the same device. ',
    'Your server does not allow connection from unauthorized hosts. Well done.',
    'Your server allows connections from unauthorized hosts. Read this guide on how to block unauthorized hosts.',
  ),
  Test(
    lambda test: try_socket(test, 28017),
    0,
    'MongoDB HTTP status interface is not accessible on port 28017',
    'HTTP status interface should be disabled in production environments to prevent potential data exposure and vulnerability to attackers.',
    'HTTP interface is disabled. Well done.',
    'HTTP interface is enabled. Please read this guide on how to disable MongoDB HTTP status interface.',
    #breaks=True # uncomment after debug
  ),
  Test(
    lambda test: test.tester.info['version'] > "2.4" ,
    0, #TODO update number
    'MongoDB version is newer than 2.4',
    'MongoDB versions prior to 2.4 allow usage of the “db” object inside “$where” clauses in your queries. This is a huge security flaw that allows attackers to inject and run arbitrary code in your database.',
    lambda test: 'You are running MongoDB version ' + str(test.tester.info['version']) + '. Well done.',
    lambda test: 'You are running MongoDB version ' + str(test.tester.info['version']) + '.',
  ),
  Test(
    lambda test: test.tester.info['openssl']['running'] != 'disabled' ,
    0, #TODO update number
    'Encryption is enabled',
    'Enable TLS/SSL to encrypt communications between your Mongo client and Mongo server to avoid eavesdropping, tampering and “man in the middle” attacks.',
    'TLS/SSL is enabled. Well done.',
    'Encryption is disabled.',

  ),
  Test(
    try_authorization,
    0, #TODO update number
    'Authentication is enabled',
    'Enable access control and specify the authentication mechanism, Authentication requires that all clients and servers provide valid credentials before they can connect to the system. In clustered deployments, enable authentication for each MongoDB server.',
    'Authentication is enabled. Well done.',
    'Authentication is disabled.',
  ),

  # next tests require credentials
  Test(
    lambda test: bool(test.tester.get_db()),
    0, #TODO update number
    'Valid credentials',
    'To continue testing the provided credentials must be valid.',
    'Credentials are valid',
    'Invalid credentials',
    breaks=False
  ),

  Test(
    try_javascript,
    0, #TODO update number
    'Javascript is not allowed in queries',
    'Running Javascript inside queries makes MongoDB powerful but also vulnerable to injection and denial-of-service attacks. Javascript should be always disabled unless it is strictly needed by your application.',
    'Usage of Javascript is not allowed inside queries. Well done.',
    'Usage of Javascript is allowed inside queries.',
  ),

  Test(
    try_roles ,
    0, #TODO update number
    'Role granted to the provided user only permits CRUD operations',
    'Your user should only be allowed to perform CRUD (create, replace, update and delete) operations. Granting database administration roles such as “dbAdmin”, “dbOwner” or “userAdmin” is a huge risk for data integrity.',
    'Your user’s only role is “readWrite”. Well done.',
    lambda test: 'Your user’s roles set has a too high permissions profile ("' + str(test.message) + '"). Please read this guide to learn how to create a readWrite user in MongoDB.',
  ),

  # Test(
  #   lambda test: ,
  #   0, #TODO update number
  #   'MongoDB is not exposing its version number',
  #   'Publicly exposing the version number makes it too easy for potential attackers to immediately exploit known vulnerabilities.',
  #   'MongoDB is hiding its version number. Well done.',
  #   'MongoDB version number is exposed. This could be solved using a reverse proxy.',
  #
  # ),
  # Test(
  #   lambda test: ,
  #   0, #TODO update number
  #   'Run MongoDB with a dedicated user',
  #   'Run MongoDB processes with a dedicated operating system user account. Ensure that the account has permissions to access data but no unnecessary permissions.',
  #   'No unnecessary permissions are given .Well done.',
  #   'Please read this guide to learn how to disable it.',
  #
  # ),
  # Test(
  #   lambda test: ,
  #   0, #TODO update number
  #   'Role based administration',
  #   'Using roles helps simplify management of access control by defining a single set of rules that apply to specific classes of entities, rather than having to define them individually for each user.',
  #   'Roles are ???.Well done.',
  #   'Please read this guide to learn how to disable it.',
  #
  # ),

  # Test(
  #   lambda test: ,
  #   0, #TODO update number
  #   '',
  #   '',
  #   '',
  #   '',
  #
  # ),

  ### implement below this line
]
