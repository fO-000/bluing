#!/usr/bin/env python

PKG_NAME = 'bluing'
VERSION = '0.11.0'
DEBUG_VERSION = ''


from xpycommon import py_pkg_init

locals_dict = {}
py_pkg_init(globals(), locals_dict)
LOG_LEVEL = locals_dict['LOG_LEVEL']
VERSION_STR = locals_dict['VERSION_STR']


import io
from pathlib import Path
import pkg_resources

from bthci import HCI, ControllerErrorCodes


PKG_ROOT = Path(__file__).parent
MICRO_BIT_FIRMWARE_PATH = PKG_ROOT/'res'/'micro-bit.hex'

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


class BlueScanner():
    def __init__(self, iface='hci0'):
        self.iface = iface
        self.devid = HCI.hcistr2devid(self.iface)
        
        hci = HCI(iface)
        cmd_complete = hci.read_bd_addr()
        hci.close()

        if cmd_complete.status != ControllerErrorCodes.SUCCESS:
            raise RuntimeError("hci.read_bd_addr() returned, status: 0x{:02x} - {}".format(
                cmd_complete.status, cmd_complete.status.name))
        else:
            self.hci_bd_addr = cmd_complete.bd_addr.upper()


class ScanResult:  
    def __init__(self, type: str) -> None:
        """
        type - May be 'GATT', 'LE Devices', 'BR/EDR Devices' ...
        """
        self.type = type

    def store(self):
        pass


__all__ = []
