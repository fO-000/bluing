#!/usr/bin/env python3

import time
import select
import subprocess
import warnings
import struct

from bluetooth import DeviceDiscoverer

# Temporary solution for PyBlueZ problems
warnings.filterwarnings("ignore", category=DeprecationWarning)
from bluetooth._bluetooth import SOL_HCI, HCI_FILTER
from bluetooth._bluetooth import hci_open_dev, hci_filter_new, \
    hci_filter_set_ptype, hci_filter_all_events, hci_send_cmd, hci_close_dev
from bluetooth._bluetooth import OGF_LINK_CTL, OCF_INQUIRY
from bluetooth._bluetooth import HCI_EVENT_PKT, EVT_CMD_STATUS, \
    EVT_INQUIRY_RESULT, EVT_INQUIRY_RESULT_WITH_RSSI, \
    EVT_EXTENDED_INQUIRY_RESULT, EVT_INQUIRY_COMPLETE

from bthci import HCI
from pyclui import green, blue, yellow, red, \
    DEBUG, INFO, WARNING, ERROR

from . import BlueScanner
from . import service_cls_profile_ids
from . import gap_type_name_pairs, \
    COMPLETE_16_BIT_SERVICE_CLS_UUID_LIST, \
    COMPLETE_32_BIT_SERVICE_CLS_UUID_LIST, \
    COMPLETE_128_BIT_SERVICE_CLS_UUID_LIST, COMPLETE_LOCAL_NAME, \
    SHORTENED_LOCAL_NAME, TX_POWER_LEVEL


major_dev_clses = {
    0b00000: 'Miscellaneous',
    0b00001: 'Computer',
    0b00010: 'Phone',
    0b00011: 'Lan/Network Access Point',
    0b00100: 'Audio/Video',
    0b00101: 'Peripheral (HID)',
    0b00110: 'Imaging',
    0b00111: 'Wearable',
    0b01000: 'Toy',
    0b01001: 'Health',
    0b11111: 'Uncategorized'
}

