#!/usr/bin/env python

r"""
An intelligence gathering tool for hacking Bluetooth

Usage:
    bluing [-h | --help]
    bluing (-v | --version)
    bluing [-i <hci>] --clean BD_ADDR
    bluing [-i <hci>] --spoof-bd-addr BD_ADDR
    bluing --flash-micro-bit
    bluing <command> [<args>...]

Arguments:
    BD_ADDR    Bluetooth device address

Options:
    -h, --help           Print this help and quit
    -v, --version        Print version information and quit
    -i <hci>             HCI device
    --clean              Clean cached data of a remote device
    --spoof-bd-addr      Spoof the BD_ADDR of a local controller
    --flash-micro-bit    Download the dedicated firmware to micro:bit(s)

Commands:
    br        Basic Rate system, includes an optional Enhanced Data Rate (EDR) extension
    le        Low Energy system
    android   Android Bluetooth stack
    plugin    Manage plugins

Run `bluing <command> --help` for more information on a command.
"""


import sys
from collections import Counter

from docopt import docopt
from xpycommon.log import Logger
from xpycommon.ui import red
from xpycommon.bluetooth import verify_bd_addr
from bthci import HCI

from . import VERSION_STR, LOG_LEVEL


logger = Logger(__name__, LOG_LEVEL)
INDENT = ' ' * 4


def parse_cmdline(argv: list[str] = sys.argv[1:]) -> dict:
    logger.debug("Entered parse_cmdline(argv={})".format(argv))
    
    args = docopt(__doc__, argv, version=VERSION_STR, options_first=True)
    logger.debug("docopt() returned\n"
                 "    args:", args)

    try:
        if len(argv) == 0:
            print(__doc__)
            sys.exit()

        # Not all scenarios require HCI devcies. So when the HCI device is `None`
        # (`-i` is `None`), in order to determine whether to use the default HCI 
        # device (need call `clean_up_running()`) or not need the HCI device at all,
        # we can use other options to assist the determination.
        hci_demander_counter = Counter([args['--clean'], args['--spoof-bd-addr']])
        if hci_demander_counter[True] == 1:
            if args['-i'] is None:
                args['-i'] = HCI.get_default_iface()
           
            hci = HCI(args['-i'])
            hci.clean_up_running()
            hci.close()
                
        if args['BD_ADDR']:
            if not verify_bd_addr(args['BD_ADDR']):
                raise ValueError("Invalid BD_ADDR: " + red(args['BD_ADDR']))
            args['BD_ADDR'] = args['BD_ADDR'].upper()
    except Exception as e:
        logger.error("{}: \"{}\"".format(e.__class__.__name__, e))
        sys.exit(1)
    else:
        return args
