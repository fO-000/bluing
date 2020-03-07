#!/usr/bin/env python3

import time
import select
import subprocess

from bluetooth import discover_devices
from bluetooth import DeviceDiscoverer
from bluetooth import _bluetooth

from bluescan import BlueScanner
from bluescan.ui import WARNING
from bluescan.ui import ERROR
from bluescan.ui import INFO
from bluescan.hci import hci_inquiry_cancel


class BRDiscoverer(DeviceDiscoverer): # DeviceDiscoverer is in bluetooth/bluez.py
    def pre_inquiry(self):
        '''Called when find_devices() returned'''
        self.existing_devs = []
        self.done = False
    
    def device_discovered(self, address, device_class, rssi, name):
        if address not in self.existing_devs:
            self.existing_devs.append(address)
            print('addr:', address)
            print('name:', name.decode())
            print("class: " + "0x%06X" % device_class)
            print('rssi:', rssi, '\n')

    def inquiry_complete(self):
        '''HCI_Inquiry_Complete 与 HCI_Command_Complete 都会导致该函数被回调'''
        self.done = True
        self.existing_devs.clear()


class BRScanner(BlueScanner):
    def scan(self, inquiry_len=8, sort='rssi'):
        existing_devs = []

        print(INFO + 'BR scanning on \x1B[1;34mhci%d\x1B[0m with timeout \x1B[1;34m%.2f sec\x1B[0m\n' % (self.iface, inquiry_len*1.28))
        try:
            #print('[Debug] Call discover_devices()')
            found_devs_info = discover_devices(duration=inquiry_len, 
                flush_cache=False, lookup_names=True, lookup_class=True, 
                device_id=self.iface)
        except KeyboardInterrupt:
            print(INFO + 'Send HCI_Inquiry_Cancel')
            hci_inquiry_cancel()
            return

        # found_devs_info.sort(key=lambda i:i)

        for addr, name, dev_class in found_devs_info:
            if addr not in existing_devs:
                print("addr: " + addr)
                print("name: " + name)
                print("class: " + "0x%06X" % dev_class + "\n")

                existing_devs.append(addr)


    def async_scan(self, inquiry_len=8):
        print(INFO+"BR asynchronous scanning on \x1B[1;34mhci%d\x1B[0m with timeout \x1B[1;34m%.2f sec\x1B[0m\n" % (
            self.iface, inquiry_len*1.28))

        br_discover = BRDiscoverer(self.iface)

        # find_devices() 会立即返回，期间 HCI_Inquiry 也会被发送。
        # flush_cache=False 不让之前 inquiry 发现的设备影响本次扫描结果
        br_discover.find_devices(
            lookup_names=True, duration=inquiry_len, flush_cache=False
        )

        readfiles = [br_discover,]

        while True:
            try:
                rfds = select.select(readfiles, [], [])[0] # blocking
                if br_discover in rfds:
                    #print('[DEBUG] process_event()')
                    # 只有调用 process_event()，device_discovered() 与 
                    # inquiry_complete() 才会被回调
                    br_discover.process_event()

                if br_discover.done:
                    break
            except KeyboardInterrupt:
                # send HCI_Inquiry_Cancel，当收到 HCI_Command_Complete 时
                # inquiry_complete() 将被回调
                br_discover.cancel_inquiry()


def test():
    BRScanner().scan(4)
    

if __name__ == "__main__":
    test()
