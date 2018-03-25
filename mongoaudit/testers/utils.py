# -*- coding: utf-8 -*-


def in_range(num, minimum, maximum):
    return minimum <= num <= maximum


def decode_to_string(data):
    """
    Decode the strings in the list/set so we can call print the strings without the 'u' in front
    Args:
      data (list(str) or set(str))
    """
    return str([x.encode('UTF8') for x in data])