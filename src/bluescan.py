#!/usr/bin/env python3

from blue_scanner import BlueScanner
from ui import parse_cmdline
from bluepy.btle import BTLEException


def main():
    try:
        args = parse_cmdline()

        blue_scanner = BlueScanner(
            args['-m'], args['-i'], 
            timeout=args['--timeout'], le_scan_type=args['--le-scan-type']
        )
        blue_scanner.scan()
    except ValueError as e:
        print(e)
    except BTLEException as e:
        print(e)
    except KeyboardInterrupt:
        print("\n[" + args['-m'] + " scan] stopped\n")


if __name__ == "__main__":
    main()
