#!/usr/bin/env python3

import struct
import logging
import threading
from enum import Enum, unique

from serial import Serial
from pyclui import Logger

from .ll import pp_adv_phych_pdu

logger = Logger(__name__, logging.INFO)

# public_addrs = set()
# random_addrs = set()

@unique
class SerialEvtCodes(Enum):
    READY   = 0X00
    ERROR   = 0X01
    ACK     = 0X02
    NEW_ADV = 0X0B
    DEBUG   = 0XFF


@unique
class SerialCmdOpcodes(Enum):
    RESET     = 0X00
    ACK       = 0X02
    SNIFF_ADV = 0X0B


def serial_reset(dev:Serial):
    cmd = struct.pack('>BH', SerialCmdOpcodes.RESET.value, 0)
    dev.write(cmd)


def serial_sniff_adv(dev:Serial, channel:int):
    cmd = struct.pack('>BHB', SerialCmdOpcodes.SNIFF_ADV.value, 1, channel)
    dev.write(cmd)


class SerialEventHandler(threading.Thread):
    adv_phych_pdu_set = set()

    def __init__(self, dev:Serial, channel:int):
        logger.debug("SerialEventHandler, %s, channel: %d"%(dev.name, channel))
        super().__init__()
        self.dev = dev
        self.channel = channel
        serial_reset(self.dev)


    def run(self):
        while True:
            header = self.dev.read(3)
            evt_code, length = struct.unpack(">BH", header)
            payload = self.dev.read(length)
            
            if len(payload) > 257:
                print('Invalid payload')
                continue

            if evt_code == SerialEvtCodes.READY.value:
                logger.info("micro:bit {} < Ready -> Start".format(self.channel))
                # input("Start?")
                serial_sniff_adv(self.dev, self.channel)
            elif evt_code == SerialEvtCodes.ERROR.value:
                print('<', SerialEvtCodes.ERROR.name, payload)
            elif evt_code == SerialEvtCodes.ACK.value:
                print('<', SerialEvtCodes.ACK.name, payload)
            elif evt_code == SerialEvtCodes.DEBUG.value:
                logger.debug("micro:bit < {}".format(payload))
            elif evt_code == SerialEvtCodes.NEW_ADV.value:
                # print(SerialEvtCodes.NEW_ADV.name, payload)
                if payload not in SerialEventHandler.adv_phych_pdu_set:
                    SerialEventHandler.adv_phych_pdu_set.add(payload)
                    try:
                        pp_adv_phych_pdu(payload, self.channel)
                    except IndexError as e:
                        logger.warning("{}, channel: {}".format(e, self.channel))
                        continue

                # for addr in addrs:
                #     if addr['BD_ADDR'] not in public_addrs and addr['BD_ADDR'] not in random_addrs:
                #         print(':'.join('%02X'%b for b in addr['BD_ADDR']), addr['type'])
                #     public_addrs.add(addr['BD_ADDR']) if addr['type'] == 'public' else random_addrs.add(addr['BD_ADDR'])
            else:
                print('Unknown event 0x%02x'%evt_code, header)


if __name__ == '__main__':
    print(SerialEvtCodes.DEBUG.name)
