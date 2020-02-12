#!/usr/bin/env python3

from bluescan.br_scan import BRScanner
from bluescan.le_scan import LEScanner
from bluescan.gatt_scan import GATTScanner
from bluescan.sdp_scan import SDPScanner
from bluescan.stack_scan import StackScanner
from bluescan.vuln_scan import VulnScanner

from bluescan.ui import parse_cmdline
from bluepy.btle import BTLEException

import subprocess
import time


def main():
    try:
        args = parse_cmdline()

        subprocess.getoutput('hciconfig hci%d reset' % args['-i'])
        subprocess.getoutput('hciconfig hci%d noscan' % args['-i'])

        if args['-m'] == 'br':
            br_scanner = BRScanner(args['-i'])
            if args['--async']:
                br_scanner.async_scan(args['--inquiry-len'])
            else:
                br_scanner.scan(args['--inquiry-len'], sort=args['--sort'])
        elif args['-m'] == 'le':
            LEScanner(args['-i']).scan(args['--timeout'], 
                args['--le-scan-type'], args['--sort']
            )
        elif args['-m'] == 'sdp':
            SDPScanner(args['-i']).scan(args['BD_ADDR'])
        elif args['-m'] == 'gatt':
            GATTScanner(args['-i']).scan(args['BD_ADDR'], args['--addr-type'])
        elif args['-m'] == 'stack':
            StackScanner(args['-i']).scan(args['BD_ADDR'])
        elif args['-m'] == 'vuln':
            VulnScanner(args['-i']).scan(args['BD_ADDR'], args['--addr-type'])
        else:
            print("[Error] invalid scan mode")
    except (BTLEException, ValueError) as e:
        print(e)
        if 'le on' in str(e):
            print('No BLE adapter? or missing sudo ?')
    except KeyboardInterrupt:
        print("\n[i] " + args['-m'].upper() + " scan canceled\n")


if __name__ == "__main__":
    main()
