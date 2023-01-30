#!/usr/bin/env python

r"""
Usage:
    bluing android [-h | --help]
    bluing android [-t <id>] --collect-btsnoop-log [-o <file>]

Options:
    -h, --help               Display this help and quit
    -t <id>                  Use android device with given transport id. This option 
                             will be ignored when only one device is available
    --collect-btsnoop-log    Collect the btsnoop log being generated to a local file, 
                             default ./btsnoop_hci.log
    -o <file>                Place the output into <file> [default: ./btsnoop_hci.log]
"""


import sys

from docopt import docopt
from xpycommon.log import Logger
from xpycommon import str2int, check_malicious_char
from xpycommon.ui import red
from xpycommon.android import get_adb_transport_ids

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

        if args['-t'] is not None:
            try:
                args['-t'] = str2int(args['-t'])
            except ValueError as e:
                e.args = ("Invalid -t: " + red(args['-t']),)
                raise e
            
            transport_ids = get_adb_transport_ids()
            
            if len(transport_ids) == 0:
                raise RuntimeError("No connected Android devices found")
            elif len(transport_ids) == 1:
                args['-t'] = None
            elif len(transport_ids) > 1:
                if args['-t'] not in transport_ids:
                    logger.info("Valid transport ID(s):", transport_ids)
                    raise ValueError("Transport ID {} not found".format(red(str(args['-t']))))
            else:
                raise RuntimeError("Android devices transport ID error: {}".format(
                    red(str(transport_ids))))

        check_malicious_char(args['-o'], ['.', '/'])
    except Exception as e:
        logger.error("{}: \"{}\"".format(e.__class__.__name__, e))
        sys.exit(1)
    else:
        return args
