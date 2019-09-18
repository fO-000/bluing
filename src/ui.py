#!/usr/bin/env python3

r'''bluescan v0.0.1

Usage:
    bluescan (-h | --help)
    bluescan (-v | --version)
    bluescan [-i <hcix>] -m br
    bluescan [-i <hcix>] -m le [--timeout=<sec>] [--le-scan-type=<type>]

Options:
    -h, --help               Display this help.
    -v, --version            Show the version.
    -i <hcix>                HCI device. [default: hci0]
    -m <mode>                Scan mode, br or le.
    --timeout=<sec>          Duration of scan. Only valid in le scan. [default: 10]
    --le-scan-type=<type>    Active or passive scan for le scan. [default: active]
'''


from docopt import docopt


def parse_cmdline() -> dict:
    args = docopt(__doc__, version='v0.0.1', options_first=True)
    #print("[Debug] args =", args)

    args['--timeout'] = int(args['--timeout'])

    return args
