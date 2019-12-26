#!/usr/bin/env python3

from bluetooth import discover_devices
from bluetooth import DeviceDiscoverer
from bluetooth import _bluetooth

from bluescan import BlueScanner

import select
import time
import subprocess


OGF = {
    #  Control and Baseband commands, _bluetooth.OGF_HOST_CTL
    'CTL_BB_CMD_OGF': 0x03,
}

OCF = {
    'HCI_Write_Current_IAC_LAP': 0x003A,
    'HCI_Write_Scan_Enable': 0x001A 
}


class BRDiscoverer(DeviceDiscoverer):
    def pre_inquiry(self):
        '''Called when find_devices() returned'''
        self.existing_devs = []
        self.done = False
    
    def device_discovered(self, address, device_class, rssi, name):
        if address not in self.existing_devs:
            self.existing_devs.append(address)
            print('addr:', address)
            print('name:', name)
            print("class: " + "0x%06X" % device_class)
            print('rssi:', rssi, '\n')

    def inquiry_complete(self):
        '''HCI_Inquiry_Complete event 与 HCI_Command_Complete event 都会导致
        该函数被回调'''
        print('\n[i] done')
        self.done = True
        self.existing_devs.clear()


class BRScanner(BlueScanner):
    def scan(self, inquiry_len=8, sort='rssi'):
        existing_devs = []

        print("BR scanning on hci%d...timeout %.2f sec\n" % (self.iface, 
            inquiry_len*1.28)
        )
        try:
            #print('[Debug] discover_devices()')
            found_devs_info = discover_devices(duration=inquiry_len, 
                flush_cache=False, lookup_names=True, lookup_class=True, 
                device_id=self.iface
            )
        except KeyboardInterrupt:
            subprocess.getoutput('hcitool cmd 0x1 0x2')
            return

        # found_devs_info.sort(key=lambda i:i)

        for addr, name, dev_class in found_devs_info:
            if addr not in existing_devs:
                print("[BR scan] discovered new device")
                print("addr: " + addr)
                print("name: " + name)
                print("class: " + "0x%06X" % dev_class + "\n\n")

                existing_devs.append(addr)


    def async_scan(self, inquiry_len=8):
        print("BR async scanning on hci%d...timeout %.2f sec\n" % (self.iface, 
            inquiry_len*1.28)
        )
        #subprocess.run(['systemctl', 'restart', 'bluetooth.service'])
        #time.sleep(0.5)

        br_discover = BRDiscoverer(self.iface)
        # br_discover.cancel_inquiry()
        # br_discover.process_event()
        # find_devices() 会立即返回，HCI_Inquiry 也会被发送出去。
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
                # HCI_Inquiry_Cancel 会触发 HCI_Command_Complete event
                # 进而导致 inquiry_complete() 被调用
                # _bluetooth.hci_send_cmd(
                #     br_discover.sock, _bluetooth.OGF_LINK_CTL, 
                #     _bluetooth.OCF_INQUIRY_CANCEL
                # )
                br_discover.cancel_inquiry()


if __name__ == "__main__":
    BRScanner().scan(4)
