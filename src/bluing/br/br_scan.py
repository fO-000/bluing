#!/usr/bin/env python

import sys
import struct

from bthci import HCI, HciRuntimeError, ControllerErrorCodes
from bthci.events import HciEventCodes, HCI_Inquiry_Result, HCI_Inquiry_Result_with_RSSI, \
                         HCI_Extended_Inquiry_Result
from bthci.bluez_hci import HCI_CHANNEL_USER
from xpycommon.log import Logger
from xpycommon.ui import green, blue, red
from xpycommon.bluetooth import ClassOfDevice

from .. import BlueScanner, service_cls_profile_ids
from ..ui import INDENT
from ..common import bdaddr_to_company_name
from ..le.ll import ll_vers
from ..gap_data import gap_type_names, \
    COMPLETE_LIST_OF_16_BIT_SERVICE_CLASS_UUIDS, \
    COMPLETE_LIST_OF_32_BIT_SERVICE_CLASS_UUIDS, \
    COMPLETE_LIST_OF_128_BIT_SERVICE_CLASS_UUIDS, COMPLETE_LOCAL_NAME, \
    SHORTENED_LOCAL_NAME, TX_POWER_LEVEL

from . import LOG_LEVEL
from .lmp import lmp_vers, company_identfiers, pp_lmp_features, pp_ext_lmp_features


logger = Logger(__name__, LOG_LEVEL)


