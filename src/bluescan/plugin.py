#!/usr/bin/env python

import subprocess
from subprocess import CalledProcessError
from importlib.metadata import metadata, version

import pkg_resources
from xpycommon.log import Logger
from xpycommon.plugin import Plugin, PluginError, PluginInstallError, PluginUninstallError, \
                             PluginOptionError, PluginRuntimeError, PluginPrepareError, \
                             PluginRunError, PluginCleanError

from .ui import LOG_LEVEL


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
    """exec_plugin() may raise this exception"""


class BluescanPlugin(Plugin):
    MAGIC_CLASSIFIER = 'Framework :: Bluescan :: Plugin'


def list_plugins():
    for dist in pkg_resources.working_set:
        pkg_name = dist.key
        try:
            if BluescanPlugin.MAGIC_CLASSIFIER in str(metadata(pkg_name)):
                logger.debug("BluescanPlugin.MAGIC_CLASSIFIER: {}".format(BluescanPlugin.MAGIC_CLASSIFIER))
                logger.debug("str(metadata(pkg_name): {}".format(str(metadata(pkg_name))))
                print(pkg_name.replace('-', '_'), version(pkg_name))
        except:
            pass

        # if 'meta' in str(metadata(pkg_name)):
        #     version(pkg_name)

        #     metadata(pkg_name)
        #     print(pkg_name)

        # try:
        #     dist.get_metadata('METADATA'))
        # except FileNotFoundError:
        #     pass
        
        # print(distri.key)


def install_plugin(whl_path: str):
    # ps = subprocess.Popen(('pip', 'install', '--force-reinstalls', whl_path, '2>2&1'), stdout=subprocess.PIPE, shell=True)
    # subprocess.check_output('grep -v "pip as the \'root\'"'.format(whl_path), shell=True)

    # 下面安装 plugin 的方法无法检测出，pip 的安装错误。因为在 check_output 中携带管道时，
    # 当管道成功时不会包抛出异常。
    # subprocess.check_output('pip install --force-reinstall --no-deps {} 2>&1 | grep -v "pip as the \'root\'"'.format(whl_path), shell=True)

    # --force-reinstall
    #     该参数让 pip 在安装 package 时，无视 package 版本，强制重新安装它。这样做可以方
    #     便开发者在不更改版本号的情况下，调试未发布的 plugin。
    # --no-deps
    #     该参数配合 --force-reinstall 使用，即在强制重装的过程中，不重新安装依赖包。这样
    #     可以避免在重装过程中遇到 apt 安装的 python package 无法被 pip 卸载的问题。
    try:
        subprocess.check_output('sudo pip install --force-reinstall --no-deps {} 2>&1 | grep -v "pip as the \'root\'"'.format(whl_path), shell=True)
        logger.info("Installed {}".format(whl_path))
    except CalledProcessError:
        raise BluescanPluginInstallError(whl_path)


def uninstall_plugin(name: str):
    subprocess.check_output('sudo pip uninstall -y {}  2>&1 | grep -v "pip as the \'root\'"'.format(name), shell=True)
    logger.info("Uninstalled {}".format(name))


def exec_plugin(plugin_name: str):
    """
    Parameters
        name
            plugin 的名字。
            
        opts
            传给 plugin 的所有命令行选项，是一个单独的字符串。该字符串不包括 plugin 的名字本身。
            就好像 plugin 单独运行时，少了 sys.argv[0] 的 sys.argv 一样。
    """
    if ' ' in plugin_name or ';' in plugin_name or '(' in plugin_name or ')' in plugin_name or \
       '{' in plugin_name or '}' in plugin_name or ':' in plugin_name or '\'' in plugin_name or \
       '"' in plugin_name or '.' in plugin_name or len(plugin_name) > 34:
        raise ValueError("malicious name")

    # cmd = 'python -m {} {}'.format(name, opts)
    # logger.debug("{}: {}".format(blue("run_plugin()"), cmd))
    # try:
        # subprocess.run(cmd, shell=True, check=True)
    # except CalledProcessError as e:
        # logger.error("{}".format(e))
    try:
        exec("import {}".format(plugin_name))
    except ModuleNotFoundError as e:
        raise BluescanPluginNotFoundError('Plugin {} not found'.format(plugin_name))
        
    plugin__all__ = eval("{}.__all__".format(plugin_name))
    plugin_cls_name = plugin__all__[0]
        
    
    code = \
"""
import sys
from traceback import format_exception

from {} import {}


try:
    plugin = {}()
except Exception as e:
    e_info = ''.join(format_exception(*sys.exc_info()))
    logger.debug("e_info: {{}}".format(e_info))
    raise BluescanPluginError(str(e))
    
try:
    plugin.prepare()
    plugin.run()
except Exception as e:
    e_info = ''.join(format_exception(*sys.exc_info()))
    logger.debug("e_info: {{}}".format(e_info))
    logger.error("{{}}: {{}}".format(e.__class__.__name__, e))
finally:
    plugin.print_result()
    plugin.clean()
""".format(plugin_name, plugin_cls_name, plugin_cls_name)

    exec(code)
