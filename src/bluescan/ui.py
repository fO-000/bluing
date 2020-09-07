#!/usr/bin/env python3

r'''bluescan v0.2.2

A powerful Bluetooth scanner.

Author: Sourcell Xu from DBAPP Security HatLab.

License: GPL-3.0

Usage:
    bluescan (-h | --help)
    bluescan (-v | --version)
    bluescan [-i <hcix>] -m br [--inquiry-len=<n>]
    bluescan [-i <hcix>] -m lmp BD_ADDR
    bluescan [-i <hcix>] -m sdp BD_ADDR
    bluescan [-i <hcix>] -m le [--timeout=<sec>] [--le-scan-type=<type>] [--sort=<key>]
    bluescan [-i <hcix>] -m gatt [--include-descriptor] --addr-type=<type> BD_ADDR
    bluescan [-i <hcix>] -m vuln --addr-type=br BD_ADDR

Arguments:
    BD_ADDR    Target Bluetooth device address. FF:FF:FF:00:00:00 means local device.

Options:
    -h, --help                  Display this help.
    -v, --version               Show the version.
    -i <hcix>                   HCI device for scan. [default: hci0]
    -m <mode>                   Scan mode, support BR, LE, LMP, SDP, GATT and vuln.
    --inquiry-len=<n>           Inquiry_Length parameter of HCI_Inquiry command. [default: 8]
    --timeout=<sec>             Duration of LE scan. [default: 10]
    --le-scan-type=<type>       Active or passive scan for LE scan. [default: active]
    --sort=<key>                Sort the discovered devices by key, only support RSSI now. [default: rssi]
    --include-descriptor        Fetch descriptor information.
    --addr-type=<type>          Public, random or BR.
'''

from pyclui import green, blue, yellow, red, \
    DEBUG, INFO, WARNING, ERROR

from docopt import docopt
from .helper import valid_bdaddr


def parse_cmdline() -> dict:
    args = docopt(__doc__, version='v0.2.2', options_first=True)
    #print("[Debug] args =", args)

    args['-m'] = args['-m'].lower()
    args['--inquiry-len'] = int(args['--inquiry-len'])
    args['--timeout'] = int(args['--timeout'])
    args['--le-scan-type'] = args['--le-scan-type'].lower()
    args['--sort'] = args['--sort'].lower()

    try:
        if args['-m'] == 'gatt' or args['-m'] == 'sdp':
            if args['BD_ADDR'] is None:
                raise ValueError(ERROR + 'Need BD_ADDR')
            else:
                args['BD_ADDR'] = args['BD_ADDR'].lower()
                if not valid_bdaddr(args['BD_ADDR']):
                    raise ValueError(
                        ERROR + ' ' + 'Invalid BD_ADDR: ' + args['BD_ADDR']
                    )

        if args['-m'] == 'gatt':
            if args['--addr-type'] not in ('public', 'random'):
                raise ValueError(
                    ERROR + ' ' + 'Invalid address type, must be public or random'
                )
            args['--addr-type'] = args['--addr-type'].lower()
    except ValueError as e:
        print(e)
        exit(1)
        
    return args


def __test():
    pass


if __name__ == "__main__":
    __test()
