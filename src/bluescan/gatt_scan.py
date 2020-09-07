#!/usr/bin/env python3

import sys
import io

from bluepy.btle import Peripheral
from bluepy.btle import BTLEException

from . import BlueScanner

import pkg_resources

from pyclui import green, blue, yellow, red, \
    DEBUG, INFO, WARNING, ERROR

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
    def scan(self, bdaddr, addr_type, include_descriptor:bool):
        #print("[Debug] target_addr:", self.target_bdaddr)
        #print("[Debug] iface:", self.iface)
        #print("[Debug] addr_type:", self.addr_type)
        target = Peripheral(bdaddr, iface=self.devid, addrType=addr_type)
        #print("[Debug] target", target)

        services = target.getServices()
        print("Number of services: %s\n\n" % len(services))

        # Show service
        for service in services:
            characteristics = service.getCharacteristics()

            print(blue('Service'), '(%s characteristics)' % len(characteristics))
            print('\tHandle:", "\"attr handle\" by using gatttool -b <BD_ADDR> --primary')
            print('\tType: (May be primary service 0x2800)')
            print('\tValue (Service UUID): ', blue(str(service.uuid)), end=' ')
            try:
                print('(' + services_spec[
                    '0x' + ("%s" % service.uuid)[4:8].upper()
                ]['Name'] + ')', '\x1B[0m')
            except KeyError:
                print('('+red('unknown')+')', '\x1B[0m')
            print('\tPermission: Read Only, No Authentication, No Authorization\n')

            # Show characteristic
            for characteristic in characteristics:
                descriptors = []
                # 对每个 characteristic 都获取 descriptor 会很耗时
                # 有些设备会因此断开连接。于是这里提供了一个是否获取 descriptor 的选项
                if include_descriptor:
                    descriptors = characteristic.getDescriptors()
                
                try:
                    print(yellow('\tCharacteristic'), '(%s descriptors)' % len(descriptors))
                    #print('-'*8)
                    print('\t\tHandle: %#06x' % (characteristic.getHandle() - 1))
                    print('\t\tType: 0x2803 (tCharacteristic)')
                    print('\t\tValue:')
                    print('\t\t\tCharacteristic properties:', green(characteristic.propertiesToString()))
                    print('\t\t\tCharacteristic value handle: %#06x' % characteristic.getHandle())
                    print('\t\t\tCharacteristic UUID: ', green(str(characteristic.uuid)), end=' ') # This UUID is also the type field of characteristic value declaration attribute.
                    try:
                        print('(' + characteristics_spec[
                            '0x' + ("%s" % characteristic.uuid)[4:8].upper()
                        ]['Name'] + ')')
                    except KeyError:
                        print('('+red('unknown')+')')
                    print('\t\tPermission: Read Only, No Authentication, No Authorization')
                    
                    if characteristic.supportsRead():
                        print(yellow('\tCharacteristic value'))
                        print('\t\tHandle:', green('%#06x' % characteristic.getHandle()))
                        print('\t\tType:', characteristic.uuid)
                        print('\t\tValue:', green(str(characteristic.read())))
                        print('\t\tPermission: Higher layer profile or implementation-specific')
                except BTLEException as e:
                    print('        ' + str(e))

                # Show descriptor
                for descriptor in descriptors:
                    try:
                        print('\tDescriptor')
                        print('\t\tHandle:', green('%#06x' % descriptor.handle))
                        print('\t\tType:', descriptor.uuid, end=' ')
                        try:
                            print('(' + descriptors_spec[
                                '0x' + ("%s" % descriptor.uuid)[4:8].upper()
                            ]['Name'] + ')')
                        except KeyError:
                            print('(Unknown descriptor)')
                        print('\t\tValue:', descriptor.read())
                        print('\t\tPermissions:')
                    except BTLEException as e:
                        print('\t\t' + str(e))
                print()
            print()


if __name__ == "__main__":
    pass
