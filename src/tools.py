# -*- coding: utf-8 -*-

def validate_uri(uri, error_field, error_message, cb):
  parsed = parse_mongo_uri(uri)
  if parsed:
    cb(parsed)
  else:
    error_field.set_error("Invalid URI" )

def parse_mongo_uri(conn):
  from pymongo import uri_parser
  try:
    uri = uri_parser.parse_uri(conn)
  except Exception:
    return []
  else:
    return uri
