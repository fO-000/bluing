#!/usr/bin/env python3

import io
import pkg_resources
from bthci import HCI



# https://www.bluetooth.com/specifications/assigned-numbers/service-discovery/
#     Table 2: Service Class Profile Identifiers
#
#     For historical reasons, some UUIDs in Table 2 are used to identify 
#     profiles in a BluetoothProfileDescriptorList universal attribute as well 
#     as service classes in a ServiceClassIDList universal attribute. However, 
#     for new profiles, Service Class UUIDs shall not be used in a 
#     BluetoothProfileDescriptorList universal attribute and Profile UUIDs 
#     shall not be used in a ServiceClassIDList universal attribute.
#
# Include both service class UUID (32-bit) and profile UUID (32-bit), and other
# information. 
service_cls_profile_ids_file = pkg_resources.resource_stream(__name__, 
    'res/service-class-profile-ids.txt')
service_cls_profile_ids_file = io.TextIOWrapper(
    service_cls_profile_ids_file)
service_cls_profile_ids = {}

# 需要手动编辑的 Service Class 如下：
#     IrMCSyncCommand
#     Headset – HS
# 同时注意去掉可能出现的 E2 80 8B
for line in service_cls_profile_ids_file:
    items = line.strip().split('\t')
    if items[0] == 'Service Class Name':
        continue
    # print(items)
    uuid = int(items.pop(1)[2:], base=16)
    service_cls_profile_ids[uuid] = {
        'Name': items[0],
        'Specification': items[1],
        'Allowed Usage': items[2]
    }


COMPLETE_16_BIT_SERVICE_CLS_UUID_LIST  = 0x03
COMPLETE_32_BIT_SERVICE_CLS_UUID_LIST  = 0x05
COMPLETE_128_BIT_SERVICE_CLS_UUID_LIST = 0x07
COMPLETE_LOCAL_NAME                    = 0X09
SHORTENED_LOCAL_NAME                   = 0X08
TX_POWER_LEVEL                         = 0x0a

gap_type_name_pairs = {
    0x01: 'Flags',
    0x02: 'Incomplete List of 16-bit Service Class UUIDs',
    COMPLETE_16_BIT_SERVICE_CLS_UUID_LIST: 'Complete List of 16-bit Service Class UUIDs',
    0x04: 'Incomplete List of 32-bit Service Class UUIDs',
    COMPLETE_32_BIT_SERVICE_CLS_UUID_LIST: 'Complete List of 32-bit Service Class UUIDs',
    0x06: 'Incomplete List of 128-bit Service Class UUIDs',
    COMPLETE_128_BIT_SERVICE_CLS_UUID_LIST: 'Complete List of 128-bit Service Class UUIDs',
    0x08: 'Shortened Local Name',
    0x09: 'Complete Local Name',
    TX_POWER_LEVEL: 'Tx Power Level',
    0x0D: 'Class of Device',
    0x0E: 'Simple Pairing Hash C(-192)',
    0x0F: 'Simple Pairing Randomizer R(-192)',
    0x10: 'Device ID or Security Manager TK Value',
    0x11: 'Security Manager Out of Band Flags',
    0x12: 'Slave Connection Interval Range',
    0x14: 'List of 16-bit Service Solicitation UUIDs',
    0x15: 'List of 128-bit Service Solicitation UUIDs',
    0x16: 'Service Data (- 16 bit UUID)',
    0x17: 'Public Target Address',
    0x18: 'Random Target Address',
    0x19: 'Appearance',
    0x1A: 'Advertising Interval',
    0x1B: 'LE Bluetooth Device Address',
    0x1C: 'LE Role',
    0x1D: 'Simple Pairing Hash C-256',
    0x0E: 'Simple Pairing Randomizer R-256',
    0x1F: 'List of 32-bit Service Solicitation UUIDs',
    0x20: 'Service Data - 32-bit UUID',
    0x21: 'Service Data - 128-bit UUID',
    0x22: 'LE Secure Connections Confirmation Value',
    0x23: 'LE Secure Connections Random Value',
    0x24: 'URI',
    0x25: 'Indoor Positioning',
    0x26: 'Transport Discovery Data',
    0x27: 'LE Supported Features',
    0x28: 'Channel Map Update Indication',
    0x29: 'PB-ADV',
    0x2A: 'Mesh Message',
    0x2B: 'Mesh Beacon',
    0x2C: 'BIGInfo',
    0x2D: 'Broadcast_Code',
    0x3D: '3D Information Data',
    0xFF: 'Manufacturer Specific Data'
}


class BlueScanner():
    def __init__(self, iface='hci0'):
        self.iface = iface
        self.devid = HCI.hcix2devid(self.iface)
