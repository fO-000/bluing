#!/usr/bin/env python3

import os
import re
import sys
import time
import struct
import subprocess

from bluetooth._bluetooth import SOL_HCI

from bluetooth._bluetooth import MSG_WAITALL

from bluetooth._bluetooth import hci_open_dev
from bluetooth._bluetooth import hci_close_dev

from bluetooth._bluetooth import HCI_FILTER
from bluetooth._bluetooth import hci_filter_new
from bluetooth._bluetooth import hci_filter_clear
from bluetooth._bluetooth import hci_filter_set_ptype
from bluetooth._bluetooth import hci_filter_set_event
from bluetooth._bluetooth import hci_filter_set_opcode

from bluetooth._bluetooth import cmd_opcode_pack
from bluetooth._bluetooth import hci_send_cmd

from bluetooth._bluetooth import OGF_LINK_CTL
from bluetooth._bluetooth import OCF_INQUIRY_CANCEL
from bluetooth._bluetooth import OCF_EXIT_PERIODIC_INQUIRY
from bluetooth._bluetooth import OCF_CREATE_CONN
from bluetooth._bluetooth import OCF_DISCONNECT
from bluetooth._bluetooth import OCF_READ_REMOTE_FEATURES
from bluetooth._bluetooth import OCF_READ_REMOTE_VERSION
OCF_READ_REMOTE_EXT_FEATURES = 0x001C
OCF_CREATE_CONN_CANCEL = 0x0008

from bluetooth._bluetooth import OGF_HOST_CTL
from bluetooth._bluetooth import OCF_RESET
from bluetooth._bluetooth import OCF_SET_EVENT_FLT
from bluetooth._bluetooth import OCF_WRITE_SCAN_ENABLE
from bluetooth._bluetooth import OCF_READ_LOCAL_NAME
from bluetooth._bluetooth import OCF_WRITE_INQUIRY_MODE
from bluetooth._bluetooth import OCF_WRITE_AUTH_ENABLE
from bluetooth._bluetooth import OCF_READ_CLASS_OF_DEV
from bluetooth._bluetooth import OCF_READ_PAGE_TIMEOUT
from bluetooth._bluetooth import OCF_WRITE_PAGE_TIMEOUT
OCF_READ_EXT_PAGE_TIMEOUT = 0x007E
OCF_WRITE_EXT_PAGE_TIMEOUT = 0x007F

from bluetooth._bluetooth import OGF_INFO_PARAM
from bluetooth._bluetooth import OCF_READ_BD_ADDR

OGF_LE_CTL = 0x08
OCF_LE_SET_ADVERTISING_PARAMETERS = 0x0006
OCF_LE_SET_ADVERTISING_DATA = 0x0008
OCF_LE_SET_SCAN_RESPONSE_DATA = 0x0009
OCF_LE_SET_ADVERTISING_ENABLE = 0x000A
OCF_LE_SET_SCAN_ENABLE = 0x000C

# EVT_*_SIZE indicates Parameter_Total_Length of the HCI event packet
from bluetooth._bluetooth import HCI_EVENT_PKT
from bluetooth._bluetooth import HCI_MAX_EVENT_SIZE # bluez set this to 260, but the max is 257
from bluetooth._bluetooth import EVT_CMD_COMPLETE
# The size of event parameters of HCI_Command_Complete event is variable, so 
# EVT_CMD_COMPLETE_SIZE only defines the fixed part, Num_HCI_Command_Packets and 
# Command_Opcode (total 3 bytes).
from bluetooth._bluetooth import EVT_CMD_COMPLETE_SIZE
from bluetooth._bluetooth import EVT_INQUIRY_COMPLETE
from bluetooth._bluetooth import EVT_CONN_COMPLETE
from bluetooth._bluetooth import EVT_CONN_COMPLETE_SIZE
from bluetooth._bluetooth import EVT_DISCONN_COMPLETE
from bluetooth._bluetooth import EVT_DISCONN_COMPLETE_SIZE
from bluetooth._bluetooth import EVT_CMD_STATUS
from bluetooth._bluetooth import EVT_CMD_STATUS_SIZE
from bluetooth._bluetooth import EVT_READ_REMOTE_FEATURES_COMPLETE
from bluetooth._bluetooth import EVT_READ_REMOTE_FEATURES_COMPLETE_SIZE
from bluetooth._bluetooth import EVT_READ_REMOTE_VERSION_COMPLETE
from bluetooth._bluetooth import EVT_READ_REMOTE_VERSION_COMPLETE_SIZE

EVT_READ_REMOTE_EXT_FEATURES_COMPLETE = 0x23
EVT_READ_REMOTE_EXT_FEATURES_COMPLETE_SIZE = 13

EVT_LE_META = 0x3E
SUBEVT_LE_ADVERTISING_REPORT = 0x02
# HCI_LE_Scan_Request_Received event 在 Bluetooth 5.0 中加入
SUBEVT_LE_SCAN_REQUEST_RECEIVED = 0x13
SUBEVT_LE_SCAN_REQUEST_RECEIVED_SIZE = 9

BD_ADDR_LEN = 6

LINK_CTRL_CMD_OGF = 0x01
HCI_CTRL_BASEBAND_CMD_OGF = 0x03


# // bluetooth/hci.h
# struct hci_filter {
#     uint32_t type_mask;
#     uint32_t event_mask[2];
#     uint16_t opcode;
# };
HCI_FILTER_SIZE = 14 # 4 + 4*2 + 2

from .ui import WARNING


