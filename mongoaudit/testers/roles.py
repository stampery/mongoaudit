import pymongo
from . import TestResult, WARNING
from .utils import decode_to_string
from functools import reduce


def valid_role(role):
    """
    Args:
      role (str): name of a role
    Returns:
      Bool: True if the role is not administrative
    """
    return role not in [
        'userAdminAnyDatabase',
        'dbAdminAnyDatabase'
        'dbAdmin',
        'dbOwner',
        'userAdmin',
        'clusterAdmin',
        'root']


def result_default_value():
    """
    Returns:
      dict(set()): returns an empty dictionary that contains 3 empty
      sets where valid, invalid and custom roles are stored
    """
    return {'invalid': set([]), 'valid': set([]), 'custom': set([])}


def combine_result(value_1, value_2):
    """
    Args:
      value_1 (dict(set())): result_default_value
      value_2 (dict(set())): result_default_value
    Returns:
      dict(set()): the union of 2 default values
    """
    return {'invalid': value_1['invalid'].union(value_2['invalid']),
            'valid': value_1['valid'].union(value_2['valid']),
            'custom': value_1['custom'].union(value_2['custom'])}


def basic_validation(roles):
    """
    Basic validation in case validate role fails due to lack of permissions
    Returns:
      result_default_value
    """
    validated = result_default_value()
    for role in roles['roles']:
        if valid_role(role['role']):
            validated['valid'].add(role['role'])
        else:
            validated['invalid'].add(role['role'])
    return validated


def get_roles(role, key, database):
    return validate_role(role[key], database) if key in role else result_default_value()


def get_builtin_role(role, database):
    result = result_default_value()
    is_valid_role = valid_role(role['role'])
    if is_valid_role and role['isBuiltin']:
        result['valid'].add(role['role'])
    elif is_valid_role:
        result['custom'].add(role['role'])
    else:
        result['invalid'].add(role['role'])
    inherited = get_roles(role, 'inherited', database)
    other_roles = get_roles(role, 'roles', database)
    return combine_result(result, combine_result(inherited, other_roles))


def validate_role_dict(role, database):
    if 'role' in role:
        return get_builtin_role(role, database) if 'isBuiltin' in role else \
            validate_role(database.command('rolesInfo', role)['roles'], database)
    if 'roles' in role and bool(role['roles']):
        return validate_role(role['roles'], database)
    else:
        raise Exception('Non exhaustive type case')


def validate_role(role, database):
    """
    Recursively process the different roles that a role implements or inherits
    Args:
      role (list or dict): value returned by database.command 'usersInfo' or 'rolesInfo'
    """
    if isinstance(role, list):
        return reduce(lambda x, y: combine_result(x, y), [validate_role(r, database) for r in role]) \
            if bool(role) else result_default_value()
    elif isinstance(role, dict):
        return validate_role_dict(role, database)
    else:
        raise Exception('Non exhaustive type case')


def get_message(validated, state, text1, text2):
    return text1 + decode_to_string(validated[state]) + text2


def validation_result(validated):
    if bool(validated['invalid']):
        # if the profile is invalid
        return TestResult(success=False, message=decode_to_string(validated['invalid']))
    elif bool(validated['custom']):
        # if the profile has custom permissions
        message = get_message(validated, 'valid', 'Your user\'s role set ',
                              ' seems to be ok, but we couldn\'t do an exhaustive check.')
        return TestResult(success=True, severity=WARNING, message=message)
    # if everything seems to be ok
    return TestResult(success=True, message=decode_to_string(validated['valid']))


def try_roles(test):
    """
    Verify that the user roles are not administrative
    Returns:
      [bool or 2 , str ]: True Valid role, False invalid role, 2 custome role ,
    """

    database = test.tester.get_db()
    roles = test.tester.get_roles()

    try:
        validated = validate_role(roles, database)
    except pymongo.errors.OperationFailure:
        # if the users doesn't have permission to run the command 'rolesInfo'
        validated = basic_validation(roles)
        if bool(validated['valid']):
            message = get_message(validated, 'valid', 'You user permission ',
                                  ' didn\'t allow us to do an exhaustive check')
            return TestResult(success=True, severity=WARNING, message=message)

    return validation_result(validated)
