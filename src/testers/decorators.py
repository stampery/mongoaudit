def requires_userinfo(func):
    """
    If userinfo is required and not available then skip the test
    """
    def userinfo_available(test):
        return func(test) if test.tester.info else 3
    return userinfo_available


def return_version_on_fail(func):
    """
    If the result from alert is false we return also the mongo version
    """
    @requires_userinfo
    def get_data(test):
        return func(test) or [False, test.tester.info["version"]]
    return get_data


