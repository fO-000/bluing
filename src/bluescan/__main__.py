#!/usr/bin/env python3

import os
import sys
import time
import subprocess
from pathlib import PosixPath

from bluepy.btle import BTLEException
from bluetooth.btcommon import BluetoothError

from bluescan.br_scan import BRScanner
from bluescan.le_scan import LEScanner
from bluescan.gatt_scan import GATTScanner
from bluescan.sdp_scan import SDPScanner
from bluescan.stack_scan import StackScanner
from bluescan.vuln_scan import VulnScanner

from bluescan.ui import parse_cmdline
from bluescan.ui import WARNING
from bluescan.ui import ERROR
from bluescan.ui import INFO
from bluescan.helper import find_rfkill_devid

from bluescan.hci import hcix2devid
from bluescan.hci import hci_reset
from bluescan.hci import hci_inquiry_cancel
from bluescan.hci import hci_exit_periodic_inquiry_mode
from bluescan.hci import hci_write_scan_enable
from bluescan.hci import hci_write_inquiry_mode
from bluescan.hci import hci_set_event_filter
from bluescan.hci import hci_le_set_advertising_enable
from bluescan.hci import hci_le_set_scan_enable
from bluescan.hci import hci_read_bd_addr


def init(iface='hci0'):
    exitcode, output = subprocess.getstatusoutput(
        'rfkill unblock %d' % find_rfkill_devid(iface))
    if exitcode != 0:
        print('[\x1B[1;31mERROR\x1B[0m] rfkill: ', output)
        sys.exit(exitcode)

    #hci_reset(iface)
    hci_inquiry_cancel(iface)
    hci_exit_periodic_inquiry_mode(iface)
    hci_write_scan_enable(iface) # No scan enabled
    hci_le_set_advertising_enable(iface) # disable adv

    # disable scan; enabled filter duplicates, but ignored here
    hci_le_set_scan_enable(iface, b'\x00', b'\x01')

    # Ony for inquiry result and return responses from all devices during the Inquiry process
    hci_set_event_filter(iface, b'\x01', b'\x00')
    
    # Inquiry Result with RSSI format or Extended Inquiry Result format
    hci_write_inquiry_mode(iface, b'\x02')

    # clear cache
    cache_path = PosixPath('/var/lib/bluetooth/') / hci_read_bd_addr(iface) / 'cache'
    if cache_path.exists():
        for file in cache_path.iterdir():
            os.remove(file)


def main():
    try:
        args = parse_cmdline()

        init(args['-i'])
        args['-i'] = hcix2devid(args['-i'])

        if args['-m'] == 'br':
            br_scanner = BRScanner(args['-i'])
            try:
                if args['--async']:
                    br_scanner.async_scan(args['--inquiry-len'])
                else:
                    br_scanner.scan(args['--inquiry-len'], sort=args['--sort'])
            except BluetoothError as e:
                print("[\x1B[1;31mERROR\x1B[0m]", e)
                sys.exit(1)

        elif args['-m'] == 'le':
            LEScanner(args['-i']).scan(args['--timeout'], 
                args['--le-scan-type'], args['--sort']
            )
        elif args['-m'] == 'sdp':
            SDPScanner(args['-i']).scan(args['BD_ADDR'])
        elif args['-m'] == 'gatt':
            GATTScanner(args['-i']).scan(args['BD_ADDR'], args['--addr-type'],
                args['--include-descriptor'])
        elif args['-m'] == 'stack':
            StackScanner(args['-i']).scan(args['BD_ADDR'])
        elif args['-m'] == 'vuln':
            VulnScanner(args['-i']).scan(args['BD_ADDR'], args['--addr-type'])
        else:
            print("[Error] invalid scan mode")
    except (BTLEException, ValueError) as e:
        print(e)
        if 'le on' in str(e):
            print(ERROR+'No BLE adapter? or missing sudo ?')
    except KeyboardInterrupt:
        print("\n[i] " + args['-m'].upper() + " scan canceled\n")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
