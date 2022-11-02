#!/usr/bin/env python

# import pickle

from serial.tools.list_ports import comports

from xpycommon.log import Logger

from . import LOG_LEVEL

# from . import LE_DEVS_SCAN_RESULT_CACHE


logger = Logger(__name__, LOG_LEVEL)


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
