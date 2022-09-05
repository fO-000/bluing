#!/usr/bin/env python3

import subprocess
from subprocess import CalledProcessError
from typing import Union
from abc import ABCMeta, abstractmethod
from importlib.metadata import metadata, version

import pkg_resources
from pyclui import Logger
from docopt import DocoptExit

from .ui import LOG_LEVEL


logger = Logger(__name__, LOG_LEVEL)


class PluginError(Exception):
    pass

class PluginInstallError(PluginError):
    pass

class PluginOptionError(PluginError):
    pass

class PluginRuntimeError(PluginError):
    pass

class PluginPrepareError(PluginError):
    pass

class PluginCleanError(PluginError):
    pass


class PluginHelpException(Exception):
    """给 plugin 传递 -h, --help 时，plugin 应该抛出该异常，表示自己只打印了帮助，并没有
    执行核心内容"""
    pass

class Plugin(metaclass=ABCMeta):
    MAGIC_CLASSIFIER = 'Framework :: Bluescan :: Plugin'
    
    @abstractmethod
    def __init__(self, argv: Union[list[str], None] = None) -> None:
        pass

    @abstractmethod
    def prepare(self):
        """如果一个 plugin 的某些初始化代码，会影响到其他 plugin 的创建，那么应该把它们写
        在 prepare() 中，而不是 __init__() 中。"""
        pass
    
    @abstractmethod
    def run(self):
        pass
    
    @abstractmethod
    def clean(self):
        pass
    
    @abstractmethod
    def print_result(self):
        pass


def list_plugins():
    for dist in pkg_resources.working_set:
        pkg_name = dist.key
        try:
            if Plugin.MAGIC_CLASSIFIER in str(metadata(pkg_name)):
                logger.debug("Plugin.MAGIC_CLASSIFIER: {}".format(Plugin.MAGIC_CLASSIFIER))
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
        subprocess.check_output('pip install --force-reinstall --no-deps {}'.format(whl_path), shell=True)
        logger.info("Installed {}".format(whl_path))
    except CalledProcessError:
        raise PluginInstallError(whl_path)


def uninstall_plugin(name: str):
    subprocess.check_output('pip uninstall -y {}  2>&1 | grep -v "pip as the \'root\'"'.format(name), shell=True)
    logger.info("Uninstalled {}".format(name))


def run_plugin(name: str, opts: str):
    """
    Parameters
        name
            Plugin 的名字。
            
        opts
            传给 plugin 的所有命令行选项，是一个单独的字符串。该字符串不包括 plugin 的名字本身。
            就好像 plugin 单独运行时，少了 sys.argv[0] 的 sys.argv 一样。
    """
    if ' ' in name or ';' in name or '(' in name or ')' in name or '{' in name or \
       '}' in name or ':' in name or '\'' in name or '"' in name or '.' in name or \
       len(name) > 34:
        raise ValueError("malicious name")
    
    # cmd = 'python -m {} {}'.format(name, opts)
    # logger.debug("{}: {}".format(blue("run_plugin()"), cmd))
    # try:
        # subprocess.run(cmd, shell=True, check=True)
    # except CalledProcessError as e:
        # logger.error("{}".format(e))
        
    exec("import {}".format(name))
    plugin__all__ = eval("{}.__all__".format(name))
    for i in plugin__all__:
        if issubclass(i, Plugin):
            PluginSubclass = i
            logger.debug("PluginSubclass: {}".format(i))
    
    try:
        logger.debug("opts: {}".format(opts))
        plugin = PluginSubclass(argv=opts)
        
        plugin.prepare()
        plugin.run()
        plugin.clean()
        
        plugin.print_result()
    except DocoptExit as e:
        # 当不给 plugin 提供任何参数时，解析 plugin 参数的 docopt() 会抛出携带帮助信息的
        # DocoptExit 异常。
        logger.debug("{}".format(type(e)))
        help_msg = str(e)
        print(help_msg)
    except PluginHelpException as e:
        # print help doc of the plugin
        # logger.debug("PluginHelpException, {}".format(type(e)))
        print(e)
    except PluginOptionError as e:
        logger.error("PluginOptionError, {}: {}".format(name, e))
    except PluginPrepareError as e:
        logger.error("PluginPrepareError, {}: {}".format(name, e))
    except PluginRuntimeError as e:
        logger.error("PluginRuntimeError, {}: {}".format(name, e))
    except PluginCleanError as e:
        logger.error("PluginCleanError, {}: {}".format(name, e))
