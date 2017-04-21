# -*- coding: utf-8 -*-

from collections import namedtuple

ERROR = 0
SUCCESS = 1
WARNING = 2
OMITTED = 3


class TestResult(namedtuple('Status', 'success, severity, message')):
    def __new__(cls, success, severity=SUCCESS, message=None):
        if not success:
            severity = ERROR
        return super(TestResult, cls).__new__(cls, success, severity, message)
