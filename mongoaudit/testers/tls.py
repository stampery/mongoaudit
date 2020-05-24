# -*- coding: utf-8 -*-
import ssl

from . import TestResult, OMITTED, WARNING
from .decorators import requires_userinfo


@requires_userinfo
def available(test):
    """
    Check if MongoDB is compiled with OpenSSL support
    """
    return TestResult(success='OpenSSLVersion' in test.tester.info or 'openssl' in test.tester.info)


@requires_userinfo
def enabled(test):
    """
    Check if TLS/SSL is enabled on the server side
    """
    if not available(test).success:
        return TestResult(success=True, severity=OMITTED)

    try:
        with test.tester.conn._socket_for_writes(None) as socket_info:
            socket = socket_info.sock
            return TestResult(success=isinstance(socket, ssl.SSLSocket))
    except (KeyError, AttributeError):
        return TestResult(success=False)


def valid(test):
    """
    Verify if server certificate is valid
    """
    if not enabled(test) is True:
        return TestResult(success=True, severity=OMITTED)

    with test.tester.conn._socket_for_writes(None) as socket_info:
        cert = socket_info.sock.getpeercert()
        if not cert:
            return TestResult(success=True,
                              severity=WARNING,
                              message='Your server is presenting a self-signed certificate, which will '
                                  'not protect your connections from man-in-the-middle attacks.')
        return TestResult(success=True)
