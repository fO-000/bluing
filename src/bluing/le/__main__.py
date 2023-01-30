#!/usr/bin/env python

import sys
from subprocess import CalledProcessError, check_output, STDOUT
from traceback import format_exception

from xpycommon.log import Logger
from xpycommon.ui import blue

from bluepy.btle import BTLEException

from .microbit import get_microbit_devpaths
from . import LOG_LEVEL
from .ui import parse_cmdline
from .le_scan import LeScanner
from .gatt_scan import GattScanner


logger = Logger(__name__, LOG_LEVEL)


def main(argv: list[str] = sys.argv):
    args = parse_cmdline(argv[1:])
    logger.debug("parse_cmdline() returned\n"
                 "    args:", args)

    try:
        scan_result = None

        if args['--scan']:
            scan_result = LeScanner(args['-i']).scan_devs(args['--timeout'], 
                    args['--scan-type'], args['--sort'])
        elif args['--ll-feature-set']:
            LeScanner(args['-i']).read_ll_feature_set(
                args['PEER_ADDR'], args['--addr-type'], args['--timeout'])
        elif args['--pairing-feature']:
            LeScanner(args['-i']).req_pairing_feature(
                args['PEER_ADDR'], args['--addr-type'], args['--timeout'])
        elif args['--gatt']:
            scan_result = GattScanner(args['-i'], args['--io-cap']).scan(
                args['PEER_ADDR'], args['--addr-type']) 
        elif args['--sniff-adv']:
            dev_paths = get_microbit_devpaths()
            if len(dev_paths) == 0:
                raise RuntimeError("Micro:bit not found")
            LeScanner(microbit_devpaths=dev_paths).sniff_adv(args['--channel'])
        elif args['--mon-incoming-conn']:
            #hci = HCI(args['-i'])
            #     flt = hci_filter()
            #     hci_filter_set_ptype(HciPacketTypes.EVENT, flt)
            #     hci_filter_set_event(HCI_LE_Connection_Complete.evt_code, flt)
            #     hci.set_filter(flt)
                
            #     while True:
            #         raw = hci.recv()
            #         print(raw)
            raise NotImplementedError("The `--mon-incoming-conn` option is not"
                                      " yet implemented")
        else:
            raise ValueError("Invalid option(s)")

        if scan_result is not None:
            print()
            print()
            print(blue("----------------"+scan_result.type+" Scan Result"+"----------------"))
            scan_result.print()
            scan_result.store()
    except BTLEException as e:
        logger.error(str(e) + ("\nNo BLE adapter or missing sudo?" if 'le on' in str(e) else ""))
        sys.exit(1)
    except TimeoutError as e:
        logger.error("Timeout")
        if args != None and args['-i'] != None:
            try:
                output = check_output(' '.join(['hciconfig', args['-i'], 'reset']), 
                                                 stderr=STDOUT, timeout=60, shell=True)
            except CalledProcessError as e:
                logger.warning("{}: {}".format(e.__class__.__name__, e))
    except KeyboardInterrupt:
        if args != None and args['-i'] != None:
            try:
                output = check_output(' '.join(['hciconfig', args['-i'], 'reset']), 
                                                 stderr=STDOUT, timeout=60, shell=True)
            except CalledProcessError as e:
                logger.warning("{}: {}".format(e.__class__.__name__, e))
        print()
        logger.info("Canceled\n")
    except RuntimeError as e:
        logger.error("{}: \"{}\"".format(e.__class__.__name__, e))
        sys.exit(1)
    except Exception as e:
        e_info = ''.join(format_exception(*sys.exc_info()))
        logger.debug("e_info: {}".format(e_info))
        logger.error("{}: \"{}\"".format(e.__class__.__name__, e))
        sys.exit(1)
