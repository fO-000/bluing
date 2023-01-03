#!/usr/bin/env python

PKG_NAME = 'br'


from xpycommon.log import INFO, DEBUG

from .. import LOG_LEVEL as BLUING_LOG_LEVEL

LOG_LEVEL = BLUING_LOG_LEVEL
# LOG_LEVEL = DEBUG


from .__main__ import main

__all__ = ['main']
