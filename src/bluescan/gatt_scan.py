#!/usr/bin/env python3

import sys
import io

from bluepy.btle import Peripheral
from bluepy.btle import BTLEException

from bluescan import BlueScanner

import pkg_resources

# char_uuid = pkg_resources.resource_string()
# service_uuid = pkg_resources.resource_string()

service_uuid_file = pkg_resources.resource_stream(__name__, "res/gatt-service-uuid.txt")
service_uuid_file = io.TextIOWrapper(service_uuid_file)

char_uuid_file = pkg_resources.resource_stream(__name__, 'res/gatt-characteristic-uuid.txt')
char_uuid_file = io.TextIOWrapper(char_uuid_file)

descriptor_uuid_file = pkg_resources.resource_stream(__name__, 'res/gatt-descriptor-uuid.txt')
descriptor_uuid_file = io.TextIOWrapper(descriptor_uuid_file)

services_spec = {}
characteristics_spec = {}
descriptors_spec = {}

for line in service_uuid_file:
    items = line.strip().split('\t')
    uuid = items.pop(2)
    services_spec[uuid] = {
        'Name': items[0],
        'Uniform Type Identifier': items[1],
        'Specification': items[2]
    }

for line in char_uuid_file:
    items = line.strip().split('\t')
    uuid = items.pop(2)
    characteristics_spec[uuid] = {
        'Name': items[0],
        'Uniform Type Identifier': items[1],
        'Specification': items[2]
    }

for line in descriptor_uuid_file:
    items = line.strip().split('\t')
    uuid = items.pop(2)
    descriptors_spec[uuid] = {
        'Name': items[0],
        'Uniform Type Identifier': items[1],
        'Specification': items[2]
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

        # Show service
        for service in services:
            characteristics = service.getCharacteristics()

            print("\x1B[1;34mService declaration\x1B[0m", '(%s characteristics)' % len(characteristics))
            print("    Handle:", "\"attr handle\" by using gatttool -b <BD_ADDR> --primary")
            print("    Type: (May be primary service 00002800-0000-1000-8000-00805f9b34fb)")
            print("    Value (Service UUID): \x1B[1;34m%s" % service.uuid, end=' ')
            try:
                print('(' + services_spec[
                    '0x' + ("%s" % service.uuid)[4:8].upper()
                ]['Name'] + ')', '\x1B[0m')
            except KeyError:
                print("(Unknown service)", '\x1B[0m')
            print('    Permission: Read Only, No Authentication, No Authorization\n')

            # Show characteristic
            for characteristic in characteristics:
                descriptors = characteristic.getDescriptors()
                try:
                    print("\x1B[1;33m    Characteristic declaration\x1B[0m", '(%s descriptors)' % len(descriptors))
                    #print('-'*8)
                    print("        Handle: %#06x" % (characteristic.getHandle() - 1))
                    print("        Type: 00002803-0000-1000-8000-00805f9b34fb")
                    print("        Value:")
                    print("            Characteristic properties:\x1B[1;32m", characteristic.propertiesToString(), "\x1B[0m")
                    print("            Characteristic value handle: %#06x" % characteristic.getHandle())
                    print("            Characteristic UUID: \x1B[1;32m", characteristic.uuid, end=' ') # This UUID is also the type field of characteristic value declaration attribute.
                    try:
                        print('(' + characteristics_spec[
                            '0x' + ("%s" % characteristic.uuid)[4:8].upper()
                        ]['Name'] + ')', '\x1B[0m')
                    except KeyError:
                        print("(Unknown characteristic)", '\x1B[0m')
                    print('        Permission: Read Only, No Authentication, No Authorization')
                    
                    if characteristic.supportsRead():
                        print("\x1B[1;33m    Characteristic value declaration\x1B[0m")
                        print("        Handle:\x1B[1;32m %#06x" % characteristic.getHandle(), "\x1B[0m")
                        print("        Type:", characteristic.uuid)
                        print("        Value:\x1B[1;32m", characteristic.read(), "\x1B[0m")
                        print("        Permission: Higher layer profile or implementation specific")
                except BTLEException as e:
                    print('        ' + str(e))

                # Show descriptor
                for descriptor in descriptors:
                    try:
                        print("\x1B[1;33m    Descriptor declaration\x1B[0m")
                        print("        Handle:\x1B[1;32m %#06x" % descriptor.handle, "\x1B[0m")
                        print("        Type:\x1B[1;32m", descriptor.uuid, end=' ')
                        try:
                            print('(' + descriptors_spec[
                                '0x' + ("%s" % descriptor.uuid)[4:8].upper()
                            ]['Name'] + ')', '\x1B[0m')
                        except KeyError:
                            print("(Unknown descriptor)", '\x1B[0m')
                        print('        Value:', descriptor.read())
                        print('        Permissions:')
                    except BTLEException as e:
                        print('        ' + str(e))
                print()
            print()


if __name__ == "__main__":
    pass
