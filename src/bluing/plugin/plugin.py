#!/usr/bin/env python

from xpycommon.plugin import Plugin, PluginManager

from . import PARENT_PKG_NAME


class BluingPlugin(Plugin):
    """"""


class BluingPluginManager(PluginManager):
    MAGIC_CLASSIFIER = 'Framework :: BluInG :: Plugin'
    ROOT = '/opt/{}-plugins'.format(PARENT_PKG_NAME)
