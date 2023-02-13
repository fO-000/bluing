#!/usr/bin/env python

r"""
Usage:
    bluing spoof [-h | --help]
    bluing spoof [-i <hci>] --bd-addr=<BD_ADDR>
    bluing spoof [-i <hci>] --cls-of-dev=<num>
    bluing spoof --host-name=<name>
    bluing spoof [-i <hci>] --alias=<alias>

Options:
    -h, --help             Print this help and quit
    -i <hci>               HCI device
    --bd-addr=<BD_ADDR>    Spoof with a new BD_ADDR
    --cls-of-dev=<num>     Spoof with a new Class of Device
    --host-name=<name>     Spoof with a new host name
    --alias=<alias>        Spoof with a new alias
"""


import sys
from collections import Counter

from docopt import docopt

from xpycommon.cmdline_arg_converter import CmdlineArgConverter
from xpycommon.log import Logger
from xpycommon.ui import red
from xpycommon.bluetooth import BD_ADDR, ClassOfDevice, \
    verify_host_name, verify_controller_alias

from bthci import HCI

from . import PKG_NAME, LOG_LEVEL

logger = Logger(__name__, LOG_LEVEL)


def parse_cmdline(argv: list[str] = sys.argv[1:]) -> dict:
    logger.debug("Entered parse_cmdline(argv={})".format(argv))

    args = docopt(__doc__.replace(PKG_NAME.replace('.', ' '), PKG_NAME.split('.')[-1]), 
                  argv, help=False, options_first=True)
    logger.debug("docopt() returned\n"
                 "    args:", args)

    try:
        if args['--help'] or len(argv) == 0:
            print(__doc__)
            sys.exit()

        # Not all scenarios require HCI devcies. So when the HCI device is `None`
        # (`-i` is `None`), in order to determine whether to use the default HCI 
        # device (need call `clean_up_running()`) or not need the HCI device at all,
        # we can use other options to assist the determination.
        hci_demanders = [args['--bd-addr'], args['--cls-of-dev'], args['--alias']]
        hci_demander_counter = Counter(hci_demanders)
        if hci_demander_counter[None] != len(hci_demanders):
            if args['-i'] is None:
                args['-i'] = HCI.get_default_iface()

            hci = HCI(args['-i'])
            hci.clean_up_running()
            hci.close()

        if args['--bd-addr']:
            if not BD_ADDR.verify(args['--bd-addr']):
                raise ValueError("Invalid BD_ADDR: " + red(args['BD_ADDR']))
            args['--bd-addr'] = args['--bd-addr'].upper()
            
        if args['--cls-of-dev']:
            args['--cls-of-dev'] = CmdlineArgConverter.str2int(args['--cls-of-dev'])
            if not ClassOfDevice.verify(args['--cls-of-dev']):
                raise ValueError("Invalid Class of Device: " + red(args['--cls-of-dev']))

        if args['--host-name']:
            if not verify_host_name(args['--host-name']):
                raise ValueError("Invalid host name: " + red(args['--host-name']))

        if args['--alias']:
            if not verify_controller_alias(args['--alias']):
                raise ValueError("Invalid device name: " + red(args['--cls-of-dev']))
            
    except Exception as e:
        logger.error("{}: \"{}\"".format(e.__class__.__name__, e))
        sys.exit(1)
    else:
        return args
