#!/usr/bin/env python3

import re
import sys

import subprocess


def valid_bdaddr(addr:str) -> bool:
    regexp = r'(?:[\da-fA-F]{2}:){5}[\da-fA-F]{2}'
    result = re.findall(regexp, addr)
    if len(result) == 0 or result[0] != addr:
        return False
    else:
        return True


def find_rfkill_devid(dev='hci0') -> int:
    exitcode, output = subprocess.getstatusoutput('rfkill -rno ID,DEVICE')

    for line in output.splitlines():
        id_dev = line.split()
        if len(id_dev) == 2 and id_dev[1] == dev:
            return int(id_dev[0])
        else:
            continue
    
    raise Exception("Can't find the ID of %s in rfkill" % dev)


def __test():
    #valid_bdaddr('11:22:33:44:55:66')
    print(find_rfkill_devid('hci1'))


if __name__ == '__main__':
    __test()
