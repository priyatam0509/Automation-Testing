import functools

# TC Exceptions
class ExitError(Exception):
    pass

class ScriptError(ExitError):
    pass

class TestError(ExitError):
    pass

# Decorators for test cases
def setup(func):
    """
    Setup decorator

    Provides an easy way to do anything that this feature script requires to do what it needs to do. 
    Specifically, use this method to configure things specific to your feature. Setting up loyalty, 
    adding a cashback fee, etc.
    """
    func._setup = True
    return func

def test(func):
    """
    Test case decorator

    Methods that are marked as test define things that need to be verified and have their results recorded. 
    Speficially, use these methods to test your feature. Make sure to validate things on the way by grabbing
    the receipt text and making sure that loyalty exists on the receipt, generating a failure via tc_fail() 
    if it does not and it should.

    *important*
    results are recorded automatically for any method decorated as test. A test entry will be started and 
    automatically marked as pass unless it is specifically marked as a fail via tc_fail().
    """
    func._test = True
    return func

def teardown(func):
    """
    Teardown decorator

    This method is meant for record keeping. Do any deconfiguration or file output (recording some value for whatever reason)
    that you may need in the future. This will be ran before the framework teardown is ran, so no loss of data will happen until
    then.
    """
    func._teardown = True
    return func

def test_func(func):
    """
    Decorator for test methods
    Defines an optional verify parameter that, if set to True, will cause tc_fail to be invoked if the decorated function returns False or None
    The parameter defaults to True
    TODO: Add parameter to allow temporary changes in logging level
    TODO: Add parameter for timeouts?
    """
    @functools.wraps(func) # Preserve func attributes like __name__ and __doc__
    def test_func_wrapper(*args, **kwargs):
        try:
            verify = kwargs['verify']
            del kwargs['verify']
        except KeyError:
            verify = True
        ret = func(*args, **kwargs)
        if verify and (ret is None or not ret):
            tc_fail(f"{func.__module__}.{func.__name__} failed.")
        return ret
    return test_func_wrapper


def tc_fail(reason, exit=False):
    """
    Used by the test case to indicate a failure to the test harness.

    Args:
        reason: (str) The reason for the failure. Specifics matter.
        exit: (bool) Set to True if this failure will cause the rest of the script to not function properly or generate incorrect results.
                     Defaulted to false which means only the individual test will stop where it's at and will continue on at the next test.
    Returns:
        None
    Throws:
        ScriptError, TestError
    Examples:
        >>> tc_fail("loyalty was not present on receipt")
        (no return type, test harness fails the test case with the reason specified and moves to the next test)
        >>> tc_fail("Loyalty did not prompt on fuel transaction", exit=True)
        (no return type, test harness fails the test case with the reason specified and exits the script,
         moving to the next script in the suite if applicable. Teardown will still happen in immediately
         before moving on to the next script)
    """
    if exit:
        raise ScriptError(reason)
    else:
        raise TestError(reason)