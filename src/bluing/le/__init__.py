#!/usr/bin/env python

PKG_NAME = 'le'


from pathlib import Path

PKG_ROOT = Path(__file__).parent
LE_DEVS_SCAN_RESULT_CACHE = PKG_ROOT/'res'/'le_devs_scan_result.cache'


from xpycommon.log import INFO, DEBUG

from .. import LOG_LEVEL as PARENT_LOG_LEVEL


LOG_LEVEL = PARENT_LOG_LEVEL
# LOG_LEVEL = DEBUG


from .__main__ import main

__all__ = ['main']
