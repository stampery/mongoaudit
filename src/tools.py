# -*- coding: utf-8 -*-
import json

def decode_to_string(data):
    """
    Decode the strings in the list/set so we can call print the strings without the 'u' in front
    Args:
      data (list(str) or set(str))
    """
    return str([x.encode('UTF8') for x in data])

def try_address(fqdn):
    """
    Check if a fqdn is valid
    Args:
        fqdn (str): fully qualified domain name
    """
    import socket
    try:
        socket.gethostbyname_ex(fqdn)
    except socket.gaierror:
        return False
    else:
        return True

def validate_uri(uri, error_field, error_message, cb):
    """
    Args:
      uri (str): MongoDB URI
      error_field (urwid.Text): field that displays the error
      error_message (str): message to display in case of error
      cb (function): callback to call on success
    """
    parsed = parse_mongo_uri(uri)
    if parsed and try_address(parsed['nodelist'][0][0]):
        cb(parsed)
    else:
        error_field.set_error("Invalid domain")


def parse_mongo_uri(conn):
    """
    Args:
      conn (str): MongoDB URI
    Returns:
      dict(str: str) or None: parsed MongoDB URI

      {
        'nodelist': <list of (host, port) tuples>,
        'username': <username> or None,
        'password': <password> or None,
        'database': <database name> or None,
        'collection': <collection name> or None,
        'options': <dict of MongoDB URI options>
      }
    """
    import re
    from pymongo import uri_parser
    conn = conn.split('://')[-1]
    try:
        uri = uri_parser.parse_uri("mongodb://" + conn)
    except Exception:
        return None
    else:
        return uri


def send_result(email, result, title, urn):
    """
    Args:
        email (str): address to send the results
        result (obj): results to send
    Returns:
        str: response from endpoint
    """
    import urllib2
    url = 'http://127.0.0.1:3000/results'
    headers = {'Content-type': 'application/json',
               'Accept': 'application/json'}
    values = {'email': email, 'result': result, 'title': title, 'urn': urn, 'date': getDate()}
    try:
        req = urllib2.Request(url, json.dumps(values), headers)
        response = urllib2.urlopen(req)
        return response.read()
    except urllib2.HTTPError as e:
        return e.msg


def load_test(path):
    with open(path) as json_data:
        return json.load(json_data)

def getDate():
    import time, calendar
    local = time.localtime(time.time())
    nth = ["st", "nd", "rd", None][min(3, local.tm_mday % 10 - 1)] or 'th'
    return "%s %d%s %d @ %d:%d" % (calendar.month_abbr[local.tm_mon], local.tm_mday, nth, local.tm_year, local.tm_hour, local.tm_min)
