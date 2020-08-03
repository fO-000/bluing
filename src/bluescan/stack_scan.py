#!/usr/bin/env python3

from . import BlueScanner

import struct
from bluetooth import BluetoothSocket
from bluetooth import L2CAP

stack_feature = {

}


class StackScanner(BlueScanner):
    def scan(self, bd_addr:str):
        print('[DEBUG] call StackScanner.scan()')
        remote_addr = bd_addr
        psm = 0x0001

        l2_sock = BluetoothSocket(L2CAP)

        code = 0x08
        identifier = 0x01
        length = 0x0001
        data = b'\xff'

        # payload = struct.pack('<BBHC', code, identifier, length, data)
        payload = struct.pack('<BBH1s', code, identifier, length, data)

        l2_sock.connect((remote_addr, psm))
        l2_sock.send(payload)
        data = l2_sock.recv(1024)


def __test():
    pass


if __name__ == '__main__':
    __test()
