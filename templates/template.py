def myfunction(arg1, arg2, kwarg='kword.'):
    """    
    Brief info goes here

    More detailed description here. Able reference a function such as main(). This is an example of how a Pythonic human-readable docstring can
    get parsed by doxypypy and marked up with Doxygen commands as a regular input filter to Doxygen. 
    
    \author insert author name
    \date insert date here
    \version version #
    \bug list any bugs here

    Args:
        arg1 (str):   argument 1.
        arg2 (str):   argument 2.

    Kwargs:
        kwarg:  keyword argument.

    Returns:
        return: (Boolean) value.

    Raises:
        ZeroDivisionError, AssertionError, & ValueError.

    Tags:
    Concord, Valero

    Examples:
        >>> myfunction(2, 3)
        '5 - 0, whatever.'
        >>> myfunction(5, 0, 'oops.')
        Traceback (most recent call last):
            ...
        ZeroDivisionError: integer division or modulo by zero
        >>> myfunction(4, 1, 'got it.')
        '5 - 4, got it.'
        >>> myfunction(23.5, 23, 'oh well.')
        Traceback (most recent call last):
            ...
        AssertionError
        >>> myfunction(5, 50, 'too big.')
        Traceback (most recent call last):
            ...
        ValueError
    """
    assert isinstance(arg1, int)
    if arg2 > 23:
        raise ValueError
    return '{0} - {1}, {2}'.format(arg1 + arg2, arg1 / arg2, kwarg)

def main(one,two):
    """
    Here is a description.
    
    Longer description
    
    Args:
    one (int):   argument 1.
    two (int):   argument 2.
    
    Examples:
        >>> myfunction(2, 3)
        '5 - 0, whatever.'
        >>> myfunction(5, 0, 'oops.')
        Traceback (most recent call last):
    """
    pass

    #docstring 