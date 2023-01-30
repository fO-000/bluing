#!/usr/bin/env python

import sys
from subprocess import CalledProcessError, check_output, STDOUT
from traceback import format_exception

from xpycommon.log import Logger
from xpycommon.ui import blue
from xpycommon.bluetooth import sniff_and_guess_bd_addr

from bthci import HCI, ControllerErrorCodes, ScanEnableValues
from bthci.commands import HCI_Write_Inquiry_Scan_Activity
from bthci.events import HCI_Connection_Request

from . import LOG_LEVEL
from .ui import parse_cmdline
from .br_scan import BrScanner
from .sdp_scan import SdpScanner


logger = Logger(__name__, LOG_LEVEL)


def main(argv: list[str] = sys.argv):
    args = parse_cmdline(argv[1:])
    logger.debug("parse_cmdline() returned\n"
                 "    args:", args)

    try:
        if args['--inquiry']:
            br_scanner = BrScanner(args['-i'])
            br_scanner.inquiry(inquiry_len=args['--inquiry-len'])
        elif args['--sdp']:
            SdpScanner(args['-i']).scan(args['BD_ADDR'])
        elif args['--lmp-features']:
            if args['--local']: # Move to BrScanenr
                # HCI Read Local Supported Features 
                raise NotImplementedError("The `--local` option is not yet implemented")
            else:
                br_scanner = BrScanner(args['-i'])
                br_scanner.scan_lmp_features(args['BD_ADDR'])
        elif args['--stack']:
            # StackScanner(args['-i']).scan(args['BD_ADDR'])
            raise NotImplementedError("The `--stack` option is not yet implemented")
        elif args['--mon-incoming-conn']:
            hci = HCI(args['-i'])

            cmd_complete = hci.write_inquiry_scan_activity(
                HCI_Write_Inquiry_Scan_Activity.inquiry_scan_interval_max, 
                HCI_Write_Inquiry_Scan_Activity.inquiry_scan_window_max)
            if cmd_complete.status != ControllerErrorCodes.SUCCESS:
                logger.warning("Failed to write inquiry scan activity\n"
                            "    command complete status: 0x{:02x} - {} ".format(
                                cmd_complete.status, cmd_complete.status.name))
            
            cmd_complete = hci.read_inquiry_scan_activity()
            if cmd_complete.status != ControllerErrorCodes.SUCCESS:
                logger.warning("Failed to read inquiry scan activity\n"
                            "    command complete status: 0x{:02x} - {} ".format(
                                cmd_complete.status, cmd_complete.status.name))
            else:
                logger.info("Inquiry_Scan_Interval: {}, {} ms\n"
                            "Inquiry_Scan_Window:   {}, {} ms".format(cmd_complete.inquiry_scan_interval, cmd_complete.inquiry_scan_interval * 0.625,
                                                                    cmd_complete.inquiry_scan_window, cmd_complete.inquiry_scan_window * 0.625))
                if cmd_complete.inquiry_scan_interval != HCI_Write_Inquiry_Scan_Activity.inquiry_scan_interval_max:
                    logger.warning("Current Inquiry_Scan_Interval is not max value.")
                if cmd_complete.inquiry_scan_window != HCI_Write_Inquiry_Scan_Activity.inquiry_scan_window_max:
                    logger.warning("Current Inquiry_Scan_Window is not max value.")
            
            scan_enable = ScanEnableValues.pscan
            if args['--inquiry-scan']:
                scan_enable = ScanEnableValues.piscan

            cmd_complete = hci.write_scan_enable(scan_enable)
            if cmd_complete.status != ControllerErrorCodes.SUCCESS:
                logger.warning("Failed to enable inquiry/page scan\n"
                            "    command complete status: 0x{:02x} - {} ".format(
                                cmd_complete.status, cmd_complete.status.name))
            
            cmd_complete = hci.read_scan_enable()
            if cmd_complete.status != ControllerErrorCodes.SUCCESS:
                logger.warning("Failed to read scan enable\n"
                            "    command complete status: 0x{:02x} - {} ".format(
                                cmd_complete.status, cmd_complete.status.name))
            else:
                logger.info(cmd_complete.scan_enable.desc)
                print()

            try:
                while True:
                    conn_req = hci.wait_event(HCI_Connection_Request.evt_code, timeout=None)
                    print("{} incoming\n"
                        "    CoD: 0x{:06x}".format(blue(conn_req.bd_addr), 
                                                                    conn_req.class_of_dev))
                    conn_req.class_of_dev.print_human_readable(2)
                    print("    link type: 0x{:02x} - {}".format(conn_req.link_type, conn_req.link_type.name))
                    print()
            except KeyboardInterrupt:
                sys.exit()
        elif args['--sniff-and-guess-bd-addr']:
            sniff_and_guess_bd_addr(args['--org'], args['--timeout'])
        else:
            raise ValueError("Invalid option(s)")
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
    except Exception as e:
        e_info = ''.join(format_exception(*sys.exc_info()))
        logger.debug("e_info: {}".format(e_info))
        logger.error("{}: \"{}\"".format(e.__class__.__name__, e))
        sys.exit(1)
