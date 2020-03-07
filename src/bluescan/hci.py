#!/usr/bin/env python3

import os
import re
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

from bluetooth._bluetooth import HCI_MAX_EVENT_SIZE # bluez set this to 260, but the max is 257
from bluetooth._bluetooth import cmd_opcode_pack
from bluetooth._bluetooth import hci_send_cmd

from bluetooth._bluetooth import OGF_LINK_CTL
from bluetooth._bluetooth import OCF_INQUIRY_CANCEL
from bluetooth._bluetooth import OCF_EXIT_PERIODIC_INQUIRY

from bluetooth._bluetooth import OGF_HOST_CTL
from bluetooth._bluetooth import OCF_RESET
from bluetooth._bluetooth import OCF_SET_EVENT_FLT
from bluetooth._bluetooth import OCF_WRITE_SCAN_ENABLE
from bluetooth._bluetooth import OCF_READ_LOCAL_NAME
from bluetooth._bluetooth import OCF_WRITE_INQUIRY_MODE
from bluetooth._bluetooth import OCF_READ_CLASS_OF_DEV

from bluetooth._bluetooth import OGF_INFO_PARAM
from bluetooth._bluetooth import OCF_READ_BD_ADDR

OGF_LE_CTL = 0x08
OCF_LE_SET_ADVERTISING_ENABLE = 0x000A
OCF_LE_SET_SCAN_ENABLE = 0x000C

from bluetooth._bluetooth import EVT_CMD_COMPLETE
from bluetooth._bluetooth import EVT_INQUIRY_COMPLETE

from bluetooth._bluetooth import HCI_EVENT_PKT

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


def hcix2devid(hcix:str) -> int:
    devid = re.findall('(0)|([1-9]+)', hcix, flags=0)
    if len(devid) == 1 and ((devid[0][0] == '') ^ (devid[0][1] == '')):
        devid = int(devid[0][0]) if devid[0][0] != '' else int(devid[0][1])
    else:
        devid = -1
        print('[ERROR] Invalid HCI device', hcix)

    return devid


################################### EVENT #####################################
def parse_hci_command_complete(pkt):
    event_code, param_total_len, num_of_allowed_cmdpkt, opcode, status \
        = struct.unpack('=BBBHB', pkt)

    # print('[DEBUG] event_code:', event_code)
    # print('[DEBUG] param_total_len:', param_total_len)
    # print('[DEBUG] num_of_allowed_cmdpkt:', num_of_allowed_cmdpkt)
    # print('[DEBUG] opcode: 0x%04x' % opcode)
    # print('[DEBUG] status:', status)
    # print()

    if event_code != 0x0E:
        return (event_code,)+(None,)*4

    return (event_code, param_total_len, num_of_allowed_cmdpkt, opcode, status)


######################## LINK CONTROL COMMANDS ################################
def hci_inquiry_cancel(iface='hci0') -> int:
    # print('[DEBUG] hci_inquiry_cancel()')
    devid = hcix2devid(iface)
    dd = hci_open_dev(devid)

    flt = hci_filter_new()
    hci_filter_clear(flt)
    hci_filter_set_ptype(flt, HCI_EVENT_PKT)
    hci_filter_set_event(flt, EVT_CMD_COMPLETE)
    hci_filter_set_opcode(
        flt, cmd_opcode_pack(OGF_LINK_CTL, OCF_INQUIRY_CANCEL))
    dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

    hci_send_cmd(dd, OGF_LINK_CTL, OCF_INQUIRY_CANCEL)

    hci_cmd_complete = dd.recv(HCI_MAX_EVENT_SIZE)[1:] # exclude 1 B HCI header
    event_code, param_total_len, num_of_allowed_cmdpkt, opcode, status \
        = parse_hci_command_complete(hci_cmd_complete)

    hci_close_dev(dd.fileno())
    return status


