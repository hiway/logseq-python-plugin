from box import Box, BoxList


def mkbox(arg):
    """
    Convert a dict or list to a Box.

    Args:
        arg: The dict or list to convert.

    Returns:
        The converted Box.

    Examples:
        >>> mkbox({"a": 1})
        Box({'a': 1})
        >>> mkbox([1, 2, 3])
        [1, 2, 3]
        >>> mkbox([{"a": 1}, {"b": 2}])
        [Box({'a': 1}), Box({'b': 2})]
        >>> mkbox("a string")
        'a string'
    """
    if isinstance(arg, dict):
        return Box(arg)
    elif isinstance(arg, list):
        return BoxList(arg)
    else:
        return arg
