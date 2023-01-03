#!/usr/bin/env python

PKG_NAME = 'plugin'


from xpycommon.plugin import Plugin, PluginManager, PluginError, PluginInstallError, PluginUninstallError, \
                             PluginOptionError, PluginRuntimeError, PluginPrepareError, \
                             PluginRunError, PluginCleanError
from xpycommon.log import INFO, DEBUG
                             
from .. import PKG_NAME as BLUING_PKG_NAME, LOG_LEVEL as BLUING_LOG_LEVEL


LOG_LEVEL = BLUING_LOG_LEVEL


class BluingPluginError(PluginError):
    """"""


class BluingPluginInstallError(BluingPluginError, PluginInstallError):
    """"""


class BluingPluginUninstallError(BluingPluginError, PluginUninstallError):
    """"""
    

class BluingPluginOptionError(BluingPluginError, PluginOptionError):
    """"""


class BluingPluginRuntimeError(BluingPluginError, PluginRuntimeError):
    """"""


class BluingPluginPrepareError(BluingPluginError, PluginPrepareError):
    """"""


class BluingPluginRunError(BluingPluginError, PluginRunError):
    """"""


class BluingPluginCleanError(BluingPluginError, PluginCleanError):
    """"""


class BluingPluginNotFoundError(BluingPluginError):
    """run_plugin() may raise this exception"""


class BluingPlugin(Plugin):
    """"""


class BluingPluginManager(PluginManager):
    MAGIC_CLASSIFIER = 'Framework :: BluInG :: Plugin'
    ROOT = '/opt/{}-plugins'.format(BLUING_PKG_NAME)


from .__main__ import main

__all__ = ['main']
