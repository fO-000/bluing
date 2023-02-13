#!/usr/bin/env python

from xpycommon.log import INFO, DEBUG

from .. import PKG_NAME as PARNET_PKG_NAME, LOG_LEVEL as PARENT_LOG_LEVEL


PKG_NAME = '.'.join([PARNET_PKG_NAME, 'uninstall'])
LOG_LEVEL = PARENT_LOG_LEVEL


from .__main__ import main

__all__ = ['main']
