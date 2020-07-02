#!/usr/bin/env python3

import re
import sys

import subprocess

from .ui import WARNING
from .ui import ERROR
from .ui import INFO


def valid_bdaddr(addr:str) -> bool:
    regexp = r'(?:[\da-fA-F]{2}:){5}[\da-fA-F]{2}'
    result = re.findall(regexp, addr)
    if len(result) == 0 or result[0] != addr:
        return False
    else:
        return True


def find_rfkill_devid(dev='hci0') -> int:
    exitcode, output = subprocess.getstatusoutput('rfkill --output ID,DEVICE -r')
    for line in output.splitlines()[1:]:
        id_dev = line.split()
        if len(id_dev) == 2 and id_dev[1] == dev:
            return int(id_dev[0])
        else:
            continue
    
    raise Exception("Can't find the ID of %s in rfkill" % dev)


def __test():
    valid_bdaddr('11:22:33:44:55:66')
    pp_lmp_features(b'\xbf\xfeO\xfe\xdb\xff[\x87')
    pp_ext_lmp_features(b'\xbf\xfe\xcf\xfe\xdb\xff{\x87', 0)
    pp_ext_lmp_features(b'\x0f\x00\x00\x00\x00\x00\x00\x00', 1)
    pp_ext_lmp_features(b'0\x0b\x00\x00\x00\x00\x00\x00', 2)


if __name__ == '__main__':
    __test()
