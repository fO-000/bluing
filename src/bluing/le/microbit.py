#!/usr/bin/env python

from serial.tools.list_ports import comports
from xpycommon.log import Logger

from . import LOG_LEVEL


logger = Logger(__name__, LOG_LEVEL)


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
