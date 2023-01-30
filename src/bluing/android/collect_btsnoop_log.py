#!/usr/bin/env python

import os
import subprocess
from subprocess import CalledProcessError, STDOUT

from xpycommon import Logger
from . import LOG_LEVEL, PKG_ROOT


logger = Logger(__name__, LOG_LEVEL)


def collect_btsnoop_log(transport_id: int | None = None, output_file: str = './btsnoop_hci.log'):
    bluetooth_manager_bug_report = '/tmp/bluetooth_manager_bug_report.txt'
    btsnooz_py = PKG_ROOT/'btsnooz.py'

    try:
        subprocess.check_output('adb {} shell dumpsys bluetooth_manager > {}'.format(
            '' if transport_id is None else '-t {}'.format(transport_id), 
            bluetooth_manager_bug_report), shell=True)
    except CalledProcessError as e:
        raise RuntimeError('adb failed')

    try:
        subprocess.check_output('python {} {} > {}'.format(btsnooz_py, bluetooth_manager_bug_report, 
                                                    output_file), stderr=STDOUT, shell=True)
    except CalledProcessError as e:
        if "No btsnooz section found in bugreport" in e.stdout.decode():
            logger.warning("No btsnooz section found in bugreport\n"
                           "Check if Android Bluetooth is turned on and HCI snoop log is enabled")
        else:
            logger.error("{}: \"{}\"".format(e.__class__.__name__, str(e)))
            raise RuntimeError('btsnooz failed')

    if os.path.exists(bluetooth_manager_bug_report):
        try:
            subprocess.check_output('rm -f {}'.format(bluetooth_manager_bug_report), shell=True)
        except CalledProcessError as e:
            logger.warning("{}: {}".format(e.__class__.__name__, str(e)))
