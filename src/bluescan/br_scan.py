#!/usr/bin/env python3

import time
import select
import subprocess

from bluetooth import discover_devices
from bluetooth import DeviceDiscoverer
from bluetooth import _bluetooth

from bluescan import BlueScanner
from .ui import DEBUG
from .ui import INFO
from .ui import WARNING
from .ui import ERROR
from .ui import blue

from .hci import HCI


major_dev_clses = {
    0b00000: 'Miscellaneous',
    0b00001: 'Computer',
    0b00010: 'Phone',
    0b00011: 'Lan/Network Access Point',
    0b00100: 'Audio/Video',
    0b00101: 'Peripheral (HID)',
    0b00110: 'Imaging',
    0b00111: 'Wearable',
    0b01000: 'Toy',
    0b01001: 'Health',
    0b11111: 'Uncategorized'
}

# DeviceDiscoverer is in bluetooth/bluez.py
class BRDiscoverer(DeviceDiscoverer):
    def pre_inquiry(self):
        '''Called when find_devices() returned'''
        self.existing_devs = []
        self.done = False
    
    def device_discovered(self, address, device_class, rssi, name):
        if address not in self.existing_devs:
            self.existing_devs.append(address)
            print('addr:', blue(address))
            print('name:', blue(name.decode()))
            print('class: 0x%06X' % device_class)
            pp_cod(device_class)
            print('rssi:', rssi, '\n')

    def inquiry_complete(self):
        '''HCI_Inquiry_Complete 与 HCI_Command_Complete 都会导致该函数被回调'''
        self.done = True


class BRScanner(BlueScanner):
    # def scan(self, inquiry_len=8, sort='rssi'):

    #     print(INFO, 'BR scanning on \x1B[1;34mhci%d\x1B[0m with timeout \x1B[1;34m%.2f sec\x1B[0m\n' % (self.devid, inquiry_len*1.28))

    #     existing_devs = []
    #     found_devs_info = []

    #     try:
    #         # When using BlueZ, discover_devices() is in bluetooth/bluez.py
    #         found_devs_info = discover_devices(duration=inquiry_len, 
    #             lookup_names=True, lookup_class=True, device_id=self.devid)
    #     except KeyboardInterrupt:
    #         HCI(self.iface).inquiry_cancel()

    #     # found_devs_info.sort(key=lambda i:i)

    #     for addr, name, dev_class in found_devs_info:
    #         if addr not in existing_devs:
    #             print("addr: " + blue(addr))
    #             print("name: " + blue(name))
    #             print("class: " + "0x%06X" % dev_class)
    #             pp_cod(dev_class)
    #             print()

    #             existing_devs.append(addr)

    def scan(self, inquiry_len=8):
        '''timeout = inquiry_len * 1.28 s'''
        print(INFO, "BR scanning on \x1B[1;34mhci%d\x1B[0m with timeout \x1B[1;34m%.2f sec\x1B[0m\n" % (
            self.devid, inquiry_len*1.28))

        br_discover = BRDiscoverer(self.devid)

        # find_devices() 会立即返回，期间 HCI_Inquiry command 也会被发送。
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


def pp_cod(cod:int):
    '''Print and parse Class of Device.'''
    #print(DEBUG, 'br_scan.py pp_cod()')
    if cod > 0xFFFFFF:
        print(WARNING, "CoD's Format Type is not format #1")
        return
    elif cod & 0x000003 != 0:
        print(WARNING, "CoD's Format Type is not format #1")
        return

    print('    Service Class: %s' % bin(cod>>13))
    information = lambda b: (b >> 23) & 1
    telephony = lambda b: (b >> 22) & 1
    audio = lambda b: (b >> 21) & 1
    object_transfer = lambda b: (b >> 20) & 1
    capturing = lambda b: (b >> 19) & 1
    rendering = lambda b: (b >> 18) & 1
    networking = lambda b: (b >> 17) & 1
    positioning = lambda b: (b >> 16) & 1
    limited_discoverable_mode = lambda b: (b >> 13) & 1

    # Parse Service Class Field
    if information(cod):
        print(' '*8+'Information (WEB-server, WAP-server, ...)')

    if telephony(cod):
        print(' '*8+'Telephony (Cordless telephony, Modem, Headset service, ...)')

    if audio(cod):
        print(' '*8+'Audio (Cordless telephony, Modem, Headset service, ...)')

    if object_transfer(cod):
        print(' '*8+'Object Transfer (v-Inbox, v-Folder, ...)')

    if capturing(cod):
        print(' '*8+'Capturing (Scanner, Microphone, ...)')

    if rendering(cod):
        print(' '*8+'Rendering (Printing, Speaker, ...)')

    if networking(cod):
        print(' '*8+'Networking (LAN, Ad hoc, ...)')

    if positioning(cod):
        print(' '*8+'Positioning (Location identification)')

    if limited_discoverable_mode(cod):
        print(' '*8+'Limited Discoverable Mode')

    # Parse Major Device Class
    major_dev_cls = (cod>>8)&0x001F
    print('    Major Device Class: %s,'%bin(major_dev_cls), major_dev_clses[major_dev_cls])

    # Parse Minor Device class
    pp_minor_dev_cls((cod>>8)&0x0000, major_dev_cls)


def pp_minor_dev_cls(val:int, major_dev_cls:int):
    pass


def __test():
    #BRScanner().scan(4)
    pp_minor_dev_cls(0x002540)


if __name__ == "__main__":
    __test()
