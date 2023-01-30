#!/usr/bin/env python

PKG_NAME = 'run'


from xpycommon.log import INFO, DEBUG

from .. import LOG_LEVEL as PARENT_LOG_LEVEL

LOG_LEVEL = PARENT_LOG_LEVEL
# LOG_LEVEL = DEBUG


from .__main__ import main

__all__ = ['main']