class BrScanner(BlueScanner):
    def inquiry(self, inquiry_len=0x08):
        logger.info("Discovering other nearby BR/EDR Controllers on {} for {} sec\n\n".format(
            blue(self.iface), blue("{:.2f}".format(inquiry_len*1.28))))

        self.scanned_dev = []
        self.remote_name_req_flag = True
        hci = HCI(self.iface)

        def inquiry_result_handler(result: bytes):
            event_code = result[0]

            logger.debug("Entered inquiry(), inquiry_result_handler()\n"
                         "{}".format(HciEventCodes[event_code].name))

            if event_code == HCI_Inquiry_Result.evt_code:
                self.pp_inquiry_result(result[2:])
            elif event_code == HCI_Inquiry_Result_with_RSSI.evt_code:
                self.pp_inquiry_result_with_rssi(result[2:])
            elif event_code == HCI_Extended_Inquiry_Result.evt_code:
                self.pp_extended_inquiry_result(result[2:])
            else:
                logger.warning('Unknow inquiry result: {}'.format(result))

        try:
            hci.inquiry(inquiry_len=inquiry_len, inquiry_result_handler=inquiry_result_handler)
            # logger.info('Inquiry completed\n')

            if self.remote_name_req_flag and len(self.scanned_dev) != 0:
                logger.info('Requesting the names of all discovered devices...')
                for bd_addr in self.scanned_dev:
                    try:
                        remote_name_req_compelte = hci.remote_name_request(bd_addr)
                        if remote_name_req_compelte.status != ControllerErrorCodes.SUCCESS:
                            logger.warning("Failed to request name of {}\n"
                                           "    remote name request complete status: 0x{:02x} - {}".format(
                                             bd_addr,
                                             remote_name_req_compelte.status, ControllerErrorCodes[remote_name_req_compelte.status].name))
                            name = ''
                        else:
                            name = remote_name_req_compelte.remote_name
                    except TimeoutError as e:
                        name = ''
                    except HciRuntimeError as e:
                        logger.error("{}: \"{}\"".format(e.__class__, e))
                        name = ''

                    print("{} : {}".format(bd_addr, blue(name)))
        except HciRuntimeError as e:
            logger.error("{}".format(e))
        except KeyboardInterrupt as e:
            logger.info('BR/EDR devices scan canceled\n')
            hci.inquiry_cancel()
            
        hci.close()


    def scan_lmp_features(self, paddr: str):
        hci = HCI(self.iface, HCI_CHANNEL_USER)
        conn_complete = hci.create_connection(paddr, page_scan_repetition_mode = 0x02)

        if conn_complete.status != ControllerErrorCodes.SUCCESS:
            logger.error("Failed to connect {} BD/EDR address\n"
                         "    connection complete status: 0x{:02x} - {}".format(
                             paddr,
                             conn_complete.status, ControllerErrorCodes[conn_complete.status].name))
            sys.exit(1)

        read_remote_version_info_complete = hci.read_remote_version_information(conn_complete.conn_handle)

        if read_remote_version_info_complete.status != ControllerErrorCodes.SUCCESS:
            logger.error('Failed to read remote version')
            sys.exit(1)

        print(blue('Version'))
        print('    Version:')
        print(' '*8+lmp_vers[read_remote_version_info_complete.version], '(LMP)')
        print(' '*8+ll_vers[read_remote_version_info_complete.version], '(LL)')
        print('    Manufacturer name:', green(company_identfiers[read_remote_version_info_complete.company_id]))
        print('    Subversion:', read_remote_version_info_complete.subversion, '\n')

        read_remote_supported_features_complete = hci.read_remote_supported_features(conn_complete.conn_handle)
        if read_remote_supported_features_complete.status != ControllerErrorCodes.SUCCESS:
            logger.error("Failed to read remote extented features\n"
                         "    read remote extented features complete status: 0x{:02x} - {}".format(
                             read_remote_ext_features_complete.status, ControllerErrorCodes[read_remote_ext_features_complete.status].name))
            hci.disconnect(conn_complete.conn_handle)
            sys.exit(1)
  
        print(blue('LMP features'))
        pp_lmp_features(read_remote_supported_features_complete.lmp_features)
        print()

        if not True if (read_remote_supported_features_complete.lmp_features[7] >> 7) & 0x01 else False:
            sys.exit(1)

        print(blue('Extended LMP features'))
        # Get Max_Page_Number
        read_remote_ext_features_complete = hci.read_remote_extended_features(conn_complete.conn_handle, 0x00)
        if read_remote_ext_features_complete.status != ControllerErrorCodes.SUCCESS:
            logger.error("Failed to read remote extented features\n"
                         "    read remote extented features complete status: 0x{:02x} - {}".format(
                             read_remote_ext_features_complete.status, ControllerErrorCodes[read_remote_ext_features_complete.status].name))
            hci.disconnect(conn_complete.conn_handle)
            sys.exit(1)
            
        max_page_num = read_remote_ext_features_complete.max_page_num
        for i in range(1, max_page_num+1):
            read_remote_ext_features_complete_i = hci.read_remote_extended_features(conn_complete.conn_handle, i)
            if read_remote_ext_features_complete_i.status != ControllerErrorCodes.SUCCESS:
                logger.error('Failed to read remote extented features, page {}'.format(i))
            else:
                pp_ext_lmp_features(read_remote_ext_features_complete_i.ext_lmp_features, i)
                
        hci.disconnect(conn_complete.conn_handle)


    def pp_inquiry_result(self, params):
        '''Parse and print HCI_Inquiry_Result.'''
        num_rsp = params[0]
        if num_rsp != 1:
            logger.info('Num_Responses in HCI_Inquiry_Result is %d.'%num_rsp)
            logger.debug('HCI_Inquiry_Result: {}'.format(params))
            return

        bd_addr, page_scan_repetition_mode, reserved, cod, clk_offset = \
           struct.unpack('<6sBH3sH', params[1:])

        bd_addr = ':'.join(['%02X'%b for b in bd_addr[::-1]])
        if bd_addr in self.scanned_dev:
            return

        print("BD_ADDR: {} ({})".format(blue(bd_addr), bdaddr_to_company_name(bd_addr)))
        print("Page scan repetition mode: ", end='')
        pp_page_scan_repetition_mode(page_scan_repetition_mode)
        print("Reserved: 0x{:04x}".format(reserved))

        cod = int.from_bytes(cod, byteorder='little')
        print("CoD: 0x{:06x}".format(cod))
        ClassOfDevice.from_int(cod).print_human_readable(1)

        print("Clock offset: 0x{:04X}".format(clk_offset))

        # HCI(self.iface).read_remote_name_req()
        print('\n')

        self.scanned_dev.append(bd_addr)


    def pp_inquiry_result_with_rssi(self, params):
        '''Parse and print HCI_Inquiry_Result_with_RSSI.'''
        num_rsp = params[0]
        if num_rsp != 1:
            logger.info('Num_Responses in HCI_Inquiry_Result_with_RSSI is %d.'%num_rsp)
            logger.debug('HCI_Inquiry_Result_with_RSSI: {}'.format(params))
            return

        bd_addr, page_scan_repetition_mode, reserved, cod, clk_offset, rssi = \
            struct.unpack('<6sBB3sHb', params[1:])

        bd_addr = ':'.join(['%02X'%b for b in bd_addr[::-1]])
        if bd_addr in self.scanned_dev:
            return

        print("BD_ADDR: {} ({})".format(blue(bd_addr), bdaddr_to_company_name(bd_addr)))
        # print('name:', blue(name.decode()))
        print("Page scan repetition mode: ", end='')
        pp_page_scan_repetition_mode(page_scan_repetition_mode)
        print("Reserved: 0x{:02x}".format(reserved))

        cod = int.from_bytes(cod, byteorder='little')
        print("CoD: 0x{:06x}".format(cod))
        ClassOfDevice.from_int(cod).print_human_readable(1)

        print("Clock offset: 0x{:04X}".format(clk_offset))
        print("RSSI:", rssi)
        print('\n')

        self.scanned_dev.append(bd_addr)


    def pp_extended_inquiry_result(self, params):
        '''Parse and print HCI_Extended_Inquiry_Result'''
        num_rsp = params[0]
        if num_rsp != 1:
            logger.info('Num_Responses in HCI_Extended_Inquiry_Result is %d.'%num_rsp)
            logger.debug('HCI_Extended_Inquiry_Result: {}'.format(params))
            return

        bd_addr, page_scan_repetition_mode, reserved, cod, \
            clk_offset, rssi, ext_inq_rsp = struct.unpack(
                '<6sBB3sHb240s', params[1:])

        bd_addr = ':'.join(['%02X'%b for b in bd_addr[::-1]])
        if bd_addr in self.scanned_dev:
            return

        print("BD_ADDR: {} ({})".format(blue(bd_addr), bdaddr_to_company_name(bd_addr)))
        # print('name:', blue(name.decode()))
        print('Page scan repetition mode: ', end='')
        pp_page_scan_repetition_mode(page_scan_repetition_mode)
        print("Reserved: 0x{:02x}".format(reserved))

        cod = int.from_bytes(cod, byteorder='little')
        print("CoD: 0x{:06x}".format(cod))
        ClassOfDevice.from_int(cod).print_human_readable(1)

        print("Clock offset: 0x{:04X}".format(clk_offset))
        print("RSSI:", rssi)
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
        print(INDENT, end='')
        # TODO: Unify the gap type name parsings of BR and LE
        if data_type == COMPLETE_LIST_OF_16_BIT_SERVICE_CLASS_UUIDS:
            print(gap_type_names[data_type])
            if length - 1 >= 2:
                eir_data = data[1:]
                if len(eir_data) % 2 != 0:
                    print(INDENT*2 + blue('Invalid EIR data length: %d'%len(eir_data)))
                    continue

                for i in range(0, len(eir_data), 2):
                    uuid = int.from_bytes(eir_data[i:i+2], byteorder='little')
                    print(INDENT*2 + '0x%04x '%uuid, end='')
                    try:
                        print(blue(service_cls_profile_ids[uuid]['Name']))
                    except KeyError as e:
                        print(red('unknown'))
            else:
                print(INDENT*2 + red('None'))
        elif data_type == COMPLETE_LIST_OF_32_BIT_SERVICE_CLASS_UUIDS:
            print(gap_type_names[data_type])
            if length - 1 >= 4:
                eir_data = data[1:]
                if len(eir_data) % 4 != 0:
                    logger.info(INDENT*2 + 'Invalid EIR data length: {} {}'.format(len(eir_data), eir_data))
                    continue
                for i in range(0, len(eir_data), 4):
                    uuid = int.from_bytes(eir_data[i:i+4], byteorder='little')
                    print(INDENT*2 + '0x%08x '%uuid)
            else:
                print(INDENT*2 + red('None'))
        elif data_type == COMPLETE_LIST_OF_128_BIT_SERVICE_CLASS_UUIDS:
            print(gap_type_names[data_type])
            if length - 1 >= 16:
                eir_data = data[1:]
                if len(eir_data) % 16 != 0:
                    logger.info(INDENT*2 + 'Invalid EIR data length: {} {}'.format(len(eir_data), eir_data))
                    continue
                for i in range(0, len(eir_data), 16):
                    uuid = int.from_bytes(eir_data[i:i+16], byteorder='little')
                    uuid_str = '%032X' % uuid
                    print(INDENT*2, end='')
                    print(blue('-'.join([uuid_str[:8], uuid_str[8:12], 
                        uuid_str[12:16], uuid_str[16:20], uuid_str[20:32]])))   
            else:
                print(INDENT*2 + red('None'))
        elif data_type == SHORTENED_LOCAL_NAME or \
            data_type == COMPLETE_LOCAL_NAME:
            print(gap_type_names[data_type]+':', blue(data[1:].decode()))
        elif data_type == TX_POWER_LEVEL:
            print(gap_type_names[data_type]+':', blue(str(int.from_bytes(
                data[1:], byteorder='little')) + ' dBm'))
        else:
            try:
                print(gap_type_names[data_type])
            except KeyError as e:
                print(red('Unknown, 0x%02x'%data_type))
            print(INDENT*2, data[1:],sep='')
