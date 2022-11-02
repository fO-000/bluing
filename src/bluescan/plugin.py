#!/usr/bin/env python

from xpycommon.log import Logger
from xpycommon.plugin import Plugin, PluginManager, PluginError, PluginInstallError, PluginUninstallError, \
                             PluginOptionError, PluginRuntimeError, PluginPrepareError, \
                             PluginRunError, PluginCleanError

from .ui import LOG_LEVEL
from . import PKG_NAME


logger = Logger(__name__, LOG_LEVEL)


class BluescanPluginError(PluginError):
    """"""


class BluescanPluginInstallError(BluescanPluginError, PluginInstallError):
    """"""


class BluescanPluginUninstallError(BluescanPluginError, PluginUninstallError):
    """"""
    

class BluescanPluginOptionError(BluescanPluginError, PluginOptionError):
    """"""


class BluescanPluginRuntimeError(BluescanPluginError, PluginRuntimeError):
    """"""


class BluescanPluginPrepareError(BluescanPluginError, PluginPrepareError):
    """"""


class BluescanPluginRunError(BluescanPluginError, PluginRunError):
    """"""


class BluescanPluginCleanError(BluescanPluginError, PluginCleanError):
    """"""


class BluescanPluginNotFoundError(BluescanPluginError):
    """run_plugin() may raise this exception"""


class BluescanPlugin(Plugin):
    """"""


class BluescanPluginManager(PluginManager):
    MAGIC_CLASSIFIER = 'Framework :: Bluescan :: Plugin'
    ROOT = '/opt/{}-plugins'.format(PKG_NAME)