class HCI:
    def __init__(self, iface='hci0'):
        self.devid = HCI.hcix2devid(iface)
        if self.devid == -1:
            raise ValueError

    @classmethod
    def hcix2devid(cls, hcix:str) -> int:
        devid = re.findall('(0)|([1-9]+)', hcix, flags=0)
        if len(devid) == 1 and ((devid[0][0] == '') ^ (devid[0][1] == '')):
            devid = int(devid[0][0]) if devid[0][0] != '' else int(devid[0][1])
        else:
            devid = -1

        return devid

    ################### Link Control Commands #################################
    def inquiry_cancel(self) -> dict:
        '''
        Return -- {
            'Num_HCI_Command_Packets': int,
            'Command_Opcode': int,
            'Status': int
        }
        '''
        dd = hci_open_dev(self.devid)

        flt = hci_filter_new()
        hci_filter_set_ptype(flt, HCI_EVENT_PKT)
        hci_filter_set_event(flt, EVT_CMD_COMPLETE)
        hci_filter_set_opcode(
            flt, cmd_opcode_pack(OGF_LINK_CTL, OCF_INQUIRY_CANCEL))
        dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

        hci_send_cmd(dd, OGF_LINK_CTL, OCF_INQUIRY_CANCEL)
        event_params = dd.recv(3+EVT_CMD_COMPLETE_SIZE+1)[3:]
        num_hci_cmd_pkts, cmd_opcode, status = struct.unpack('<BHB', event_params)
        event_params = {
            'Num_HCI_Command_Packets': num_hci_cmd_pkts,
            'Command_Opcode': cmd_opcode,
            'Status': status
        }
    
        hci_close_dev(dd.fileno())
        return event_params

    def exit_periodic_inquiry_mode(self) -> dict:
        '''
        Return -- {
            'Num_HCI_Command_Packets': int,
            'Command_Opcode': int,
            'Status': int
        }
        '''
        dd = hci_open_dev(self.devid)

        flt = hci_filter_new()
        hci_filter_set_ptype(flt, HCI_EVENT_PKT)
        hci_filter_set_event(flt, EVT_CMD_COMPLETE)
        hci_filter_set_opcode(
            flt, cmd_opcode_pack(OGF_LINK_CTL, OCF_EXIT_PERIODIC_INQUIRY))
        dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

        hci_send_cmd(dd, OGF_LINK_CTL, OCF_EXIT_PERIODIC_INQUIRY)

        event_params = dd.recv(3+EVT_CMD_COMPLETE_SIZE+1)[3:]
        num_hci_cmd_pkts, cmd_opcode, status = struct.unpack('<BHB', event_params)
        event_params = {
            'Num_HCI_Command_Packets': num_hci_cmd_pkts,
            'Command_Opcode': cmd_opcode,
            'Status': status
        }
        
        hci_close_dev(dd.fileno())
        return status

    def create_connection(self, cmd_params:dict):
        '''
        cmd_params -- {
                          'BD_ADDR': str,
                          'Packet_Type': int,
                          'Page_Scan_Repetition_Mode': ,
                          'Reserved': ,
                          'Clock_Offset': ,
                          'Allow_Role_Switch':
                      }
        '''
        dd = hci_open_dev(self.devid)

        bin_cmd_params = bytes.fromhex(
            cmd_params['BD_ADDR'].replace(':', ''))[::-1] + \
            cmd_params['Packet_Type'].to_bytes(2, 'little') + \
            cmd_params['Page_Scan_Repetition_Mode'].to_bytes(1, 'little') + \
            cmd_params['Reserved'].to_bytes(1, 'little') + \
            cmd_params['Clock_Offset'].to_bytes(2, 'little') + \
            cmd_params['Allow_Role_Switch'].to_bytes(1, 'little')
        
        flt = hci_filter_new()
        hci_filter_set_ptype(flt, HCI_EVENT_PKT)
        hci_filter_set_event(flt, EVT_CONN_COMPLETE)
        dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

        hci_send_cmd(dd, OGF_LINK_CTL, OCF_CREATE_CONN, bin_cmd_params)

        while True:
            event_params = dd.recv(3+EVT_CONN_COMPLETE_SIZE)[3:]
            status, conn_handle, bd_addr, link_type, encrypt_enabled = \
                struct.unpack('<BH6sBB', event_params)
            event_params = {
                'Status': status,
                'Connection_Handle': conn_handle,
                'BD_ADDR': ':'.join(['%02x'%b for b in bd_addr[::-1]]),
                'Link_Type': link_type,
                'Encryption_Enabled': encrypt_enabled,
            }

            if event_params['BD_ADDR'].lower() == cmd_params['BD_ADDR'].lower():
                break
            else:
                print(WARNING, 'Another HCI_Connection_Complete event detected', event_params)

        hci_close_dev(dd.fileno())
        return event_params
        
    def disconnect(self, cmd_params:dict) -> dict:
        '''
        cmd_params -- {
            'Connection_Handle': int, 2 bytes,
            'Reason': int, 1 bytes
        }
        '''
        dd = hci_open_dev(self.devid)
        
        flt = hci_filter_new()
        hci_filter_clear(flt)
        hci_filter_set_ptype(flt, HCI_EVENT_PKT)
        hci_filter_set_event(flt, EVT_DISCONN_COMPLETE)
        dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

        bin_cmd_params = cmd_params['Connection_Handle'].to_bytes(2, 'little') + \
            cmd_params['Reason'].to_bytes(1, 'little')

        hci_send_cmd(dd, OGF_LINK_CTL, OCF_DISCONNECT, bin_cmd_params)

        # Receive and exclude HCI packet type (1 B)
        event_params = dd.recv(3+EVT_DISCONN_COMPLETE_SIZE)[3:] 
        status, conn_handle, reason, = struct.unpack(
            '<BHB', event_params)

        event_params = {
            'Status': status,
            'Connection_Handle': conn_handle,
            'Reason': reason
        }

        hci_close_dev(dd.fileno())
        return event_params


    def create_connection_cancel(self, cmd_params:dict) -> dict:
        '''
        cmd_params -- {
            'BD_ADDR': str
        }
        '''
        dd = hci_open_dev(self.devid)

        bin_cmd_params = bytes.fromhex(cmd_params['BD_ADDR'].replace(':', '')[::-1])

        flt = hci_filter_new()
        hci_filter_set_ptype(flt, HCI_EVENT_PKT)
        hci_filter_set_event(flt, EVT_CMD_COMPLETE)
        hci_filter_set_opcode(
            flt, cmd_opcode_pack(OGF_LINK_CTL, OCF_CREATE_CONN_CANCEL))
        dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

        hci_send_cmd(dd, OGF_LINK_CTL, OCF_CREATE_CONN_CANCEL, bin_cmd_params)
        
        event_params = dd.recv(3+EVT_CMD_COMPLETE_SIZE+7)[3:]
        num_hci_cmd_pkts, cmd_opcode, status, \
            bdaddr = struct.unpack('<BHB6s', event_params)

        hci_close_dev(dd.fileno())
        return event_params


    def read_remote_supported_features(self, cmd_params:dict) -> dict:
        '''
        cmd_params -- {'Connection_Handle': 0x0000 to 0x0EFF}
        '''
        dd = hci_open_dev(self.devid)

        bin_cmd_params = cmd_params['Connection_Handle'].to_bytes(2, 'little')

        flt = hci_filter_new()
        hci_filter_set_ptype(flt, HCI_EVENT_PKT)
        hci_filter_set_event(flt, EVT_READ_REMOTE_FEATURES_COMPLETE)
        dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

        hci_send_cmd(dd, OGF_LINK_CTL, OCF_READ_REMOTE_FEATURES, 
            bin_cmd_params)

        while True:
            event_params = dd.recv(3+EVT_READ_REMOTE_FEATURES_COMPLETE_SIZE)[3:]
            status, conn_handle, lmp_features = struct.unpack('<BH8s', event_params)
            event_params = {
                'Status': status,
                'Connection_Handle': conn_handle,
                'LMP_Features': lmp_features
            }

            if event_params['Connection_Handle'] == cmd_params['Connection_Handle']:
                break

        hci_close_dev(dd.fileno())
        return event_params


    def read_remote_extended_features(self, cmd_params:dict) -> dict:
        '''
        cmd_params -- {
                          'Connection_Handle': 0x0000 to 0x0EFF,
                          'Page_Number': int
                      }
        '''
        dd = hci_open_dev(self.devid)

        bin_cmd_params = cmd_params[
            'Connection_Handle'].to_bytes(2, 'little') + \
            cmd_params['Page_Number'].to_bytes(1, 'little')

        flt = hci_filter_new()
        hci_filter_set_ptype(flt, HCI_EVENT_PKT)
        hci_filter_set_event(flt, EVT_READ_REMOTE_EXT_FEATURES_COMPLETE)
        dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

        hci_send_cmd(dd, OGF_LINK_CTL, OCF_READ_REMOTE_EXT_FEATURES, 
            bin_cmd_params)

        while True:
            event_params = dd.recv(3 + \
                EVT_READ_REMOTE_EXT_FEATURES_COMPLETE_SIZE)[3:]
            status, conn_handle, page_num, max_page_num, ext_lmp_features = \
                struct.unpack('<BHBB8s', event_params)
            event_params = {
                'Status': status,
                'Connection_Handle': conn_handle,
                'Page_Number': page_num,
                'Maximum_Page_Number': max_page_num,
                'Extended_LMP_Features': ext_lmp_features
            }

            if event_params['Connection_Handle'] == cmd_params['Connection_Handle'] and \
                event_params['Page_Number'] == cmd_params['Page_Number']:
                break

        hci_close_dev(dd.fileno())
        return event_params


    def read_remote_version_information(self, cmd_params:dict) -> dict:
        '''
        cmd_params -- {
            'Connection_Handle': 0x0000
        }
        '''
        dd = hci_open_dev(self.devid)

        bin_cmd_params = cmd_params['Connection_Handle'].to_bytes(2, 'little')

        flt = hci_filter_new()
        hci_filter_set_ptype(flt, HCI_EVENT_PKT)
        hci_filter_set_event(flt, EVT_READ_REMOTE_VERSION_COMPLETE)
        dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

        hci_send_cmd(dd, OGF_LINK_CTL, OCF_READ_REMOTE_VERSION, bin_cmd_params)

        while True:
            event_params = dd.recv(3 + \
                EVT_READ_REMOTE_VERSION_COMPLETE_SIZE)[3:]
            status, conn_handle, ver, manufacturer_name, subver = \
                struct.unpack('<BHBHH', event_params)
            event_params = {
                'Status': status,
                'Connection_Handle': conn_handle,
                'Version': ver,
                'Manufacturer_Name': manufacturer_name,
                'Subversion': subver
            }

            if event_params['Connection_Handle'] == cmd_params['Connection_Handle']:
                break

        hci_close_dev(dd.fileno())
        return event_params

    ################## Controller & Baseband Commands #########################
    def reset(self) -> dict:
        dd = hci_open_dev(self.devid)

        flt = hci_filter_new()
        hci_filter_set_ptype(flt, HCI_EVENT_PKT)
        hci_filter_set_event(flt, EVT_CMD_COMPLETE)
        hci_filter_set_opcode(flt, cmd_opcode_pack(OGF_HOST_CTL, OCF_RESET))
        dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

        hci_send_cmd(dd, OGF_HOST_CTL, OCF_RESET)
        event_params = dd.recv(3+EVT_CMD_COMPLETE_SIZE+1)[3:]
        num_hci_cmd_pkts, cmd_opcode, status = struct.unpack('<BHB', event_params)
        event_params = {
            'Num_HCI_Command_Packets': num_hci_cmd_pkts,
            'Command_Opcode': cmd_opcode,
            'Status': status
        }
    
        hci_close_dev(dd.fileno())
        return event_params


    def write_scan_enable(self, cmd_params={'Scan_Enable': 0x00}) -> dict:
        dd = hci_open_dev(self.devid)

        bin_cmd_params = cmd_params['Scan_Enable'].to_bytes(1, 'little')

        flt = hci_filter_new()
        hci_filter_set_ptype(flt, HCI_EVENT_PKT)
        hci_filter_set_event(flt, EVT_CMD_COMPLETE)
        hci_filter_set_opcode(
            flt, cmd_opcode_pack(OGF_HOST_CTL, OCF_WRITE_SCAN_ENABLE))
        dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

        hci_send_cmd(dd, OGF_HOST_CTL, OCF_WRITE_SCAN_ENABLE, bin_cmd_params)
        event_params = dd.recv(3+EVT_CMD_COMPLETE_SIZE+1)[3:]
        num_hci_cmd_pkts, cmd_opcode, status = struct.unpack('<BHB', event_params)
        event_params = {
            'Num_HCI_Command_Packets': num_hci_cmd_pkts,
            'Command_Opcode': cmd_opcode,
            'Status': status
        }

        hci_close_dev(dd.fileno())
        return event_params


    def set_event_filter(self, cmd_params:dict) -> dict:
        '''A little complicated. see the core specification 
        BLUETOOTH CORE SPECIFICATION Version 5.2 | Vol 4, Part E page 2078. 
        Only support Filter_Type = 0x00 now.
        '''
        dd = hci_open_dev(self.devid)

        bin_cmd_params = cmd_params['Filter_Type'].to_bytes(1, 'little')

        flt = hci_filter_new()
        hci_filter_set_ptype(flt, HCI_EVENT_PKT)
        hci_filter_set_event(flt, EVT_CMD_COMPLETE)
        hci_filter_set_opcode(flt, cmd_opcode_pack(OGF_HOST_CTL, OCF_SET_EVENT_FLT))
        dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

        hci_send_cmd(dd, OGF_HOST_CTL, OCF_SET_EVENT_FLT, bin_cmd_params)
        event_params = dd.recv(3+EVT_CMD_COMPLETE_SIZE+1)[3:]
        num_hci_cmd_pkts, cmd_opcode, status = struct.unpack('<BHB', event_params)
        event_params = {
            'Num_HCI_Command_Packets': num_hci_cmd_pkts,
            'Command_Opcode': cmd_opcode,
            'Status': status
        }

        hci_close_dev(dd.fileno())
        return event_params


    def read_local_name(self) -> dict:
        dd = hci_open_dev(self.devid)

        flt = hci_filter_new()
        hci_filter_set_ptype(flt, HCI_EVENT_PKT)
        hci_filter_set_event(flt, EVT_CMD_COMPLETE)
        hci_filter_set_opcode(
            flt, cmd_opcode_pack(OGF_HOST_CTL, OCF_READ_LOCAL_NAME))
        dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

        hci_send_cmd(dd, OGF_HOST_CTL, OCF_READ_LOCAL_NAME)

        event_params = dd.recv(3+EVT_CMD_COMPLETE_SIZE+249)[3:]
        num_hci_cmd_pkts, cmd_opcode, status, local_name = struct.unpack('<BHB248s', event_params)
        event_params = {
            'Num_HCI_Command_Packets': num_hci_cmd_pkts,
            'Command_Opcode': cmd_opcode,
            'Status': status,
            'Local_Name': local_name.decode()
        }

        hci_close_dev(dd.fileno())
        return event_params


    def write_inquiry_mode(self, cmd_params={'Inquiry_Mode': 0x00}) -> dict:
        dd = hci_open_dev(self.devid)

        bin_cmd_params = cmd_params['Inquiry_Mode'].to_bytes(1, 'little')

        flt = hci_filter_new()
        hci_filter_set_ptype(flt, HCI_EVENT_PKT)
        hci_filter_set_event(flt, EVT_CMD_COMPLETE)
        hci_filter_set_opcode(
            flt, cmd_opcode_pack(OGF_HOST_CTL, OCF_WRITE_INQUIRY_MODE))
        dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

        hci_send_cmd(dd, OGF_HOST_CTL, OCF_WRITE_INQUIRY_MODE, bin_cmd_params)
        event_params = dd.recv(3+EVT_CMD_COMPLETE_SIZE+1)[3:]
        num_hci_cmd_pkts, cmd_opcode, status = struct.unpack('<BHB', event_params)
        event_params = {
            'Num_HCI_Command_Packets': num_hci_cmd_pkts,
            'Command_Opcode': cmd_opcode,
            'Status': status
        }
        
        hci_close_dev(dd.fileno())
        return event_params


    def read_page_timeout(self) -> dict:
        dd = hci_open_dev(self.devid)

        flt = hci_filter_new()
        hci_filter_set_ptype(flt, HCI_EVENT_PKT)
        hci_filter_set_event(flt, EVT_CMD_COMPLETE)
        hci_filter_set_opcode(
            flt, cmd_opcode_pack(OGF_HOST_CTL, OCF_READ_PAGE_TIMEOUT))
        dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

        hci_send_cmd(dd, OGF_HOST_CTL, OCF_READ_PAGE_TIMEOUT)
        event_params = dd.recv(3+EVT_CMD_COMPLETE_SIZE+3)[3:]
        num_hci_cmd_pkts, cmd_opcode, status, page_timeout = struct.unpack('<BHBH', event_params)
        event_params = {
            'Num_HCI_Command_Packets': num_hci_cmd_pkts,
            'Command_Opcode': cmd_opcode,
            'Status': status,
            'Page_Timeout': page_timeout
        }

        hci_close_dev(dd.fileno())
        return event_params


    def write_page_timeout(self, cmd_params={'Page_Timeout': 0x2000}) -> dict:
        dd = hci_open_dev(self.devid)

        bin_cmd_params = cmd_params['Page_Timeout'].to_bytes(2, 'little')

        flt = hci_filter_new()
        hci_filter_set_ptype(flt, HCI_EVENT_PKT)
        hci_filter_set_event(flt, EVT_CMD_COMPLETE)
        hci_filter_set_opcode(
            flt, cmd_opcode_pack(OGF_HOST_CTL, OCF_WRITE_PAGE_TIMEOUT))
        dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

        hci_send_cmd(dd, OGF_HOST_CTL, OCF_WRITE_PAGE_TIMEOUT, bin_cmd_params)
        event_params = dd.recv(3+EVT_CMD_COMPLETE_SIZE+3)[3:]
        num_hci_cmd_pkts, cmd_opcode, status = struct.unpack('<BHB', event_params)
        event_params = {
            'Num_HCI_Command_Packets': num_hci_cmd_pkts,
            'Command_Opcode': cmd_opcode,
            'Status': status
        }

        hci_close_dev(dd.fileno())
        return event_params


    def write_authentication_enable(self, cmd_params={'Authentication_Enable': 0x00}) -> dict:
        dd = hci_open_dev(self.devid)

        bin_cmd_params = cmd_params['Authentication_Enable'].to_bytes(1, 'little')

        flt = hci_filter_new()
        hci_filter_set_ptype(flt, HCI_EVENT_PKT)
        hci_filter_set_event(flt, EVT_CMD_COMPLETE)
        hci_filter_set_opcode(
            flt, cmd_opcode_pack(OGF_HOST_CTL, OCF_WRITE_AUTH_ENABLE))
        dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

        hci_send_cmd(dd, OGF_HOST_CTL, OCF_WRITE_AUTH_ENABLE, bin_cmd_params)
        event_params = dd.recv(3+EVT_CMD_COMPLETE_SIZE+3)[3:]
        num_hci_cmd_pkts, cmd_opcode, status = struct.unpack('<BHB', event_params)
        event_params = {
            'Num_HCI_Command_Packets': num_hci_cmd_pkts,
            'Command_Opcode': cmd_opcode,
            'Status': status
        }

        hci_close_dev(dd.fileno())
        return event_params


    def read_class_of_device(self) -> dict:
        dd = hci_open_dev(self.devid)

        flt = hci_filter_new()
        hci_filter_set_ptype(flt, HCI_EVENT_PKT)
        hci_filter_set_event(flt, EVT_CMD_COMPLETE)
        hci_filter_set_opcode(
            flt, cmd_opcode_pack(OGF_HOST_CTL, OCF_READ_CLASS_OF_DEV))
        dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

        hci_send_cmd(dd, OGF_HOST_CTL, OCF_READ_CLASS_OF_DEV)

        event_params = dd.recv(3+HCI_MAX_EVENT_SIZE)[3:]
        num_hci_cmd_pkts, cmd_opcode, status, cod = struct.unpack('<BHB3s', event_params)
        event_params = {
            'Num_HCI_Command_Packets': num_hci_cmd_pkts,
            'Command_Opcode': cmd_opcode,
            'Status': status,
            'Class_Of_Device': cod[::-1]
        }

        hci_close_dev(dd.fileno())
        return event_params


    def read_extended_page_timeout(self):
        dd = hci_open_dev(self.devid)

        flt = hci_filter_new()
        hci_filter_set_ptype(flt, HCI_EVENT_PKT)
        hci_filter_set_event(flt, EVT_CMD_COMPLETE)
        hci_filter_set_opcode(
            flt, cmd_opcode_pack(OGF_HOST_CTL, OCF_READ_EXT_PAGE_TIMEOUT))
        dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

        hci_send_cmd(dd, OGF_HOST_CTL, OCF_READ_EXT_PAGE_TIMEOUT)

        event_params = dd.recv(3+EVT_CMD_COMPLETE_SIZE+3)[3:]
        num_hci_cmd_pkts, cmd_opcode, status, \
           ext_page_timeout = struct.unpack('<BHBH', event_params)
        event_params = {
            'Num_HCI_Command_Packets': num_hci_cmd_pkts,
            'Command_Opcode': cmd_opcode,
            'Status': status,
            'Extended_Page_Timeout': ext_page_timeout
        }

        hci_close_dev(dd.fileno())
        return event_params


    #################### Informational Parameters ###############################
    def read_bd_addr(self) -> dict:
        r"""'Return BD_ADDR string "XX:XX:XX:XX:XX:XX'"""
        dd = hci_open_dev(self.devid)

        flt = hci_filter_new()
        hci_filter_set_ptype(flt, HCI_EVENT_PKT)
        hci_filter_set_event(flt, EVT_CMD_COMPLETE)
        hci_filter_set_opcode(
            flt, cmd_opcode_pack(OGF_INFO_PARAM, OCF_READ_BD_ADDR))
        dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

        hci_send_cmd(dd, OGF_INFO_PARAM, OCF_READ_BD_ADDR)
        event_params = dd.recv(HCI_MAX_EVENT_SIZE)[3:]
        num_hci_cmd_pkts, cmd_opcode, status, bd_addr = struct.unpack("<BHB6s", event_params)
        bd_addr = ["%02X"%b for b in bd_addr]
        bd_addr.reverse()
        event_params = {
            'Num_HCI_Command_Packets': num_hci_cmd_pkts,
            'Command_Opcode': cmd_opcode,
            'Status': status,
            'BD_ADDR': ':'.join(bd_addr)
        }
        
        hci_close_dev(dd.fileno())
        return event_params


    #################### LE Controller Commands ###############################
    def le_set_advertising_parameters(self, cmd_params={
        'Advertising_Interval_Min': 0x0800, 
        'Advertising_Interval_Max': 0x0800,
        'Advertising_Type': 0x00, # ADV_IND
        'Own_Address_Type': 0x00, # Public Device Address
        'Peer_Address_Type': 0x00, # Public Device Address
        'Peer_Address': bytes(6),
        'Advertising_Channel_Map': 0x07, # 37, 38, 39
        'Advertising_Filter_Policy': 0x00 # Process scan and connection requests from all devices
    }) -> dict:
        dd = hci_open_dev(self.devid)
        
        bin_cmd_params = cmd_params['Advertising_Interval_Min'].to_bytes(2, 'little') + \
            cmd_params['Advertising_Interval_Max'].to_bytes(2, 'little') + \
            cmd_params['Advertising_Type'].to_bytes(1, 'little') + \
            cmd_params['Own_Address_Type'].to_bytes(1, 'little') + \
            cmd_params['Peer_Address_Type'].to_bytes(1, 'little') + \
            cmd_params['Peer_Address'][::-1] + \
            cmd_params['Advertising_Channel_Map'].to_bytes(1, 'little') + \
            cmd_params['Advertising_Filter_Policy'].to_bytes(1, 'little')
        
        flt = hci_filter_new()
        hci_filter_set_ptype(flt, HCI_EVENT_PKT)
        hci_filter_set_event(flt, EVT_CMD_COMPLETE)
        hci_filter_set_opcode(
            flt, cmd_opcode_pack(OGF_LE_CTL, OCF_LE_SET_ADVERTISING_PARAMETERS))
        dd.setsockopt(SOL_HCI, HCI_FILTER, flt)
        
        hci_send_cmd(dd, OGF_LE_CTL, OCF_LE_SET_ADVERTISING_PARAMETERS, bin_cmd_params)
        event_params = dd.recv(3+EVT_CMD_COMPLETE_SIZE+1)[3:]
        num_hci_cmd_pkts, cmd_opcode, status = struct.unpack('<BHB', event_params)
        event_params = {
            'Num_HCI_Command_Packets': num_hci_cmd_pkts,
            'Command_Opcode': cmd_opcode,
            'Status': status
        }
    
        hci_close_dev(dd.fileno())
        return event_params


    def le_set_advertising_data(self, cmd_params={
        'Advertising_Data_Length': 0x1f,
        'Advertising_Data': bytes(0x1f)}) -> dict:
        dd = hci_open_dev(self.devid)

        bin_cmd_params = cmd_params['Advertising_Data_Length'].to_bytes(1, 'little') + \
            cmd_params['Advertising_Data']

        flt = hci_filter_new()
        hci_filter_set_ptype(flt, HCI_EVENT_PKT)
        hci_filter_set_event(flt, EVT_CMD_COMPLETE)
        hci_filter_set_opcode(
            flt, cmd_opcode_pack(OGF_LE_CTL, OCF_LE_SET_ADVERTISING_DATA))
        dd.setsockopt(SOL_HCI, HCI_FILTER, flt)
        
        hci_send_cmd(dd, OGF_LE_CTL, OCF_LE_SET_ADVERTISING_DATA, bin_cmd_params)
        event_params = dd.recv(3+EVT_CMD_COMPLETE_SIZE+1)[3:]
        num_hci_cmd_pkts, cmd_opcode, status = struct.unpack('<BHB', event_params)
        event_params = {
            'Num_HCI_Command_Packets': num_hci_cmd_pkts,
            'Command_Opcode': cmd_opcode,
            'Status': status
        }

        hci_close_dev(dd.fileno())
        return event_params


    def le_set_scan_response_data(self, cmd_params={
        'Scan_Response_Data_Length': 0x1f,
        'Scan_Response_Data': bytes(0x1f)}) -> dict:
        dd = hci_open_dev(self.devid)

        bin_cmd_params = cmd_params['Scan_Response_Data_Length'].to_bytes(1, 'little') + \
            cmd_params['Scan_Response_Data']

        flt = hci_filter_new()
        hci_filter_set_ptype(flt, HCI_EVENT_PKT)
        hci_filter_set_event(flt, EVT_CMD_COMPLETE)
        hci_filter_set_opcode(
            flt, cmd_opcode_pack(OGF_LE_CTL, OCF_LE_SET_SCAN_RESPONSE_DATA))
        dd.setsockopt(SOL_HCI, HCI_FILTER, flt)
        
        hci_send_cmd(dd, OGF_LE_CTL, OCF_LE_SET_SCAN_RESPONSE_DATA, bin_cmd_params)
        event_params = dd.recv(3+EVT_CMD_COMPLETE_SIZE+1)[3:]
        num_hci_cmd_pkts, cmd_opcode, status = struct.unpack('<BHB', event_params)
        event_params = {
            'Num_HCI_Command_Packets': num_hci_cmd_pkts,
            'Command_Opcode': cmd_opcode,
            'Status': status
        }

        hci_close_dev(dd.fileno())
        return event_params


    def le_set_advertising_enable(self, cmd_params={'Advertising_Enable': 0x00}) -> dict:
        dd = hci_open_dev(self.devid)

        bin_cmd_params = cmd_params['Advertising_Enable'].to_bytes(1, 'little')

        flt = hci_filter_new()
        hci_filter_set_ptype(flt, HCI_EVENT_PKT)
        hci_filter_set_event(flt, EVT_CMD_COMPLETE)
        hci_filter_set_opcode(
            flt, cmd_opcode_pack(OGF_LE_CTL, OCF_LE_SET_ADVERTISING_ENABLE))
        dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

        hci_send_cmd(dd, OGF_LE_CTL, OCF_LE_SET_ADVERTISING_ENABLE, bin_cmd_params)
        event_params = dd.recv(3+EVT_CMD_COMPLETE_SIZE+1)[3:]
        num_hci_cmd_pkts, cmd_opcode, status = struct.unpack('<BHB', event_params)
        event_params = {
            'Num_HCI_Command_Packets': num_hci_cmd_pkts,
            'Command_Opcode': cmd_opcode,
            'Status': status
        }
        
        hci_close_dev(dd.fileno())
        return event_params


    def le_set_scan_enable(self, cmd_params:dict):
        '''
        cmd_params -- {
                          'LE_Scan_Enable': int 0 or 1,
                          'Filter_Duplicates': int 0 or 1
                      }
        '''
        dd = hci_open_dev(self.devid)

        bin_cmd_params = cmd_params['LE_Scan_Enable'].to_bytes(1, 'little') + \
            cmd_params['Filter_Duplicates'].to_bytes(1, 'little')

        flt = hci_filter_new()
        hci_filter_set_ptype(flt, HCI_EVENT_PKT)
        hci_filter_set_event(flt, EVT_CMD_COMPLETE)
        hci_filter_set_opcode(
            flt, cmd_opcode_pack(OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE))
        dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

        hci_send_cmd(dd, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, bin_cmd_params)
        event_params = dd.recv(3+EVT_CMD_COMPLETE_SIZE+1)[3:]
        num_hci_cmd_pkts, cmd_opcode, status = struct.unpack('<BHB', event_params)
        event_params = {
            'Num_HCI_Command_Packets': num_hci_cmd_pkts,
            'Command_Opcode': cmd_opcode,
            'Status': status
        }

        if event_params['Status'] != 0x00:
            raise RuntimeError(
                'Status of HCI_LE_Set_Scan_Enable command: 0x%02x'%event_params['Status'])

        if not cmd_params['LE_Scan_Enable']:
            return event_params

        flt = hci_filter_new()
        hci_filter_set_ptype(flt, HCI_EVENT_PKT)
        hci_filter_set_event(flt, EVT_LE_META)
        dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

        while True:
            event_params = dd.recv(3+HCI_MAX_EVENT_SIZE)[3:]
            if event_params[0] != SUBEVT_LE_ADVERTISING_REPORT:
                continue

            num_reports = event_params[1]
            if num_reports == 1:
                event_type, addr_type, addr = struct.unpack('<BB6s', 
                    event_params[2:10])
                print('Event_Type:', event_type)
                print('Address_Type:', addr_type)
                print('Address:', addr)

        hci_close_dev(dd.fileno())
        return event_params
    
    
    def le_create_connection(self, cmd_params:dict) -> dict:
        '''
        cmd_params -- {
            'LE_Scan_Interval': ,
            'LE_Scan_Window': ,
            'Initiator_Filter_Policy': ,
            'Peer_Address_Type': ,
            'Peer_Address': ,
            'Own_Address_Type': ,
            'Connection_Interval_Min': ,
            'Connection_Interval_Max': ,
            'Connection_Latency': ,
            'Supervision_Timeout': ,
            'Min_CE_Length': ,
            'Max_CE_Lengt':
        }
        '''
        pass
        

