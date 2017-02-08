# -*- coding: utf-8 -*-
import json
import os
import sys
import urllib2


def decode_to_string(data):
    """
    Decode the strings in the list/set so we can call print the strings without the 'u' in front
    Args:
      data (list(str) or set(str))
    """
    return str([x.encode('UTF8') for x in data])


def try_address(fqdn):
    """
    Check if the fqdn is valid
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


def validate_uri(uri, error_field, callback):
    """
    Args:
      uri (str): MongoDB URI
      error_field (urwid.Text): field that displays the error
      callback (function): callback to call on success
    """
    parsed = parse_mongo_uri(uri)
    if parsed and try_address(parsed['nodelist'][0][0]):
        callback(parsed)
    else:
        error_field.set_error("Invalid domain")


def validate_email(email):
    import re
    valid = re.compile(r"^[^@]+@[^@]+\.[^@]+$")
    return valid.match(email.strip())


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
    from pymongo import uri_parser
    conn = conn.split('://')[-1]
    try:
        uri = uri_parser.parse_uri("mongodb://" + conn)
    except (uri_parser.InvalidURI, ValueError):
        return None
    else:
        return uri


def send_result(email, result, title, urn):
    """
    Args:
        email (str): address to send the results
        result (obj): results to send
        title (str):
        urn (str): uniform resource name
    Returns:
        str: response from endpoint
    """
    url = 'https://mongoaud.it/results'
    headers = {'Content-type': 'application/json',
               'Accept': 'application/json'}
    values = {'email': email, 'result': result, 'title': title, 'urn': urn, 'date': get_date()}
    try:
        req = urllib2.Request(url, json.dumps(values), headers)
        response = urllib2.urlopen(req)
        return response.read()
    except (urllib2.HTTPError, urllib2.URLError) as exc:
        return "Sadly enough, we are having technical difficulties at the moment, " \
               "please try again later.\n\n%s" % str(exc)


def load_test(path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    with open(os.path.join(base_path, 'rsc/' + path)) as json_data:
        return json.load(json_data)


def get_date():
    import time
    import calendar
    local = time.localtime(time.time())
    nth = ["st", "nd", "rd", None][min(3, local.tm_mday % 10 - 1)] or 'th'
    return "%s %d%s %d @ %02d:%02d" % (
        calendar.month_abbr[local.tm_mon], local.tm_mday,
        nth, local.tm_year, local.tm_hour, local.tm_min)


def check_version(version):
    import stat
    # if application is binary then check for latest version
    if getattr(sys, 'frozen', False):
        try:
            url = "https://api.github.com/repos/stampery/mongoaudit/releases/latest"
            req = urllib2.urlopen(url)
            releases = json.loads(req.read())
            latest = releases["tag_name"]

            print("Current version " + version + " Latest " + latest)
            if version < latest:
                path = os.path.dirname(sys.executable)
                print("about to update to version " + latest)
                # save the permissions from the current binary
                old_stat = os.stat(path + "/mongoaudit")
                # rename the current binary in order to download the latest
                os.rename(path + "/mongoaudit", path + "/temp")
                req = urllib2.urlopen(releases["assets"][0]["browser_download_url"])
                with open(path + "/mongoaudit", "wb+") as mongoaudit_bin:
                    mongoaudit_bin.write(req.read())
                    # set the same permissions that had the previous binary
                    os.chmod(path + "/mongoaudit", old_stat.st_mode | stat.S_IEXEC)
                # delete the old binary
                os.remove(path + "/temp")
                print("mongoaudit updated, restarting...")
                app_path = path + "/mongoaudit"
                os.execl(app_path, app_path, *sys.argv)

        except (urllib2.HTTPError, urllib2.URLError):
            print("Client offline")
        except os.error:
            print("Couldn't write mongoaudit binary")


def in_range(num, minimum, maximum):
    return minimum <= num <= maximum


def check_terminal():
    rows = int(os.popen('stty size', 'r').read().split()[0])
    if rows < 24:
        print("Mongo audit requires a terminal with a minimum height of 24.")
        sys.exit()
