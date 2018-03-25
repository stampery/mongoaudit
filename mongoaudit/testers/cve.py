from . import TestResult
from .decorators import return_version_on_fail
from .utils import in_range

# https://www.mongodb.com/alerts


@return_version_on_fail
def alerts_dec012015(test):
    if "modules" in test.tester.info:
        enterprise = "enterprise" in test.tester.info["modules"]
        version = test.tester.info["version"]
        return TestResult(success=not (enterprise and in_range(version, "3.0.0", "3.0.6")))
    else:
        return TestResult(success=True)


@return_version_on_fail
def alerts_mar272015(test):
    return TestResult(success=test.tester.info["version"] != "3.0.0")


@return_version_on_fail
def alerts_mar252015(test):
    version = test.tester.info["version"]
    return TestResult(success=version > "2.6.8" and version != "3.0.0")


@return_version_on_fail
def alerts_feb252015(test):
    version = test.tester.info["version"]
    return TestResult(success=version > "2.6.7" or version == "2.4.13")


@return_version_on_fail
def alerts_jun172014(test):
    version = test.tester.info["version"]
    return TestResult(success=version not in ["2.6.0", "2.6.1"])


@return_version_on_fail
def alerts_may052014(test):
    version = test.tester.info["version"]
    return TestResult(success=version != "2.6.0")


@return_version_on_fail
def alerts_jun202013(test):
    version = test.tester.info["version"]
    return TestResult(success=not in_range(version, "2.4.0", "2.4.4") and version != "2.5.1")


@return_version_on_fail
def alerts_jun052013(test):
    version = test.tester.info["version"]
    return TestResult(success=not in_range(version, "2.4.0", "2.4.4"))


@return_version_on_fail
def alerts_mar062014(test):
    version = test.tester.info["version"]
    return TestResult(success=version > "2.3.1")


@return_version_on_fail
def alerts_oct012013(test):
    version = test.tester.info["version"]
    return TestResult(success=version > "2.2.3")


@return_version_on_fail
def alerts_aug152013(test):
    version = test.tester.info["version"]
    return TestResult(success=version > "2.5.1")