def hci_write_local_name(params:bytes, iface='hci0'):
    ogf = HCI_CTRL_BASEBAND_CMD_OGF
    ocf = 0x0013

    params = ' '.join([hex(b) for b in params])
    hcitool_cmd = gen_hcitool_cmd(ogf, ocf, params, iface)

    print(subprocess.getoutput(hcitool_cmd))


def hci_link_Key_request_reply(bd_addr:str, link_key:str, iface='hci0'):
    '''BLUETOOTH CORE SPECIFICATION Version 5.1 | Vol 2, Part E page 825, 7.1.10 Link Key Request Reply command'''
    ogf = LINK_CTRL_CMD_OGF
    ocf = 0x000B

    # HCI command parameter using litten-endian
    bd_addr = ' '.join(['0x' + e for e in bd_addr.split(':')[::-1]])
    print(bd_addr)
    link_key = ' '.join([hex(b) for b in bytes.fromhex(link_key)])
    print(link_key)

    params = bd_addr + ' ' + link_key
    hcitool_cmd = gen_hcitool_cmd(ogf, ocf, params, iface)

    print(subprocess.getoutput(hcitool_cmd))


def hci_read_stored_link_key(bd_addr='00:00:00:00:00:00', read_all_flag=0x01, iface='hci0'):
    '''BLUETOOTH CORE SPECIFICATION Version 5.1 | Vol 2, Part E page 966, 7.3.8 Read Stored Link Key command'''
    ogf = HCI_CTRL_BASEBAND_CMD_OGF
    ocf = 0x000D
    
    bd_addr = ' '.join(['0x' + e for e in bd_addr.split(':')[::-1]])
    read_all_flag = hex(read_all_flag)

    params = ' '.join([bd_addr, read_all_flag])

    hcitool_cmd = gen_hcitool_cmd(ogf, ocf, params, iface)
    print(subprocess.getoutput(hcitool_cmd))