def hci_exit_periodic_inquiry_mode(iface='hci0'):
    # print('[DEBUG] hci_exit_periodic_inquiry_mode()')
    devid = hcix2devid(iface)
    dd = hci_open_dev(devid)

    flt = hci_filter_new()
    hci_filter_set_ptype(flt, HCI_EVENT_PKT)
    hci_filter_set_event(flt, EVT_CMD_COMPLETE)
    hci_filter_set_opcode(
        flt, cmd_opcode_pack(OGF_LINK_CTL, OCF_EXIT_PERIODIC_INQUIRY))
    dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

    hci_send_cmd(dd, OGF_LINK_CTL, OCF_EXIT_PERIODIC_INQUIRY)

    hci_cmd_complete = dd.recv(HCI_MAX_EVENT_SIZE)[1:] # exclude 1 B HCI header
    event_code, param_total_len, num_of_allowed_cmdpkt, opcode, status \
        = parse_hci_command_complete(hci_cmd_complete)
    
    hci_close_dev(dd.fileno())
    return status


###################### CONTROLLER & BASEBAND COMMANDS #########################
def hci_reset(iface='hci0'):
    # print('[DEBUG] hci_reset()')
    devid = hcix2devid(iface)
    dd = hci_open_dev(devid)

    flt = hci_filter_new()
    hci_filter_set_ptype(flt, HCI_EVENT_PKT)
    hci_filter_set_event(flt, EVT_CMD_COMPLETE)
    hci_filter_set_opcode(flt, cmd_opcode_pack(OGF_HOST_CTL, OCF_RESET))
    dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

    hci_send_cmd(dd, OGF_HOST_CTL, OCF_RESET)
    hci_cmd_complete = dd.recv(HCI_MAX_EVENT_SIZE)[1:] # exclude 1 B HCI header
    event_code, param_total_len, num_of_allowed_cmdpkt, opcode, status \
        = parse_hci_command_complete(hci_cmd_complete)
    
    hci_close_dev(dd.fileno())
    return status


def hci_set_event_filter(
    iface='hci0', filter_type=b'\x00', condition_type=b'', condition=b''):
    # print('[DEBUG] hci_set_event_filter()')
    devid = hcix2devid(iface)
    dd = hci_open_dev(devid)

    flt = hci_filter_new()
    hci_filter_set_ptype(flt, HCI_EVENT_PKT)
    hci_filter_set_event(flt, EVT_CMD_COMPLETE)
    hci_filter_set_opcode(flt, cmd_opcode_pack(OGF_HOST_CTL, OCF_SET_EVENT_FLT))
    dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

    hci_send_cmd(dd, OGF_HOST_CTL, OCF_SET_EVENT_FLT, filter_type+condition_type+condition)
    hci_cmd_complete = dd.recv(HCI_MAX_EVENT_SIZE)[1:] # exclude 1 B HCI header
    event_code, param_total_len, num_of_allowed_cmdpkt, opcode, status \
        = parse_hci_command_complete(hci_cmd_complete)
    
    hci_close_dev(dd.fileno())
    return status


    
def hci_write_scan_enable(iface='hci0', scan_enable=b'\x00'):
    # print('[DEBUG] hci_write_scan_enable()')
    devid = hcix2devid(iface)
    dd = hci_open_dev(devid)

    flt = hci_filter_new()
    hci_filter_set_ptype(flt, HCI_EVENT_PKT)
    hci_filter_set_event(flt, EVT_CMD_COMPLETE)
    hci_filter_set_opcode(
        flt, cmd_opcode_pack(OGF_HOST_CTL, OCF_WRITE_SCAN_ENABLE))
    dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

    hci_send_cmd(dd, OGF_HOST_CTL, OCF_WRITE_SCAN_ENABLE, scan_enable)
    hci_cmd_complete = dd.recv(HCI_MAX_EVENT_SIZE)[1:] # exclude 1 B HCI header
    event_code, param_total_len, num_of_allowed_cmdpkt, opcode, status \
        = parse_hci_command_complete(hci_cmd_complete)
    
    hci_close_dev(dd.fileno())
    return status


