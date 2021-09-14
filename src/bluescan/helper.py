#!/usr/bin/env python3

import logging
import re
import sys
# import pickle
import subprocess

from serial.tools.list_ports import comports

from pyclui import blue, green, yellow, red
from pyclui import Logger

# from . import LE_DEVS_SCAN_RESULT_CACHE


logger = Logger(__name__, logging.INFO)


# def determine_addr_type(self):
#     """For user not provide the remote LE address type."""
#     from .le_scan import LeScanner
#     try:
#         with open(LE_DEVS_SCAN_RESULT_CACHE, 'rb') as le_devs_scan_result_cache:
#             le_devs_scan_result = pickle.load(le_devs_scan_result_cache)
#             for dev_info in le_devs_scan_result.devices_info:
#                 if self.result.addr == dev_info.addr:
#                     logger.debug("determine_addr_type, {} {}".format(self.result.addr, dev_info.addr_type))
#                     return dev_info.addr_type
#     except FileNotFoundError as e:
#         logger.debug("No {} found".format(LE_DEVS_SCAN_RESULT_CACHE))
            
#     le_devs_scan_result = LeScanner(self.iface).scan_devs()
#     for dev_info in le_devs_scan_result.devices_info:
#         if self.result.addr == dev_info.addr:
#             return dev_info.addr_type

#     raise RuntimeError("Couldn't determine the LE address type. Please provide it explicitly.")


def valid_bdaddr(addr:str) -> bool:
    regexp = r'(?:[\da-fA-F]{2}:){5}[\da-fA-F]{2}'
    result = re.findall(regexp, addr)
    if len(result) == 0 or result[0] != addr:
        return False
    else:
        return True


def find_rfkill_devid(dev='hci0') -> int:
    exitcode, output = subprocess.getstatusoutput('rfkill -rno ID,DEVICE')

    for line in output.splitlines():
        id_dev = line.split()
        if len(id_dev) == 2 and id_dev[1] == dev:
            return int(id_dev[0])
        else:
            continue
    
    raise RuntimeError("Can't find the ID of %s in rfkill" % blue(dev))


def get_microbit_devpaths() -> list:
    """Get serial device path of all connected micro:bits."""
    # microbit_infos = []
    dev_paths = []
    for info in comports():
        dev_path, desc, hwid = info
        # logger.debug("info.device: {}".format(info.device))
        # logger.debug("info.name: {}".format(info.name))
        # logger.debug("info.description: {}".format(info.description))
        # logger.debug("info.hwid: {}".format(info.hwid))

        # # USB specific data
        # logger.debug("info.vid:".format(info.vid))
        # logger.debug("info.pid:".format(info.pid))
        # logger.debug("info.serial_number:".format(info.serial_number))
        # logger.debug("info.location:".format(info.location))
        # logger.debug("info.manufacturer:".format(info.manufacturer))
        # logger.debug("info.product:".format(info.product))
        # logger.debug("info.interface:".format(info.interface))


        # logger.debug(port)
        # logger.debug(desc)
        # logger.debug(hwid)
    
        if desc == "DAPLink CMSIS-DAP - mbed Serial Port":
            dev_paths.append(dev_path)
            # microbit_infos.append({
            #     'path': dev_path,
            #     'desc': desc,
            #     'hwid': hwid
            # })

    logger.debug("get_microbit_devpaths, dev_paths: {}".format(dev_paths))
    return dev_paths


def __test():
    #valid_bdaddr('11:22:33:44:55:66')
    try:
        print(find_rfkill_devid('hci0'))
    except RuntimeError as e:
        print(e)


if __name__ == '__main__':
    __test()
