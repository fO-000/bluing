#!/usr/bin/env python3

r'''bluescan v0.0.3

Usage:
    bluescan (-h | --help)
    bluescan (-v | --version)
    bluescan [-i <hcix>] -m br [--inquiry-len=<n>] [--async]
    bluescan [-i <hcix>] -m le [--timeout=<sec>] [--le-scan-type=<type>] [--sort=<key>]

Options:
    -h, --help               Display this help
    -v, --version            Show the version
    -i <hcix>                HCI device for scan [default: hci0]
    -m <mode>                Scan mode, BR or LE
    --inquiry-len=<n>        Inquiry_Length parameter of HCI_Inquiry command [default: 8]
    --timeout=<sec>          Duration of LE scan [default: 10]
    --le-scan-type=<type>    Active or passive scan for LE scan [default: active]
    --sort=<key>             Sort the discovered devices by key, only support RSSI now [default: rssi]
    --async                  Asynchronous scan for BR scan
'''

import re

from docopt import docopt


def parse_cmdline() -> dict:
    args = docopt(__doc__, version='v0.0.3', options_first=True)
    #print("[Debug] args =", args)

    args['-m'] = args['-m'].lower()
    args['--inquiry-len'] = int(args['--inquiry-len'])
    args['--timeout'] = int(args['--timeout'])
    args['--le-scan-type'] = args['--le-scan-type'].lower()
    args['--sort'] = args['--sort'].lower()

    # 从 "hcixxxx" 中提取 HCI devive 的编号
    regexp = "[0-9]+"
    hci_num = re.findall(regexp, args['-i'])
    if len(hci_num) != 1:
        raise ValueError("[ValueError] The BlueScanner constructor's iface argument contains more than one HCI device number.")
    else:
        args['-i'] = int(hci_num[-1])

    return args


if __name__ == "__main__":
    pass
