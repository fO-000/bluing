#!/usr/bin/env python3

import logging
from typing import Sequence

from pyclui import Logger, blue, green, yellow, red, \
    DEBUG, INFO, WARNING, ERROR
from xml.etree import ElementTree

from . import ServiceRecord


logger = Logger(__name__, logging.INFO)


class ObjPushServiceRecord(ServiceRecord):

    service_clses = [
        {'UUID': 0x1105, 'name': 'OBEXObjectPush'},
    ]
    
    GOEP_L2CAP_PSM = 0x0200
    SUPPORTED_FORMATS_LIST = 0x0303

    def __init__(self, record_xml:str):
        self.attrs = {
            self.GOEP_L2CAP_PSM: {
                'Name': 'GoepL2CapPsm',
                'Parser': self.pp_goep_l2cap_psm
            },
            self.SUPPORTED_FORMATS_LIST: {
                'Name': 'SupportedFormatsList',
                'Parser': self.pp_supported_formats_list
            }
            
        }
        super().__init__(record_xml)

    def pp_goep_l2cap_psm(self, val:int):
        print(green('\t0x%02X'%val))
    
    def pp_supported_formats_list(self, val:ElementTree.Element):
        """
        val - sequence
        """
        fid_descps = {
            0x01: "vCard 2.1",
            0x02: "vCard 3.0",
            0x03: "vCal 1.0",
            0x04: "iCal 2.0",
            0x05: "vNote",
            0x06: "vMessage",
            0xFF: "Any type of object"
        }
        
        format_ids = val.findall('./uint8')
        for format_id in format_ids:
            try:
                id_val = int(format_id.attrib['value'], base=16)
                print('\t0x%02x'%id_val, ': ', green(fid_descps[id_val]), sep='')
            except KeyError as e:
                print('\t0x%02x'%id_val, ': ', red('unknown'), sep='')
                continue
            except Exception as e:
                logger.warning('{}\n{}'.format(e, format_id.attrib['value']))
