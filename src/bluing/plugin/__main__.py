#!/usr/bin/env python

import sys

from xpycommon.log import Logger
from xpycommon.ui import red

from . import PKG_NAME, LOG_LEVEL
from .ui import parse_cmdline
from .list import main as list_main
from .install import main as install_main
from .uninstall import main as uninstall_main
from .run import main as run_main
            

logger = Logger(__name__, LOG_LEVEL)
cmd_to_main = {
    'list': list_main,
    'install': install_main,
    'uninstall': uninstall_main,
    'run': run_main
}


def main(argv: list[str] = sys.argv):
    args = parse_cmdline(argv[1:])
    logger.debug("parse_cmdline() returned\n"
                 "    args:", args)

    try:
        if args['<command>'] is None:
            raise RuntimeError("<command> is None")
        else:
            cmd = args['<command>']
            argv = [cmd] + args['<args>']

            try:
                cmd_to_main[cmd](argv)
            except KeyError as e:
                raise ValueError("Invalid {} command: {}".format(PKG_NAME, red(args['<command>'])))
    except Exception as e:
        logger.error("{}: \"{}\"".format(e.__class__.__name__, e))
        sys.exit(1)
