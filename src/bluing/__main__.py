#!/usr/bin/env python

import os
import sys
from shutil import copy
from subprocess import STDOUT, check_output
from pathlib import Path

from xpycommon.log import Logger
from xpycommon.ui import red, blue
from xpycommon.bluetooth import spoof_bd_addr

from bthci import HCI

from . import LOG_LEVEL, MICRO_BIT_FIRMWARE_PATH
from .ui import parse_cmdline
from .br import main as br_main
from .le import main as le_main
from .plugin import main as plugin_main
from .android import main as android_main


logger = Logger(__name__, LOG_LEVEL)
cmd_to_main = {
    'br': br_main,
    'le': le_main,
    'plugin': plugin_main,
    'android': android_main
}


def clean(iface: str, raddr: str):
    hci = HCI(iface)
    laddr = hci.bd_addr
    hci.close()
    
    raddr = raddr.upper()

    output = check_output(
        ' '.join(['sudo', 'systemctl', 'stop', 'bluetooth.service']), 
        stderr=STDOUT, timeout=60, shell=True)

    output = check_output(
        ' '.join(['sudo', 'rm', '-rf', '/var/lib/bluetooth/' + \
                  laddr + '/' + raddr]), 
        stderr=STDOUT, timeout=60, shell=True)
    if output != b'':
        logger.info(output.decode())

    output = check_output(
        ' '.join(['sudo', 'rm', '-rf', '/var/lib/bluetooth/' + \
                  laddr + '/' + 'cache' + '/' + raddr]), 
        stderr=STDOUT, timeout=60, shell=True)
    if output != b'':
        logger.info(output.decode())

    output = check_output(
        ' '.join(['sudo', 'systemctl', 'start', 'bluetooth.service']), 
        stderr=STDOUT, timeout=60, shell=True)


def flash_micro_bit():
    user_name = os.environ['USER']
    
    micro_bit_folders = [
        Path('/media/{}/MICROBIT'.format(user_name)),
        Path('/media/{}/MICROBIT1'.format(user_name)),
        Path('/media/{}/MICROBIT2'.format(user_name))]
    
    micro_bit_count = 0
    
    for micro_bit_folder in micro_bit_folders:
        if micro_bit_folder.is_dir():
            copy(MICRO_BIT_FIRMWARE_PATH, micro_bit_folder)
            micro_bit_count += 1
            
    if micro_bit_count > 0:
        logger.info("The firmware has been downloaded to {} micro:bit(s)".format(
            blue(str(micro_bit_count))))
    elif micro_bit_count == 0:
        logger.error("Micro:bit not found")
    else:
        raise RuntimeError("Found {} micro:bit(s)".format(micro_bit_count))


def main(argv: list[str] = sys.argv):
    args = parse_cmdline(argv[1:])
    logger.debug("parse_cmdline() returned\n"
                 "    args:", args)

    try:
        if args['<command>'] is None:
            if args['--clean']:
                clean(args['-i'], args['BD_ADDR'])
            elif args['--spoof-bd-addr']:
                spoof_bd_addr(args['BD_ADDR'], args['-i'])
            elif args['--flash-micro-bit']:
                flash_micro_bit()
            else:
                raise ValueError("Invalid option(s)")
        else:
            cmd = args['<command>']
            argv = [cmd] + args['<args>']

            try:
                cmd_to_main[cmd](argv)
            except KeyError as e:
                raise ValueError("Invalid command: " + red(args['<command>']))
    except Exception as e:
        logger.error("{}: \"{}\"".format(e.__class__.__name__, e))
        sys.exit(1)


if __name__ == '__main__':
    main()