class BRScanner(BlueScanner):
    def inquiry(self, lap=0x9e8b33, inquiry_len=0x08, num_rsp=0x00):
        print(INFO, "BR scanning on " + blue("hci%d"%self.devid) + \
              " with timeout " + blue("%.2f sec\n"%(inquiry_len*1.28))+'\n')
        
        self.scanned_dev = []
        self.remote_name_req_flag = True
        
        cmd_params = lap.to_bytes(3, 'little') + \
            inquiry_len.to_bytes(1, 'little') + num_rsp.to_bytes(1, 'little')
        
        # If no filter is set, we can't receive any inquiry result.
        flt = hci_filter_new()
        hci_filter_set_ptype(flt, HCI_EVENT_PKT)
        hci_filter_all_events(flt)

        dd = hci_open_dev(self.devid)
        dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

        hci_send_cmd(dd, OGF_LINK_CTL, OCF_INQUIRY, cmd_params)

        try:
            while True:
                data = dd.recv(300)
                if len(data) >= 4:
                    event_code = data[1]
                    if event_code == EVT_CMD_STATUS:
                        # print(DEBUG, 'HCI_Command_Status')
                        pass
                    elif event_code == EVT_INQUIRY_RESULT:
                        print(DEBUG, 'HCI_Inquiry_Result')
                        self.pp_inquiry_result(data[3:])
                    elif event_code == EVT_INQUIRY_RESULT_WITH_RSSI:
                        # print(DEBUG, 'HCI_Inquiry_Result_with_RSSI')
                        self.pp_inquiry_result_with_rssi(data[3:])
                    elif event_code == EVT_EXTENDED_INQUIRY_RESULT:
                        # print(DEBUG, 'HCI_Extended_Inquiry_Result')
                        self.pp_extended_inquiry_result(data[3:])
                    elif event_code == EVT_INQUIRY_COMPLETE:
                        # print(DEBUG, 'HCI_Inquiry_Complete')
                        print(INFO, 'Inquiry completed\n')

                        if self.remote_name_req_flag:
                            print(INFO, 'Requesting the name of the scanned devices...')
                            for bd_addr in self.scanned_dev:
                                try:
                                    name = HCI(self.iface).remote_name_request({
                                        'BD_ADDR': bytes.fromhex(bd_addr.replace(':', '')),
                                        'Page_Scan_Repetition_Mode': 0x01, 
                                        'Reserved': 0x00, 'Clock_Offset': 0x0000
                                    })['Remote_Name'].decode().strip()
                                except Exception as e:
                                    print(e)
                                    name = ''

                                print(bd_addr+':', blue(name))
                        break
                    else:
                        print(DEBUG, "Unknow:", data)
        except KeyboardInterrupt as e:
            print(INFO, "BR/EDR devices scan canceled\n")
            HCI(self.iface).inquiry_cancel()

        hci_close_dev(dd.fileno())


    def pp_inquiry_result(self, params):
        '''Parse and print HCI_Inquiry_Result.'''
        num_rsp = params[0]
        if num_rsp != 1:
            print(INFO, 'Num_Responses in HCI_Inquiry_Result is %d.'%num_rsp)
            print(DEBUG, 'HCI_Inquiry_Result:', params)
            return

        bd_addr, page_scan_repetition_mode, reserved, cod, clk_offset = \
           struct.unpack('<6sBB3sH', params[1:])

        bd_addr = ':'.join(['%02X'%b for b in bd_addr[::-1]])
        if bd_addr in self.scanned_dev:
            return

        print('Addr:', blue(bd_addr))
        print('Page scan repetition mode: ', end='')
        pp_page_scan_repetition_mode(page_scan_repetition_mode)
        print('Reserved: 0x%02x'% reserved)

        cod = int.from_bytes(cod, byteorder='little')
        print('CoD: 0x%06X' % cod)
        pp_cod(cod)

        print('Clock offset: 0x%04X' % clk_offset)

        # HCI(self.iface).read_remote_name_req()
        print('\n')

        self.scanned_dev.append(bd_addr)


    def pp_inquiry_result_with_rssi(self, params):
        '''Parse and print HCI_Inquiry_Result_with_RSSI.'''
        num_rsp = params[0]
        if num_rsp != 1:
            print(INFO, 'Num_Responses in HCI_Inquiry_Result_with_RSSI is %d.'%num_rsp)
            print(DEBUG, 'HCI_Inquiry_Result_with_RSSI:', params)
            return

        bd_addr, page_scan_repetition_mode, reserved, cod, clk_offset, rssi = \
            struct.unpack('<6sBB3sHb', params[1:])

        bd_addr = ':'.join(['%02X'%b for b in bd_addr[::-1]])
        if bd_addr in self.scanned_dev:
            return

        print('Addr:', blue(bd_addr))
        # print('name:', blue(name.decode()))
        print('Page scan repetition mode: ', end='')
        pp_page_scan_repetition_mode(page_scan_repetition_mode)
        print('Reserved: 0x%02x'% reserved)

        cod = int.from_bytes(cod, byteorder='little')
        print('CoD: 0x%06X' % cod)
        pp_cod(cod)

        print('Clock offset: 0x%04X' % clk_offset)
        print('RSSI: %d' % rssi)
        print('\n')

        self.scanned_dev.append(bd_addr)


    def pp_extended_inquiry_result(self, params):
        '''Parse and print HCI_Extended_Inquiry_Result'''
        num_rsp = params[0]
        if num_rsp != 1:
            print(INFO, 'Num_Responses in HCI_Extended_Inquiry_Result is %d.'%num_rsp)
            print(DEBUG, 'HCI_Extended_Inquiry_Result:', params)
            return

        bd_addr, page_scan_repetition_mode, reserved, cod, \
            clk_offset, rssi, ext_inq_rsp = struct.unpack(
                '<6sBB3sHb240s', params[1:])

        bd_addr = ':'.join(['%02X'%b for b in bd_addr[::-1]])
        if bd_addr in self.scanned_dev:
            return

        print('Addr:', blue(bd_addr))
        # print('name:', blue(name.decode()))
        print('Page scan repetition mode: ', end='')
        pp_page_scan_repetition_mode(page_scan_repetition_mode)
        print('Reserved: 0x%02x'% reserved)

        cod = int.from_bytes(cod, byteorder='little')
        print('CoD: 0x%06X' % cod)
        pp_cod(cod)

        print('Clock offset: 0x%04X' % clk_offset)
        print('RSSI: %d' % rssi)
        pp_ext_inquiry_rsp(ext_inq_rsp)
        print('\n')

        self.scanned_dev.append(bd_addr)


def pp_page_scan_repetition_mode(val):
    print(val, end=' ')
    if val == 0x00:
        print('(R0)')
    elif val == 0x01:
        print('(R1)')
    elif val == 0x02:
        print('(R2)')
    else:
        print(red('RFU'))


