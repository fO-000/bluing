#!/usr/bin/env python

import sys

from xpycommon.log import Logger

from .. import BluingPluginManager

from . import LOG_LEVEL
from .ui import parse_cmdline


logger = Logger(__name__, LOG_LEVEL)


def main(argv: list[str] = sys.argv):
    args = parse_cmdline(argv[1:])
    logger.debug("parse_cmdline() returned\n"
                 "    args:", args)

    try:
        BluingPluginManager.uninstall(args['NAME'])
    except Exception as e:
        logger.error("{}: \"{}\"".format(e.__class__.__name__, e))
        sys.exit(1)
