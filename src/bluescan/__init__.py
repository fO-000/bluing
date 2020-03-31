#!/usr/bin/env python3

from .hci import HCI

class BlueScanner():
    def __init__(self, iface='hci0'):
        self.iface = iface
        self.devid = HCI.hcix2devid(self.iface)
