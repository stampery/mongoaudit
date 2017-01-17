# -*- coding: utf-8 -*-


def decode_to_string(data):
    """
    Decode the strings in the list/set so we can call print the strings without the 'u' in front
    Args:
      data (list(str) or set(str))
    """
    return str([x.encode('UTF8') for x in data])


def validate_uri(uri, error_field, error_message, cb):
    """
    Args:
      uri (str): MongoDB URI
      error_field (urwid.Text): field that displays the error
      error_message (str): message to display in case of error
      cb (function): callback to call on success
    """
    parsed = parse_mongo_uri(uri)
    if parsed:
        cb(parsed)
    else:
        error_field.set_error(error_message)


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

def send_result(email, result):
    """
    Args:
        email (str): address to send the results
        result (obj): results to send
    Returns:
        str: response from endpoint
    """
    import json
    import urllib2
    url = 'http://127.0.0.1:3000/results'
    headers={'Content-type': 'application/json', 'Accept': 'application/json'}
    values = {'email' : email, 'result' : result}
    req = urllib2.Request(url, json.dumps(values), headers)
    response = urllib2.urlopen(req)
    return response.read()

