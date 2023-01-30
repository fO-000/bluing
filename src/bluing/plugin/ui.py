#!/usr/bin/env python

r"""
Usage:
    bluing plugin [-h | --help]
    bluing plugin <command> [<args>...]

Options:
    -h, --help    Display this help and quit

Commands:
    list         List installed plugins
    install      Install a plugin
    uninstall    Uninstall a plugin
    run          Run a plugin
"""


import sys

from docopt import docopt
from xpycommon.log import Logger

from .. import PKG_NAME as BLUING_PKG_NAME

from . import LOG_LEVEL, PKG_NAME


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
    except Exception as e:
        logger.error("{}: \"{}\"".format(e.__class__.__name__, e))
        sys.exit(1)
    else:
        return args