def pp_cod(cod:int):
    '''Print and parse the Class of Device.'''
    #print(DEBUG, 'br_scan.py pp_cod()')
    if cod > 0xFFFFFF or cod & 0x000003 != 0:
        print(WARNING, "CoD's Format Type is not format #1")
        return

    print('\tService Class: %s' % bin(cod>>13))
    information = lambda b: (b >> 23) & 1
    telephony = lambda b: (b >> 22) & 1
    audio = lambda b: (b >> 21) & 1
    object_transfer = lambda b: (b >> 20) & 1
    capturing = lambda b: (b >> 19) & 1
    rendering = lambda b: (b >> 18) & 1
    networking = lambda b: (b >> 17) & 1
    positioning = lambda b: (b >> 16) & 1
    limited_discoverable_mode = lambda b: (b >> 13) & 1

    # Parse Service Class field
    if information(cod):
        print('\t\t'+'Information (WEB-server, WAP-server, ...)')

    if telephony(cod):
        print('\t\t'+'Telephony (Cordless telephony, Modem, Headset service, ...)')

    if audio(cod):
        print('\t\t'+'Audio (Cordless telephony, Modem, Headset service, ...)')

    if object_transfer(cod):
        print('\t\t'+'Object Transfer (v-Inbox, v-Folder, ...)')

    if capturing(cod):
        print('\t\t'+'Capturing (Scanner, Microphone, ...)')

    if rendering(cod):
        print('\t\t'+'Rendering (Printing, Speaker, ...)')

    if networking(cod):
        print('\t\t'+'Networking (LAN, Ad hoc, ...)')

    if positioning(cod):
        print('\t\t'+'Positioning (Location identification)')

    if limited_discoverable_mode(cod):
        print('\t\t'+'Limited Discoverable Mode')

    # Parse Major Device Class
    major_dev_cls = (cod>>8)&0x001F
    print('\tMajor Device Class: %s,'%bin(major_dev_cls), blue(major_dev_clses[major_dev_cls]))

    # Parse Minor Device class
    pp_minor_dev_cls((cod>>8)&0x0000, major_dev_cls)


def pp_ext_inquiry_rsp(ext_inq_rsp):
    '''Parse and print Extended Inquiry Response (240 octets)

    https://www.bluetooth.com/specifications/assigned-numbers/generic-access-profile/
    '''
    print('Extended inquiry response: ', end='')
    if ext_inq_rsp[0] == 0:
        print(red('None'))
        return

    print()

    while ext_inq_rsp[0] != 0:
        length = ext_inq_rsp[0]
        data = ext_inq_rsp[1:1+length]
        data_type = data[0]
        ext_inq_rsp = ext_inq_rsp[1+length:]
        print('\t', end='')
        if data_type == COMPLETE_16_BIT_SERVICE_CLS_UUID_LIST:
            print(gap_type_name_pairs[data_type])
            if length - 1 >= 2:
                eir_data = data[1:]
                if len(eir_data) % 2 != 0:
                    print('\t\t'+blue('Invalid EIR data length: %d'%len(eir_data)))
                    continue

                for i in range(0, len(eir_data), 2):
                    uuid = int.from_bytes(eir_data[i:i+2], byteorder='little')
                    print('\t\t0x%04x '%uuid, end='')
                    try:
                        print(blue(service_cls_profile_ids[uuid]['Name']))
                    except KeyError as e:
                        print(red('unknown'))
            else:
                print('\t\t'+red('None'))
        elif data_type == COMPLETE_32_BIT_SERVICE_CLS_UUID_LIST:
            print(gap_type_name_pairs[data_type])
            if length - 1 >= 4:
                eir_data = data[1:]
                if len(eir_data) % 4 != 0:
                    print('\t\t'+INFO, 'Invalid EIR data length: %d'%len(eir_data), eir_data)
                    continue
                for i in range(0, len(eir_data), 4):
                    uuid = int.from_bytes(eir_data[i:i+4], byteorder='little')
                    print('\t\t0x%08x '%uuid)
            else:
                print('\t\t'+red('None'))
        elif data_type == COMPLETE_128_BIT_SERVICE_CLS_UUID_LIST:
            print(gap_type_name_pairs[data_type])
            if length - 1 >= 16:
                eir_data = data[1:]
                if len(eir_data) % 16 != 0:
                    print('\t\t'+INFO, 'Invalid EIR data length: %d'%len(eir_data), eir_data)
                    continue
                for i in range(0, len(eir_data), 16):
                    uuid = int.from_bytes(eir_data[i:i+16], byteorder='little')
                    uuid_str = '%032X' % uuid
                    print('\t\t', end='')
                    print(blue('-'.join([uuid_str[:8], uuid_str[8:12], 
                        uuid_str[12:16], uuid_str[16:20], uuid_str[20:32]])))   
            else:
                print('\t\t'+red('None'))
        elif data_type == SHORTENED_LOCAL_NAME or \
            data_type == COMPLETE_LOCAL_NAME:
            print(gap_type_name_pairs[data_type]+':', blue(data[1:].decode()))
        elif data_type == TX_POWER_LEVEL:
            print(gap_type_name_pairs[data_type]+':', blue(str(int.from_bytes(
                data[1:], byteorder='little')) + ' dBm'))
        else:
            try:
                print(gap_type_name_pairs[data_type])
            except KeyError as e:
                print(red('Unknown, 0x%02x'%data_type))
            print('\t\t', data[1:],sep='')


def pp_minor_dev_cls(val:int, major_dev_cls:int):
    pass


def __test():
    BRScanner().inquiry()
    # pp_minor_dev_cls(0x002540)


if __name__ == "__main__":
    __test()
