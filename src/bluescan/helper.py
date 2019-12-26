#!/usr/bin/env python3

import re

def valid_bdaddr(addr:str) -> bool:
    regexp = r'(?:[\da-fA-F]{2}:){5}[\da-fA-F]{2}'
    result = re.findall(regexp, addr)
    if len(result) == 0 or result[0] != addr:
        return False
    else:
        return True


def hcix2i(hcix:str) -> int:
    '''Extract HCI devive number from hcixxxx'''
    regexp = "[0-9]+"
    hci_num = re.findall(regexp, hcix)
    if len(hci_num) != 1:
        raise ValueError("[ValueError] The BlueScanner constructor's iface argument contains more than one HCI device number.")
    else:
        return int(hci_num[-1])


if __name__ == '__main__':
    valid_bdaddr('11:22:33:44:55:66')
