"""Tools for consistent research computing environments."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("lab-env")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = ["__version__"]
