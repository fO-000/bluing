#!/usr/bin/env python3


import sys

from bluepy.btle import Peripheral
from bluepy.btle import BTLEException

from bluescan import BlueScanner


num_serv_names = {
    '1800': 'Generic Access',
    '1801': 'Generic Attribute',
    '1802': 'Immediate Alert',
    '180a': 'Device Information',
    '180d': 'Heart Rate',
    '1811': 'Alert Notification Service',
}

num_char_names = {
    '2a00': 'Device Name',
    '2a01': 'Appearance',
    '2a04': 'Peripheral Preferred Connection Parameters',
    '2a05': 'Service Changed',
    '2a06': 'Alert Level',
    '2a23': 'System ID',
    '2a24': 'Model Number String',
    '2a25': 'Serial Number String',
    '2a26': 'Firmware Revision String',
    '2a27': 'Hardware Revision String',
    '2a28': 'Software Revision String',
    '2a29': 'Manufacturer Name String',
    '2a2a': 'IEEE 11073-20601 Regulatory Certification Data List',
    '2a37': 'Heart Rate Measurement',
    '2a38': 'Body Sensor Location',
    '2a39': 'Heart Rate Control Point',
    '2a44': 'Alert Notification Control Point',
    '2a46': 'New Alert',
    '2a45': 'Unread Alert Status',
    '2a47': 'Supported New Alert Category',
    '2a48': 'Supported Unread Alert Category',
    '2a50': 'PnP ID',
}


class GATTScanner(BlueScanner):
    def scan(self, bdaddr, addr_type):
        #print("[Debug] target_addr:", self.target_bdaddr)
        #print("[Debug] iface:", self.iface)
        #print("[Debug] addr_type:", self.addr_type)
        target = Peripheral(bdaddr, iface=self.iface, addrType=addr_type)
        #print("[Debug] target", target)

        services = target.getServices()
        print("Number of services: %s\n\n" % len(services))

        for service in services:
            print("\x1B[1;34mService declaration attribute\x1B[0m")
            print("    Handle:", "\"attr handle\" by using gatttool -b <BD_ADDR> --primary")
            print("    type: (May be primary service 00002800-0000-1000-8000-00805f9b34fb)")
            print("    Value (Service UUID): \x1B[1;34m%s" % service.uuid, end=' ')
            try:
                print('(' + num_serv_names[("%s" % service.uuid)[4:8]] + ')', '\x1B[0m')
            except KeyError:
                print("(Unknown service)", '\x1B[0m')

            characteristics = service.getCharacteristics()
            print("Number of characteristics: %s\n" % len(characteristics))
            
            for characteristic in characteristics:
                try:
                    print("\x1B[1;33m    Characteristic declaration attribute\x1B[0m")
                    print("        handle:")
                    print("        type:")
                    print("        value:")
                    print("            Properties:\x1B[1;32m", characteristic.propertiesToString(), "\x1B[0m")
                    print("            Characteristic value attribute handle: %#06x" % characteristic.getHandle())
                    # 该 UUID 存在于 characteristic declaration attribute 的
                    # value 字段中，也是 characteristic value attribute 的 type
                    # 字段。
                    print("            Characteristic value attribute UUID: \x1B[1;32m", characteristic.uuid, end=' ')
                    try:
                        print('(' + num_char_names[("%s" % characteristic.uuid)[4:8]] + ')', '\x1B[0m')
                    except KeyError:
                        print("(Unknown characteristic)", '\x1B[0m')
                    
                    if characteristic.supportsRead():
                        print("    Characteristic value attribute")
                        print("        handle:\x1B[1;32m %#06x" % characteristic.getHandle(), "\x1B[0m")
                        print("        type:", characteristic.uuid)
                        print("        value:\x1B[1;32m", characteristic.read(), "\x1B[0m")
                    
                    print("")  
                except BTLEException as e:
                    print(e.__str__, '\n')

            print("")

        # 目前 bluepy 还不支持对 descriptor 进行操作。
        descriptors = target.getDescriptors()
        for descriptor in descriptors:
            print(descriptor)
            print("Handle:\x1B[1;32m %#06x" % descriptor.handle, "\x1B[0m")
            print("Type:\x1B[1;32m", descriptor.uuid,"\x1B[0m", '\n')


if __name__ == "__main__":
    pass