def hci_write_stored_link_key(bd_addrs: list, link_keys:list, iface='hci0'):
    '''BLUETOOTH CORE SPECIFICATION Version 5.1 | Vol 2, Part E page 968, 7.3.9 Write Stored Link Key command.'''
    ogf = HCI_CTRL_BASEBAND_CMD_OGF
    ocf = 0x0011

    if (len(bd_addrs) != len(link_keys)):
        print("[ERROR] BD_ADDRs and Link Keys is not one-to-one correspondence.")
        return False
    
    num_keys_to_write = len(link_keys)

    temp = ''
    for bd_addr in bd_addrs:
        temp +=  ' '.join(
            ['0x' + e for e in bd_addr.split(':')[::-1]]
    ) + ' '
    bd_addrs = temp
    print(bd_addrs)

    temp = ''
    for link_key in link_keys:
        temp += ' '.join(
        [hex(b) for b in bytes.fromhex(link_key)]
    ) + ' '
    link_keys = temp
    print(link_keys)

    params = hex(num_keys_to_write) + ' ' + bd_addrs + ' ' \
        + link_keys

    hcitool_cmd = gen_hcitool_cmd(ogf, ocf, params, iface)
    print(subprocess.getoutput(hcitool_cmd))


def hci_delete_stored_link_key(bd_addr='00:00:00:00:00:00', del_all_flag=0x01, iface='hci0'):
    "BLUETOOTH CORE SPECIFICATION Version 5.1 | Vol 2, Part E page 970, 7.3.10 Delete Stored Link Key command"
    ogf = HCI_CTRL_BASEBAND_CMD_OGF
    ocf = 0x0012

    bd_addr = ' '.join(['0x' + e for e in bd_addr.split(':')[::-1]])
    del_all_flag = hex(del_all_flag)
    params = ' '.join([bd_addr, del_all_flag])

    hcitool_cmd = gen_hcitool_cmd(ogf, ocf, params)
    print(subprocess.getoutput(hcitool_cmd))


