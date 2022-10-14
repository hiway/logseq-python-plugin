import sys as _sys

__min__python_version__ = "3.9"
if _sys.version_info < tuple((int(x) for x in __min__python_version__.split("."))):
    raise RuntimeError("Python %s or later is required" % __min__python_version__)
del _sys
del __min__python_version__

__version__ = "0.1.0"

__all__ = ["__version__"]
