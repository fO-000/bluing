#!/usr/bin/env python3

r'''bluescan v0.0.4

Usage:
    bluescan (-h | --help)
    bluescan (-v | --version)
    bluescan [-i <hcix>] -m br [--inquiry-len=<n>] [--async]
    bluescan [-i <hcix>] -m le [--timeout=<sec>] [--le-scan-type=<type>] [--sort=<key>]
    bluescan [-i <hcix>] -m sdp BD_ADDR
    bluescan [-i <hcix>] -m gatt --addr-type=<type> BD_ADDR

Arguments:
    BD_ADDR    Target Bluetooth device address

Options:
    -h, --help               Display this help
    -v, --version            Show the version
    -i <hcix>                HCI device for scan [default: hci0]
    -m <mode>                Scan mode, support BR, LE, SDP and GATT
    --inquiry-len=<n>        Inquiry_Length parameter of HCI_Inquiry command [default: 8]
    --timeout=<sec>          Duration of LE scan [default: 10]
    --le-scan-type=<type>    Active or passive scan for LE scan [default: active]
    --sort=<key>             Sort the discovered devices by key, only support RSSI now [default: rssi]
    --async                  Asynchronous scan for BR scan
    --addr-type=<type>       Public or random
'''

from bluescan.helper import hcix2i
from bluescan.helper import valid_bdaddr

from docopt import docopt


def parse_cmdline() -> dict:
    args = docopt(__doc__, version='v0.0.4', options_first=True)
    #print("[Debug] args =", args)

    args['-m'] = args['-m'].lower()
    args['--inquiry-len'] = int(args['--inquiry-len'])
    args['--timeout'] = int(args['--timeout'])
    args['--le-scan-type'] = args['--le-scan-type'].lower()
    args['--sort'] = args['--sort'].lower()

    try:
        if args['-m'] == 'gatt' or args['-m'] == 'sdp':
            if args['BD_ADDR'] is None:
                raise ValueError('[ERROR] Need BD_ADDR')
            else:
                args['BD_ADDR'] = args['BD_ADDR'].lower()
                if not valid_bdaddr(args['BD_ADDR']):
                    raise ValueError(
                        '[ERROR] Invalid BD_ADDR: ' + args['BD_ADDR']
                    )

        if args['-m'] == 'gatt':
            if args['--addr-type'] != 'public' and \
               args['--addr-type'] != 'random':
                raise ValueError(
                    '[ERROR] Invalid --addr-type, must be public or random'
                )
            args['--addr-type'] = args['--addr-type'].lower()
    except ValueError as e:
        print(e)
        exit(1)

    args['-i'] = hcix2i(args['-i'])

    return args


if __name__ == "__main__":
    pass
