#!/usr/bin/env python3

r'''bluescan v0.3.1

A powerful Bluetooth scanner.

Author: Sourcell Xu from DBAPP Security HatLab.

License: GPL-3.0

Usage:
    bluescan (-h | --help)
    bluescan (-v | --version)
    bluescan [-i <hcix>] -m br [--inquiry-len=<n>]
    bluescan [-i <hcix>] -m lmp BD_ADDR
    bluescan [-i <hcix>] -m sdp BD_ADDR
    bluescan [-i <hcix>] -m le [--timeout=<sec>] [--scan-type=<type>] [--sort=<key>]
    bluescan [-i <hcix>] -m le --scan-type=features --addr-type=<type> BD_ADDR
    bluescan [-i <hcix>] -m gatt [--include-descriptor] --addr-type=<type> BD_ADDR
    bluescan [-i <hcix>] -m vuln --addr-type=br BD_ADDR

Arguments:
    BD_ADDR    Target Bluetooth device address. FF:FF:FF:00:00:00 means local device.

Options:
    -h, --help                  Display this help.
    -v, --version               Show the version.
    -i <hcix>                   HCI device for scan. [default: The first HCI device]
    -m <mode>                   Scan mode, support BR, LE, LMP, SDP, GATT and vuln.
    --inquiry-len=<n>           Inquiry_Length parameter of HCI_Inquiry command. [default: 8]
    --timeout=<sec>             Duration of LE scan. [default: 10]
    --scan-type=<type>          Active, passive or features scan for LE device(s). [default: active]
    --sort=<key>                Sort the discovered devices by key, only support RSSI now. [default: rssi]
    --include-descriptor        Fetch descriptor information.
    --addr-type=<type>          Public, random or BR.
'''


import logging

from pyclui import Logger

from docopt import docopt
from .helper import valid_bdaddr


logger = Logger(__name__, logging.INFO)


def parse_cmdline() -> dict:
    args = docopt(__doc__, version='v0.3.1', options_first=True)
    #print("[Debug] args =", args)

    args['-m'] = args['-m'].lower()
    args['--inquiry-len'] = int(args['--inquiry-len'])
    args['--timeout'] = int(args['--timeout'])
    args['--scan-type'] = args['--scan-type'].lower()
    args['--sort'] = args['--sort'].lower()

    try:
        if args['-m'] == 'gatt' or args['-m'] == 'sdp':
            if args['BD_ADDR'] is None:
                raise ValueError('Need BD_ADDR')
            else:
                args['BD_ADDR'] = args['BD_ADDR'].lower()
                if not valid_bdaddr(args['BD_ADDR']):
                    raise ValueError('Invalid BD_ADDR: ' + args['BD_ADDR'])

        if args['-m'] == 'gatt':
            if args['--addr-type'] not in ('public', 'random'):
                raise ValueError('Invalid address type, must be public or random')
            args['--addr-type'] = args['--addr-type'].lower()
    except ValueError as e:
        logger.error('{}'.format(e))
        exit(1)
        
    return args


def __test():
    pass


if __name__ == "__main__":
    __test()
