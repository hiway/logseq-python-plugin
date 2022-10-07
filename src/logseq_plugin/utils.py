from box import Box


def mkbox(arg):
    if isinstance(arg, dict):
        return Box(arg)
    elif isinstance(arg, list):
        return [mkbox(a) for a in arg]
    else:
        return arg
