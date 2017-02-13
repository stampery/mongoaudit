# -*- coding: utf-8 -*-
from src.testers.decorators import requires_userinfo


@requires_userinfo
def available(test):
    """
    Check if MongoDB is compiled with OpenSSL support
    """
    return 'OpenSSLVersion' in test.tester.info \
           or 'openssl' in test.tester.info


@requires_userinfo
def enabled(test):
    """
    Check if TLS/SSL is enabled on the server side
    """
    if not available(test):
        return 3

    try:
        if 'OpenSSLVersion' in test.tester.info:
            return bool(test.tester.info['OpenSSLVersion'])
        else:
            return test.tester.info['openssl']['running'] != 'disabled'
    except KeyError:
        return False


def valid(test):
    """
    Verify if server certificate is valid
    """
    conn = test.tester.conn
    if not enabled(test):
        return 3
    with conn._socket_for_writes() as socket_info:
        cert = socket_info.sock.getpeercert()
        if not cert:
            return [2, 'Your server is presenting a self-signed certificate, which will not '
                       'protect your connections from man-in-the-middle attacks.']
        return True