def hci_write_simple_pairing_mode(simple_pairing_mode=0x00, iface='hci0'):
    '''7.3.59 Write Simple Pairing Mode command'''
    ogf = HCI_CTRL_BASEBAND_CMD_OGF
    ocf = 0x0056

    simple_pairing_mode = hex(simple_pairing_mode)
    params = simple_pairing_mode

    hcitool_cmd = gen_hcitool_cmd(ogf, ocf, params)
    print(subprocess.getoutput(hcitool_cmd))


def gen_hcitool_cmd(ogf:int, ocf:int, params:str, iface='hci0') -> str:
    '''构造执行任意 HCI command 的 hcitool 命令。'''
    cmd_args = ['hcitool', '-i', iface, 'cmd', hex(ogf), hex(ocf), params]
    cmd = ' '.join(cmd_args)
    #print('[DEBUG]', cmd)
    return cmd


class __Test:
    @classmethod
    def scan_undiscoverable_dev(cls):
        import multiprocessing

        #hci_read_page_timeout()
        #hci_write_page_timeout(0x0200) # 0x0500 较稳定
        #hci_read_page_timeout()

        # p1 = multiprocessing.Process(target=job,args=(1,2))

        # range(, )

        #hci_create_connection('3C:28:6D:E0:58:F7')
        for i in range(0x000000, 0x100000):
            addr = '3c:28:6d:'+':'.join('%02x'%b for b in i.to_bytes(3, 'big', signed=False))
            print(addr)
            #print('HCI connect', addr)
            #status, bdaddr = hci_create_connection(addr)
            #hci_create_connection(addr)
            time.sleep(0.5)
            # if status == 0:
            #     print(status, bdaddr)

    @classmethod
    def pp_le_scanner_addr(cls):
        hci = HCI('hci0')
        hci.le_set_advertising_parameters()

        bytes.fromhex('020106020aeb0303ff00')+bytes(0x1f-10)
        hci.le_set_advertising_data({
            'Advertising_Data_Length': 0x12,
            'Advertising_Data': bytes.fromhex('020106020aeb0303ff000709424c45435446')+bytes(0x1f-0x12)
        })
        
        hci.le_set_scan_response_data({
            'Scan_Response_Data_Length': 0x0a,
            'Scan_Response_Data': bytes.fromhex('020106020aeb0303ff00')+bytes(0x1f-0x0a)
        })

        hci.le_set_advertising_enable({'Advertising_Enable': 0x01})

        dd = hci_open_dev(0)

        flt = hci_filter_new()
        hci_filter_set_ptype(flt, HCI_EVENT_PKT)
        hci_filter_set_event(flt, EVT_LE_META)
        dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

        while True:
            event_params = dd.recv(3+SUBEVT_LE_SCAN_REQUEST_RECEIVED_SIZE)[3:]
            if event_params[0] != SUBEVT_LE_SCAN_REQUEST_RECEIVED:
                continue
            
            subevt_code, adv_handle, scanner_addr_type, scanner_addr = struct.unpack('<BBB6s', event_params)
            event_params = {
                'Subevent_Code': subevt_code,
                'Advertising_Handle': adv_handle,
                'Scanner_Address_Type': scanner_addr_type,
                'Scanner_Address': scanner_addr
            }

            print(event_params)

        hci_close_dev(dd.fileno())


if __name__ == '__main__':
    # print(EVT_READ_REMOTE_VERSION_COMPLETE)
    # print(EVT_READ_REMOTE_VERSION_COMPLETE_SIZE)
    # __Test.scan_undiscoverable_dev()
    __Test.pp_le_scanner_addr()