def hci_write_inquiry_mode(iface='hci0', mode=b'\x00'):
    # print('[DEBUG] hci_write_inquiry_mode()')
    devid = hcix2devid(iface)
    dd = hci_open_dev(devid)

    flt = hci_filter_new()
    hci_filter_set_ptype(flt, HCI_EVENT_PKT)
    hci_filter_set_event(flt, EVT_CMD_COMPLETE)
    hci_filter_set_opcode(
        flt, cmd_opcode_pack(OGF_HOST_CTL, OCF_WRITE_INQUIRY_MODE))
    dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

    hci_send_cmd(dd, OGF_HOST_CTL, OCF_WRITE_INQUIRY_MODE, mode)
    hci_cmd_complete = dd.recv(HCI_MAX_EVENT_SIZE)[1:] # exclude 1 B HCI header
    event_code, param_total_len, num_of_allowed_cmdpkt, opcode, status \
        = parse_hci_command_complete(hci_cmd_complete)
    
    hci_close_dev(dd.fileno())
    return status


def hci_read_bd_addr(iface='hci0') -> str:
    r"""'Return BD_ADDR string "XX:XX:XX:XX:XX:XX'"""
    devid = hcix2devid(iface)
    dd = hci_open_dev(devid)

    flt = hci_filter_new()
    hci_filter_set_ptype(flt, HCI_EVENT_PKT)
    hci_filter_set_event(flt, EVT_CMD_COMPLETE)
    hci_filter_set_opcode(
        flt, cmd_opcode_pack(OGF_INFO_PARAM, OCF_READ_BD_ADDR))
    dd.setsockopt(SOL_HCI, HCI_FILTER, flt)
    
    hci_send_cmd(dd, OGF_INFO_PARAM, OCF_READ_BD_ADDR)

    pkt = dd.recv(HCI_MAX_EVENT_SIZE)[1:]
    event_code, param_total_len, num_of_allowed_cmdpkt, opcode, status, raw_bdaddr = struct.unpack("=cccHB6s", pkt)
    assert status == 0
    bdaddr = ["%02X" % int(b) for b in raw_bdaddr]
    bdaddr.reverse()
    bdaddr = ":".join(bdaddr)
    
    hci_close_dev(dd.fileno())
    return bdaddr


def hci_read_local_name(iface='hci0'):
    devid = hcix2devid(iface)
    dd = hci_open_dev(devid)

    flt = hci_filter_new()
    hci_filter_set_ptype(flt, HCI_EVENT_PKT)
    hci_filter_set_event(flt, EVT_CMD_COMPLETE)
    hci_filter_set_opcode(
        flt, cmd_opcode_pack(OGF_HOST_CTL, OCF_READ_LOCAL_NAME))
    dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

    hci_send_cmd(dd, OGF_HOST_CTL, OCF_READ_LOCAL_NAME)
    
    hci_cmd_complete = dd.recv(HCI_MAX_EVENT_SIZE)[1:]
    event_code, param_total_len, num_of_allowed_cmdpkt, opcode, status, local_name = struct.unpack('=cBcHc248s', hci_cmd_complete)
    local_name = local_name.decode()
    # print('[DEBUG] pkt_type:', pkt_type)
    # print('[DEBUG] event_code:', event_code)
    # print('[DEBUG] param_total_len:', param_total_len)
    # print('[DEBUG] num_of_allowed_cmdpkt:', num_of_allowed_cmdpkt)
    # print('[DEBUG] opcode:', opcode)
    # print('[DEBUG] status:', status)
    # print('[DEBUG] local_name:', local_name) # This length of this string is 248.
    hci_close_dev(dd.fileno())
    return local_name


