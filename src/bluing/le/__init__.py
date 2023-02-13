#!/usr/bin/env python

from pathlib import Path

from xpycommon.log import INFO, DEBUG

from .. import PKG_NAME as PARENT_PKG_NAME, LOG_LEVEL as PARENT_LOG_LEVEL


PKG_NAME = '.'.join([PARENT_PKG_NAME, 'le']) 
PKG_ROOT = Path(__file__).parent
LOG_LEVEL = PARENT_LOG_LEVEL
# LOG_LEVEL = DEBUG
LE_DEVS_SCAN_RESULT_CACHE = PKG_ROOT/'res'/'le_devs_scan_result.cache'


from .__main__ import main

__all__ = ['main']
