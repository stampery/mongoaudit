# -*- coding: utf-8 -*-

class Tester(object):

  def __init__(self, cred, tests):
    self.cred = cred
    self.tests = tests

  def run(self, each, end):
    for test in self.tests:
      res = test.run(self.cred)
      each(res)
      if test.breaks is not None and res.result is test.breaks:
        break
    end(self)


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

  def run(self, cred):
    """
    Args:
      cred (dict(str:str)): parsed MongoDB URI
    """
    self.cred = cred
    self.result = self.fn(self)
    return self

import socket

def try_address(test):
  fqdn, _port = test.cred['nodelist'][0]
  try:
    socket.gethostbyname_ex(fqdn)
  except socket.gaierror:
    return False
  else:
    return True

def try_socket(test, forced_port=None):
  fqdn, port = test.cred['nodelist'][0]
  try:
    socket.create_connection((fqdn, forced_port or port), 5)
  except:
    return True
  else:
    return False

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
    lambda test: test.cred is not 27017,
    2,
    'MongoDB listens on a port different to default one',
    'Using the default MongoDB port makes it too easy for potential attackers to locate and target your server.',
    'Your server is listening in a non-obvious port. Well done.',
    'Your server is listening on default port 27017. Please read this guide on how to change the listening port.'
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
    breaks=True
  )
]

# basic_tester = Tester({'nodelist': []}, tests)
# def each(test):
#   print '[' + ['H', 'M', 'L'][test.severity] + '] ' + test.title + ':\n\t' + ['✘', '✔'][test.result] + ' ' + [test.no, test.yes][test.result]

# def end(res):
#   count = lambda acc, test: acc+1 if test.result is not None else acc
#   print 'Finished running ' + str(reduce(count, res.tests, 0)) + ' tests'

# basic_tester.run(each, end)
