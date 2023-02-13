#!/usr/bin/env python

from xpycommon.plugin import PluginError, PluginInstallError, PluginUninstallError, \
    PluginOptionError, PluginRuntimeError, PluginPrepareError, \
    PluginRunError, PluginCleanError


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
