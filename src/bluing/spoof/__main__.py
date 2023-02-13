#!/usr/bin/env python

import sys

from xpycommon.log import Logger
from xpycommon.bluetooth.bluez import spoof_bd_addr, spoof_cls_of_dev, \
    spoof_host_name, spoof_controller_alias

from . import LOG_LEVEL
from .ui import parse_cmdline


logger = Logger(__name__, LOG_LEVEL)


def main(argv: list[str] = sys.argv):
    args = parse_cmdline(argv[1:])
    logger.debug("parse_cmdline() returned\n"
                 "    args:", args)

    try:
        if args['--bd-addr']:
            spoof_bd_addr(args['--bd-addr'], args['-i'])
        elif args['--cls-of-dev']:
            spoof_cls_of_dev(args['--cls-of-dev'], args['-i'])
        elif args['--host-name']:
            spoof_host_name(args['--host-name'])
        elif args['--alias']:
            spoof_controller_alias(args['--alias'], args['-i'])
        else:
            raise ValueError("Invalid option(s)")
    except Exception as e:
        logger.error("{}: \"{}\"".format(e.__class__.__name__, e))
        sys.exit(1)
