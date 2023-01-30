#!/usr/bin/env python

import sys

from xpycommon.log import Logger
from xpycommon.android import adb_devices_long, get_adb_transport_ids
from xpycommon.ui import red

from . import LOG_LEVEL
from .ui import parse_cmdline
from .collect_btsnoop_log import collect_btsnoop_log



logger = Logger(__name__, LOG_LEVEL)


def main(argv: list[str] = sys.argv):
    args = parse_cmdline(argv[1:])
    logger.debug("parse_cmdline() returned\n"
                 "    args: {}".format(args))

    try:
        if args['--collect-btsnoop-log']:
            transport_ids = get_adb_transport_ids()
            if args['-t'] is None:
                if len(transport_ids) == 0:
                    raise RuntimeError("No connected Android devices found")
                elif len(transport_ids) == 1:
                    pass
                elif len(transport_ids) > 1:
                    logger.info("Valid transport ID(s):", transport_ids)
                    raise RuntimeError("Found multiple ADB devices, need to specify a transport ID")
                else:
                    raise RuntimeError("Android devices transport ID error: {}".format(
                        red(str(transport_ids))))

            transport_id = args['-t']
            collect_btsnoop_log(transport_id, args['-o'])
        else:
            raise ValueError("Invalid option(s)")
    except Exception as e:
        logger.error("{}: \"{}\"".format(e.__class__.__name__, e))

    
if __name__ == '__main__':
    main()
