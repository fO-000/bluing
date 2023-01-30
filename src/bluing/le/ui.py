#!/usr/bin/env python

r"""
Usage:
    bluing le [-h | --help]
    bluing le [-i <hci>] [--scan-type=<type>] [--timeout=<sec>] [--sort=<key>] --scan
    bluing le [-i <hci>] --pairing-feature [--timeout=<sec>] [--addr-type=<type>] PEER_ADDR
    bluing le [-i <hci>] --ll-feature-set [--timeout=<sec>] [--addr-type=<type>] PEER_ADDR
    bluing le [-i <hci>] --gatt [--io-cap=<name>] [--addr-type=<type>] PEER_ADDR
    bluing le [-i <hci>] --local --gatt
    bluing le [-i <hci>] --mon-incoming-conn
    bluing le [--channel=<num>] --sniff-adv

Arguments:
    PEER_ADDR    LE Bluetooth device address

Options:
    -h, --help            Print this help and quit
    -i <hci>              HCI device
    --scan                Discover advertising devices nearby
    --scan-type=<type>    The type of scan to perform. active or passive [default: active]
    --sort=<key>          Sort the discovered devices by key, only support RSSI 
                          now [default: rssi]
    --ll-feature-set      Read LL FeatureSet of a remote LE device
    --pairing-feature     Request the pairing feature of a remote LE device
    --timeout=<sec>       Duration of the LE scanning, but may not be precise [default: 10]
    --gatt                Discover GATT Profile hierarchy of a remote LE device
    --io-cap=<name>       Set an IO Capability of the agent. Available value: 
                              DisplayOnly, DisplayYesNo, KeyboardOnly, NoInputNoOutput, 
                              KeyboardDisplay [default: NoInputNoOutput]
    --addr-type=<type>    Type of the LE address, public or random
    --sniff-adv           Sniff advertising physical channel PDU. Need at least 
                          one micro:bit
    --channel=<num>       LE advertising physical channel, 37, 38 or 39 [default: 37,38,39]
"""


import sys
from collections import Counter

from xpycommon.log import Logger
from xpycommon.ui import blue, yellow, red
from xpycommon.bluetooth import verify_bd_addr
from docopt import docopt
from bthci import ADDR_TYPE_PUBLIC, ADDR_TYPE_RANDOM, HCI

from .. import PKG_NAME as BLUING_PKG_NAME

from . import LOG_LEVEL, PKG_NAME
from .le_scan import LeScanner


logger = Logger(__name__, LOG_LEVEL)


def parse_cmdline(argv: list[str] = sys.argv[1:]) -> dict:
    logger.debug("Entered parse_cmdline(argv={})".format(argv))

    args = docopt(__doc__.replace(' '.join([BLUING_PKG_NAME, PKG_NAME]), PKG_NAME), 
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
        hci_demander_counter = Counter([args['--scan'], args['--ll-feature-set'], 
                                        args['--pairing-feature'], args['--gatt'], 
                                        args['--mon-incoming-conn']])
        if hci_demander_counter[True] == 1:
            if args['-i'] is None:
                args['-i'] = HCI.get_default_iface()
           
            hci = HCI(args['-i'])
            hci.clean_up_running()
            hci.close()

        args['--scan-type'] = args['--scan-type'].lower()
        if args['--scan-type'] not in ('active', 'passive'):
            raise ValueError("Invalid --scan-type: " + red(args['--scan-type']))
        elif args['--scan-type'] == 'active':
            pass
        
        args['--sort'] = args['--sort'].lower()
        if args['--sort'] != "rssi":
            raise ValueError("Invalid --sort: " + red(args['--sort']))
        
        try:
            args['--timeout'] = int(args['--timeout'])
        except ValueError:
            try:
                args['--timeout'] = int(args['--timeout'], base=16)
            except ValueError as e:
                e.args = ("Invalid --timeout: " + red(args['--timeout']),)
                raise e

        if args['--io-cap'] not in ['DisplayOnly', 'DisplayYesNo', 'KeyboardOnly', 
                                    'NoInputNoOutput', 'KeyboardDisplay']:
            raise ValueError("Invalid --io-cap: " + red(args['--io-cap']))

        if args['PEER_ADDR'] is not None:
            if not verify_bd_addr(args['PEER_ADDR']):
                raise ValueError("Invalid PEER_ADDR: " + red(args['BD_ADDR']))
            args['PEER_ADDR'] = args['PEER_ADDR'].upper()

            if args['--addr-type'] is None:
                logger.info("Automatically determining the address type of", blue(args['PEER_ADDR']))
                
                try:
                    args['--addr-type'] = LeScanner.determine_addr_type(
                        args['-i'], args['PEER_ADDR'])
                    logger.info("{} is a {} address".format(
                        blue(args['PEER_ADDR']), blue(args['--addr-type'])))
                except Exception as e:
                    logger.warning("{}: {}\n"
                                   "    Assumed to be {}".format(
                                       e.__class__.__name__, e, yellow('public')))
                    args['--addr-type'] = 'public'
            
            args['--addr-type'] = args['--addr-type'].lower()
            if args['--addr-type'] == 'public':
                args['--addr-type'] = ADDR_TYPE_PUBLIC
            elif args['--addr-type'] == 'random':
                args['--addr-type'] = ADDR_TYPE_RANDOM
            else:
                raise ValueError("Invalid --addr-type: " + red(args['--addr-type']))

        try:
            args['--channel'] =  [int(n) for n in args['--channel'].split(',')]
            args['--channel'] = set(args['--channel'])
            if not args['--channel'].issubset({37, 38, 39}):
                raise ValueError()
        except Exception as e:
            e.args = ("Invalid --channel: " + red(args['--channel']),)
            raise e

        if args['--mon-incoming-conn']:
            raise NotImplementedError("The `--mon-incoming-conn` option is not"
                                      " yet implemented")

        if args['--local']:
            raise NotImplementedError("The `--local` option is not yet implemented")
    except Exception as e:
        logger.error("{}: \"{}\"".format(e.__class__.__name__, e))
        sys.exit(1)
    else:
        return args
