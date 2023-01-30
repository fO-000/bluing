#!/usr/bin/env python

r"""
Usage:
    bluing br [-h | --help]
    bluing br [-i <hci>] [--inquiry-len=<n>] --inquiry
    bluing br [-i <hci>] --sdp BD_ADDR
    bluing br [-i <hci>] --local --sdp
    bluing br [-i <hci>] --lmp-features BD_ADDR
    bluing br [-i <hci>] --local --lmp-features
    bluing br [-i <hci>] --stack BD_ADDR
    bluing br [-i <hci>] --local --stack
    bluing br [-i <hci>] [--inquiry-scan] --mon-incoming-conn
    bluing br --org=<name> --timeout=<sec> --sniff-and-guess-bd-addr

Arguments:
    BD_ADDR    BR/EDR Bluetooth device address

Options:
    -h, --help                   Print this help and quit
    -i <hci>                     HCI device
    --local                      Target a local BR/EDR device instead of a remote one
    --inquiry                    Discover other nearby BR/EDR controllers
    --inquiry-len=<n>            Maximum amount of time (added to --ext-inquiry-len=<n>) 
                                 specified before the Inquiry is halted.
                                     Time = n * 1.28 s
                                     Time range: 1.28 to 61.44 s
                                     Range of n: 0x01 to 0x30 [default: 8]
    --ext-inquiry-len=<n>        Extended_Inquiry_Length measured in number of 
                                 Baseband slots.
                                     Interval Length = n * 0.625 ms (1 Baseband slot)
                                     Time Range: 0 to 40.9 s
                                     Range of n: 0x0000 to 0xFFFF [default: 0]
    --sdp                        Retrieve information from the SDP database of a 
                                 remote BR/EDR device
    --lmp-features               Read LMP features of a remote BR/EDR device
    --stack                      Determine the Bluetooth stack type of a remote BR/EDR device
    --mon-incoming-conn          Print incoming connection from other nearby BR/EDR devices
    --inquiry-scan               Enable the Inquiry Scan
    --sniff-and-guess-bd-addr    Sniff SAPs of BD_ADDRs over the air, then guess the 
                                 address based on the organization name. Need at 
                                 least one Ubertooth device
    --org=<name>                 An organization name in the OUI.txt
    --timeout=<sec>              Timeout in second(s) [default: 60]
"""


import sys
from collections import Counter

from docopt import docopt
from bthci import HCI

from xpycommon.log import Logger
from xpycommon.ui import red
from xpycommon.bluetooth import verify_bd_addr

from .. import PKG_NAME as BLUING_PKG_NAME
from . import LOG_LEVEL, PKG_NAME


logger = Logger(__name__, LOG_LEVEL)


def parse_cmdline(argv: list[str] = sys.argv[1:]) -> dict:
    logger.debug("Entered parse_cmdline(argv={})".format(argv))
    
    # In order to use `options_first=True` for strict compatibility with POSIX.
    # This replaces multi-level commands in `__doc__` with single-level commands.
    args = docopt(__doc__.replace(' '.join([BLUING_PKG_NAME, PKG_NAME]), PKG_NAME), 
                  argv, help=False, options_first=True)
    logger.debug("docopt() returned\n"
                 "    args:", args)

    try:
        # handle `--help`
        if args['--help'] or len(argv) == 0:
            print(__doc__)
            sys.exit()
            
        # Not all scenarios require HCI devcies. So when the HCI device is `None`
        # (`-i` is `None`), in order to determine whether to use the default HCI 
        # device (need call `clean_up_running()`) or not need the HCI device at all,
        # we can use other options to assist the determination.
        hci_demander_counter = Counter([args['--inquiry'], args['--sdp'], args['--lmp-features'], 
                                        args['--stack'], args['--mon-incoming-conn']])
        if hci_demander_counter[True] == 1:
            if args['-i'] is None:
                args['-i'] = HCI.get_default_iface()
           
            hci = HCI(args['-i'])
            hci.clean_up_running()
            hci.close()

        try:
            args['--inquiry-len'] = int(args['--inquiry-len'])
        except ValueError:
            try:
                args['--inquiry-len'] = int(args['--inquiry-len'], base=16)
            except ValueError as e:
                e.args = ("Invalid --inquiry-len: " + red(args['--inquiry-len']),)
                raise e

        try:
            args['--timeout'] = int(args['--timeout'])
        except ValueError:
            try:
                args['--timeout'] = int(args['--timeout'], base=16)
            except ValueError as e:
                e.args = ("Invalid --timeout: " + red(args['--timeout']),)
                raise e

        if args['BD_ADDR']:
            if not verify_bd_addr(args['BD_ADDR']):
                raise ValueError("Invalid BD_ADDR: " + red(args['BD_ADDR']))
            args['BD_ADDR'] = args['BD_ADDR'].upper()

        if args['--stack']:
            raise NotImplementedError("The `--stack` option is not yet implemented")
        
        if args['--local']:
            raise NotImplementedError("The `--local` option is not yet implemented")
    except Exception as e:
        logger.error("{}: \"{}\"".format(e.__class__.__name__, e))
        sys.exit(1)
    else:
        return args
