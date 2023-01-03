#!/usr/bin/env python


PKG_NAME = 'install'


from xpycommon.log import INFO, DEBUG

from .. import LOG_LEVEL as BLUING_PLUGIN_LOG_LEVEL


LOG_LEVEL = BLUING_PLUGIN_LOG_LEVEL


from .__main__ import main

__all__ = ['main']