def hci_read_class_of_device(iface='hci0'):
    devid = hcix2devid(iface)
    dd = hci_open_dev(devid)

    flt = hci_filter_new()
    hci_filter_set_ptype(flt, HCI_EVENT_PKT)
    hci_filter_set_event(flt, EVT_CMD_COMPLETE)
    hci_filter_set_opcode(
        flt, cmd_opcode_pack(OGF_HOST_CTL, OCF_READ_CLASS_OF_DEV))
    dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

    hci_send_cmd(dd, OGF_HOST_CTL, OCF_READ_CLASS_OF_DEV)

    hci_cmd_complete = dd.recv(HCI_MAX_EVENT_SIZE)[1:]
    event_code, param_total_len, num_of_allowed_cmdpkt, opcode, status, cod = struct.unpack('=cBcHc3s', hci_cmd_complete)
    cod = cod[::-1]
    # print('[DEBUG] pkt_type:', pkt_type)
    # print('[DEBUG] event_code:', event_code)
    # print('[DEBUG] param_total_len:', param_total_len)    
    # print('[DEBUG] num_of_allowed_cmdpkt:', num_of_allowed_cmdpkt)
    # print('[DEBUG] opcode:', opcode)
    # print('[DEBUG] status:', status)
    # print('[DEBUG] class:', cod)
    hci_close_dev(dd.fileno())
    return cod


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


def hci_write_authentication_enable(auth_enable=0x01, iface='hci0'):
    '''Write Authentication Enable command'''
    ogf = HCI_CTRL_BASEBAND_CMD_OGF
    ocf = 0x0020

    auth_enable = hex(auth_enable)
    params = auth_enable
    
    hcitool_cmd = gen_hcitool_cmd(ogf, ocf, params)
    subprocess.getoutput(hcitool_cmd)


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

############################## LE CONTROLLER COMMANDS #########################
def hci_le_set_advertising_enable(iface='hci0', enable=b'\x00'):
    # print('[DEBUG] hci_le_set_advertising_enable()')
    devid = hcix2devid(iface)
    dd = hci_open_dev(devid)

    flt = hci_filter_new()
    hci_filter_set_ptype(flt, HCI_EVENT_PKT)
    hci_filter_set_event(flt, EVT_CMD_COMPLETE)
    hci_filter_set_opcode(
        flt, cmd_opcode_pack(OGF_LE_CTL, OCF_LE_SET_ADVERTISING_ENABLE))
    dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

    hci_send_cmd(dd, OGF_LE_CTL, OCF_LE_SET_ADVERTISING_ENABLE, enable)
    hci_cmd_complete = dd.recv(HCI_MAX_EVENT_SIZE)[1:] # exclude 1 B HCI header
    event_code, param_total_len, num_of_allowed_cmdpkt, opcode, status \
        = parse_hci_command_complete(hci_cmd_complete)
    
    hci_close_dev(dd.fileno())
    return status


def hci_le_set_scan_enable(iface='hci0', enable=b'\x00', filter_dup=b'\x00'):
    # print('[DEBUG] hci_le_set_scan_enable()')
    devid = hcix2devid(iface)
    dd = hci_open_dev(devid)

    flt = hci_filter_new()
    hci_filter_set_ptype(flt, HCI_EVENT_PKT)
    hci_filter_set_event(flt, EVT_CMD_COMPLETE)
    hci_filter_set_opcode(
        flt, cmd_opcode_pack(OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE))
    dd.setsockopt(SOL_HCI, HCI_FILTER, flt)

    hci_send_cmd(dd, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, enable+filter_dup)
    hci_cmd_complete = dd.recv(HCI_MAX_EVENT_SIZE)[1:] # exclude 1 B HCI header
    event_code, param_total_len, num_of_allowed_cmdpkt, opcode, status \
        = parse_hci_command_complete(hci_cmd_complete)
    
    hci_close_dev(dd.fileno())
    return status


def test():
    hci_inquiry_cancel()
    hci_exit_periodic_inquiry_mode()
    hci_write_scan_enable()


if __name__ == '__main__':
    test()
