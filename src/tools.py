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
    except (socket.gaierror, UnicodeEncodeError):
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
    valid = re.compile(r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$")
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
    except (uri_parser.InvalidURI, ValueError, uri_parser.ConfigurationError):
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
    try:
        with open(os.path.join(base_path, 'rsc/' + path)) as json_data:
            return json.load(json_data)
    except ValueError:
        sys.exit("Failed to load tests.json")


def get_date():
    import time
    import calendar
    local = time.localtime(time.time())
    nth = ["st", "nd", "rd", None][min(3, local.tm_mday % 10 - 1)] or 'th'
    return "%s %d%s %d @ %02d:%02d" % (
        calendar.month_abbr[local.tm_mon], local.tm_mday,
        nth, local.tm_year, local.tm_hour, local.tm_min)


def check_version(version):
    # if application is binary then check for latest version
    if getattr(sys, 'frozen', False):
        try:
            url = "https://api.github.com/repos/stampery/mongoaudit/releases/latest"
            req = urllib2.urlopen(url)
            releases = json.loads(req.read())
            latest = releases["tag_name"]
            if version < latest:
                print("mongoaudit version " + version)
                print("There's a new version " + latest)
                _upgrade(releases)

        except (urllib2.HTTPError, urllib2.URLError):
            print("Couldn't check for upgrades")
        except os.error:
            print("Couldn't write mongoaudit binary")


def _check_md5(file_path, md5):
    import hashlib
    with open(file_path) as mongoaudit_bin:
        binary_md5 = hashlib.md5(mongoaudit_bin.read()).hexdigest()
    return binary_md5 == md5


def _clean_upgrade(binary_ok, binary_path, path, temp_path):
    if binary_ok:
        import stat
        # save the permissions from the current binary
        old_stat = os.stat(binary_path)
        # rename the current binary in order to replace it with the latest
        os.rename(binary_path, path + "/old")
        os.rename(temp_path, binary_path)
        # set the same permissions that had the previous binary
        os.chmod(binary_path, old_stat.st_mode | stat.S_IEXEC)
        # delete the old binary
        os.remove(path + "/old")
        print("mongoaudit updated, restarting...")
        os.execl(binary_path, binary_path, *sys.argv)
    else:
        os.remove(temp_path)
        print("couldn't download the latest binary")


def _download_binary(release, temp_path):
    req = urllib2.urlopen(release["binary"])
    binary_ok = False
    attempts = 0
    while not binary_ok and attempts < 3:
        with open(temp_path, "wb+") as mongoaudit_bin:
            mongoaudit_bin.write(req.read())
        # verify integrity of downloaded file
        print("Verifing mongoaudit integrity")
        if _check_md5(temp_path, release["md5"]):
            binary_ok = True
            print("Integrity check passed")
        attempts += 1
    return binary_ok


def _upgrade(releases):
    release = _get_release_link(releases["assets"])
    if release:
        print("Upgrading to latest version")
        binary_path = sys.executable
        path = os.path.dirname(binary_path)
        temp_path = path + "/temp"
        binary_ok = _download_binary(release, temp_path)
        _clean_upgrade(binary_ok, binary_path, path, temp_path)
    else:
        print("There's no binary for this platform")


def _get_md5(link, uname):
    md5 = urllib2.urlopen(link).read().split("\n")
    for line in md5:
        if uname in line:
            return line.split()[0]
    return None


def _get_release_link(assets):
    uname = get_platform()
    release = {}
    for asset in assets:
        download_url = asset["browser_download_url"]
        release_platform = download_url.rsplit('-', 1)[1]
        if release_platform == uname:
            release["binary"] = download_url
        elif release_platform == "checksums.txt":
            release["md5"] = _get_md5(download_url, uname)
        if len(release) == 2:
            return release
    return None


def get_platform():
    import platform
    platform_system = platform.system().lower()
    return "macosx" if platform_system == "darwin" else platform_system + "_" + platform.machine()


def in_range(num, minimum, maximum):
    return minimum <= num <= maximum
