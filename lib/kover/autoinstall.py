"""
Auto install Kodi monky-patches.

Patching is done if this module is imported

>>> from kover import autoinstall  # noqa: F401
"""

from . import patch

patch()
