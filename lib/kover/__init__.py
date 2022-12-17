# Simple Kodi Version API proxy
# License: MIT


from collections import namedtuple
from typing import Tuple

import xbmc
# traversal modules (ready to monkey-pathing)
import xbmcvfs      # noqa: F401
import xbmcaddon    # noqa: F401
import xbmcdrm      # noqa: F401
import xbmcgui      # noqa: F401
import xbmcplugin   # noqa: F401


#: Kodi Version tuple type.
version_info_type = namedtuple('version_info_type', 'major minor build')
version_info_type.__new__.__defaults__ = 2*(0,)


def get_kodi_version_info() -> Tuple[int]:
    """Return major kodi version as int."""
    default = '20'
    ver = xbmc.getInfoLabel('System.BuildVersion') or default
    ver = ver.partition(' ')[0].split('.', 3)[:3]
    return version_info_type(*(int(v.partition('-')[0]) for v in ver))


#: Kodi Version tuple (always 3 elements)
#: See: `version_info_type`
version_info: Tuple[int] = get_kodi_version_info()

# Major version of Kodi
version: int

if version_info < (18, 9, 701):
    version = version_info.major
elif version_info < (19, 90):
    version = 19
else:
    version = version_info.major + (version_info.minor >= 90)

# Major version of Kodi
K: int = version
#: True if Kodi 18
K18: bool = (version == 18)
#: True if Kodi 19
K19: bool = (version == 19)
#: True if Kodi 20
K20: bool = (version == 20)
#: True if Kodi 21
K21: bool = (version == 21)


if version < 20:
    from .k19 import *    # noqa: F403, F401
else:
    from .k20 import *    # noqa: F403, F401


def patch():
    """
    Monkey patching.
    """
    # Patch proper version: .k19._patch` or `.k20._patch`.
    _patch()  # noqa: F405
