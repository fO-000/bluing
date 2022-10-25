#!/usr/bin/env python

r"""bluescan

A Bluetooth scanner for hacking.

Author: Sourcell Xu

License: GPL-3.0

Usage:
    bluescan (-h | --help)
    bluescan (-v | --version)
    bluescan [-i <hci>] --clean BD_ADDR
    bluescan [-i <hci>] -m br [--inquiry-len=<n>]
    bluescan [-i <hci>] -m br --lmp-feature BD_ADDR
    bluescan [-i <hci>] -m le [--scan-type=<type>] [--timeout=<sec>] [--sort=<key>]
    bluescan [-i <hci>] -m le [--ll-feature|--smp-feature] [--timeout=<sec>] --addr-type=<type> BD_ADDR
    bluescan -m le --adv [--channel=<num>]
    bluescan [-i <hci>] -m sdp BD_ADDR
    bluescan [-i <hci>] -m gatt [--io-capability=<name>] [--addr-type=<type>] BD_ADDR
    bluescan --list-installed-plugins
    bluescan --install-plugin=<path>
    bluescan --uninstall-plugin=<name>
    bluescan --plugin=<name> [--] [<plugin-opt>...]

Arguments:
    BD_ADDR       Target Bluetooth device address. FF:FF:FF:00:00:00 means local 
                  device.
    plugin-opt    Options for a plugin.

Options:
    -h, --help                   Display this help.
    -v, --version                Show the version.
    -i <hci>                     HCI device used for subsequent scans. [default: The default HCI device]
    -m <mode>                    Scan mode, support br, le, sdp and gatt.
    --inquiry-len=<n>            Inquiry_Length parameter of HCI_Inquiry command. [default: 8]
    --lmp-feature                Scan LMP features of the remote BR/EDR device.
    --scan-type=<type>           Scan type used for scanning LE devices, active or 
                                 passive. [default: active]
    --timeout=<sec>              Duration of the LE scanning, but may not be precise. [default: 10]
    --sort=<key>                 Sort the discovered devices by key, only support 
                                 RSSI now. [default: rssi]
    --adv                        Sniff advertising physical channel PDU. Need at 
                                 least one micro:bit.
    --ll-feature                 Scan LL features of the remote LE device.
    --smp-feature                Detect pairing features of the remote LE device.
    --channel=<num>              LE advertising physical channel, 37, 38 or 39). [default: 37,38,39]
    --addr-type=<type>           Type of the LE address, public or random.
    --io-capability=<name>       Set IO capability of the agent. Available value: DisplayOnly, DisplayYesNo, 
                                 KeyboardOnly, NoInputNoOutput, KeyboardDisplay (KeyboardOnly) [default: NoInputNoOutput]
    --clean                      Clean the cached data of a remote device.
    --list-installed-plugins     List plugins in local system
    --install-plugin=<path>      Install a plugin
    --uninstall-plugin=<name>    Uninstall a plugin
    --plugin=<name>              Execute plugin by name.
"""

import sys

from docopt import docopt
# from btgatt import service_names, charac_names, descriptor_names
from xpycommon.ui import red
from xpycommon.log import Logger
from bthci import ADDR_TYPE_PUBLIC, ADDR_TYPE_RANDOM

from xpycommon.bluetooth import verify_bd_addr

from . import VERSION_STR, LOG_LEVEL


logger = Logger(__name__, LOG_LEVEL)
INDENT = ' ' * 4


def parse_cmdline() -> dict:
    args = docopt(__doc__, version=VERSION_STR, options_first=True)
    logger.debug("docopt() returned\n"
                 "    args: {}".format(args))
    
    try:
        if args['-m'] is not None:
            args['-m'] = args['-m'].lower()
            
            if (args['-m'] == 'sdp' or args['-m'] == 'gatt') and args['BD_ADDR'] is None:
                raise ValueError("The argument BD_ADDR is {}, please provide it.".format(args['BD_ADDR']))
                
        args['--inquiry-len'] = int(args['--inquiry-len'])
        args['--timeout'] = int(args['--timeout'])
        args['--sort'] = args['--sort'].lower()

        if args['--channel'] is not None:
            args['--channel'] =  [int(n) for n in args['--channel'].split(',')]
            args['--channel'] = set(args['--channel'])
            if args['--channel'].issubset({37, 38, 39}):
                args['--channel'] = list(args['--channel'])
            else:
                raise ValueError("Invalid channel {}, ".format(args['--channel']) \
                    + "must a subset of {37, 38, 39}")

        if args['BD_ADDR'] is not None:
            args['BD_ADDR'] = args['BD_ADDR'].lower()
            if not verify_bd_addr(args['BD_ADDR']):
                raise ValueError("Invalid BD_ADDR: " + red(args['BD_ADDR']))
        
        if args['--scan-type'] is not None:
            args['--scan-type'] = args['--scan-type'].lower()
            if args['--scan-type'] not in ('active', 'passive'):
                raise ValueError("Invalid scan type %s, " % \
                    red(args['--scan-type']) + "must be active or passive.")

        if args['--addr-type'] is not None:
            args['--addr-type'] = args['--addr-type'].lower()
            if args['--addr-type'] == 'public':
                args['--addr-type'] = ADDR_TYPE_PUBLIC
            elif args['--addr-type'] == 'random':
                args['--addr-type'] = ADDR_TYPE_RANDOM
            else:
                raise ValueError("Invalid address type %s, must be public or random.".format(args['--addr-type']))
        
        if args['--io-capability'] not in ['DisplayOnly', 'DisplayYesNo', 'KeyboardOnly', 'NoInputNoOutput', 'KeyboardDisplay', 'KeyboardOnly']:
            raise ValueError("Invalid IO capability %s" % args['--io-capability'])
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)

    return args


def __test():
    pass


if __name__ == '__main__':
    __test()
