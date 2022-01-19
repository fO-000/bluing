#!/usr/bin/env python3

import io
import sys
import pkg_resources
import logging
from pathlib import Path

from pyclui import Logger
from bthci import HCI

logger = Logger(__name__, logging.INFO)

PROJECT_NAME = 'bluescan'
VERSION = '0.7.1'

PKG_ROOT = Path(__file__).parent

LE_DEVS_SCAN_RESULT_CACHE = PKG_ROOT/'res'/'le_devs_scan_result.cache'

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
        try:
            self.hci_bdaddr = HCI(iface).read_bdaddr()['BD_ADDR'].upper()
        except Exception as e:
            logger.error(str(e))
            exit(1)


class ScanResult:
    def __init__(self, type: str) -> None:
        """
        type - May be 'GATT', 'LE Devices', 'BR/EDR Devices' ...
        """
        self.type = type

    def store(self):
        logger.debug("Not implemented")
