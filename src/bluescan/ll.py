#!/usr/bin/env python3

import logging

from pyclui import Logger
from pyclui import green, blue, yellow, red

logger = Logger(__name__, logging.INFO)

ll_vers = {
    0:  'Reserved',
    1:  'Reserved',
    2:  'Reserved',
    3:  'Reserved',
    4:  'Reserved',
    5:  'Reserved',
    6:  'Bluetooth® Core Specification 4.0',
    7:  'Bluetooth Core Specification 4.1',
    8:  'Bluetooth Core Specification 4.2',
    9:  'Bluetooth Core Specification 5.0',
    10: 'Bluetooth Core Specification 5.1',
    11: 'Bluetooth Core Specification 5.2'
}

# Advertising physical channel PDU header
PDU_TYPE_POS = 0
PDU_TYPE_MSK = 0b1111 << PDU_TYPE_POS

RFU_POS = 4
RFU_MSK = 0b1 << RFU_POS

CH_SEL_POS = 5
CH_SEL_MSK = 0b01 << CH_SEL_POS

TX_ADD_POS = 6
TX_ADD_MSK = 0b1 << TX_ADD_POS

RX_ADD_POS = 7
RX_ADD_MSK = 0b1 << RX_ADD_POS

# Advertising physical channel PDU type (Primary Advertising)

adv_phych_pdu_types = {
    0b0000: 'ADV_IND',
    0b0001: 'ADV_DIRECT_IND',
    0b0010: 'ADV_NONCONN_IND',
    0b0011: 'SCAN_REQ',
    0b0100: 'SCAN_RSP',
    0b0101: 'CONNECT_IND',
    0b0110: 'ADV_SCAN_IND',
    0b0111: 'ADV_EXT_IND'
}

# Advertising physical channel PDU type (Primary Advertising)
ADV_IND         = 0b0000
ADV_DIRECT_IND  = 0b0001
ADV_NONCONN_IND = 0b0010

ADV_SCAN_IND    = 0b0110
ADV_EXT_IND     = 0b0111
# AUX_ADV_IND
# AUX_SYNC_IND
# AUX_CHAIN_IND

SCAN_REQ        = 0b0011
SCAN_RSP        = 0b0100
# AUX_SCAN_REQ
# AUX_SCAN_RSP

CONNECT_IND     = 0b0101
# AUX_CONNECT_REQ
# AUX_CONNECT_RSP


def pp_adv_phych_pdu(pdu:bytes, ch:int) -> list:
    '''Parse and print advertising physical channel PDU

    ref 
    BLUETOOTH CORE SPECIFICATION Version 5.2 | Vol 6, Part B page 2871, 
    2.3 ADVERTISING PHYSICAL CHANNEL PDU

    Advertising physical channel PDU
    +------------------+
    | Header | Payload |
    |--------|---------|
    | 16 b   | 1-255 B |
    +------------------+

    Header
    +-------------------------------------------------+
    | PDU Type | RFU | ChSel | TxAdd | RxAdd | Length |
    |----------|-----|-------|-------|-------|--------|
    | 4 b      | 1 b | 1 b   | 1 b   | 1 b   | 8 b    |
    +-------------------------------------------------+
    '''
    header = pdu[:2]
    payload = pdu[2:]

    pdu_type = (header[0] & PDU_TYPE_MSK) >> PDU_TYPE_POS
    rfu      = (header[0] & RFU_MSK) >> RFU_POS
    ch_sel   = (header[0] & CH_SEL_MSK) >> CH_SEL_POS
    tx_add   = (header[0] & TX_ADD_MSK) >> TX_ADD_POS
    rx_add   = (header[0] & RX_ADD_MSK) >> RX_ADD_POS

    addrs = []
    
    print("[{}] ".format(ch), end='')
    if pdu_type == ADV_IND:
        adv_a = payload[:6][::-1]
        addrs = [{
            'BD_ADDR': adv_a,
            'type': 'public' if tx_add == 0b0 else 'random'
        }]
        
        print("[{}]".format(blue('ADV_IND')))
        print("{} AdvA: {}".format(
            'public' if tx_add == 0b0 else 'random', ':'.join('%02X'%b for b in adv_a)))
        # print("AdvData:", payload[6:])
    elif pdu_type == ADV_DIRECT_IND:
        adv_a = payload[:6][::-1]
        target_a = payload[6:][::-1]
        addrs = [
            {
                'BD_ADDR': adv_a,
                'type': 'public' if tx_add == 0b0 else 'random'
            },
            {
                'BD_ADDR': target_a,
                'type': 'public' if rx_add == 0b0 else 'random'
            },
        ]
        print("[{}]".format(blue('ADV_DIRECT_IND')))
        print("{} AdvA: {}".format(
            'public' if tx_add == 0b0 else 'random', ':'.join('%02X'%b for b in adv_a)))
        print("{} TargetA: {}".format(
            'public' if rx_add == 0b0 else 'random', ':'.join('%02X'%b for b in target_a)))
    elif pdu_type == ADV_NONCONN_IND:
        adv_a = payload[:6][::-1]
        addrs = [{
            'BD_ADDR': adv_a,
            'type': 'public' if tx_add == 0b0 else 'random'
        }]
        print("[{}]".format(red('ADV_NONCONN_IND')))
        print("{} AdvA: {}".format(
            'public' if tx_add == 0b0 else 'random', ':'.join('%02X'%b for b in adv_a)))
        # print("AdvData:", payload[6:])
    elif pdu_type == ADV_SCAN_IND:
        adv_a = payload[:6][::-1]
        addrs = [{
            'BD_ADDR': adv_a,
            'type': 'public' if tx_add == 0b0 else 'random'
        }]
        print("[{}]".format(blue('ADV_SCAN_IND')))
        print("{} AdvA: {}".format(
            'public' if tx_add == 0b0 else 'random', ':'.join('%02X'%b for b in adv_a)))
        # print("AdvData:", payload[6:])
    elif pdu_type == ADV_EXT_IND:
        print("[{}]".format(yellow('ADV_EXT_IND')))
        print("raw: {}".format(payload))
    elif pdu_type == SCAN_REQ:
        scan_a = payload[:6][::-1]
        adv_a = payload[6:][::-1]
        addrs = [
            {
                'BD_ADDR': scan_a,
                'type': 'public' if tx_add == 0b0 else 'random'
            },
            {
                'BD_ADDR': adv_a,
                'type': 'public' if rx_add == 0b0 else 'random'
            },     
        ]
        print("[{}]".format(blue('SCAN_REQ')))
        print("{} ScanA: {}".format(
            'public' if tx_add == 0b0 else 'random', ':'.join('%02X'%b for b in scan_a)))
        print("{} AdvA: {}".format(
            'public' if rx_add == 0b0 else 'random', ':'.join('%02X'%b for b in adv_a)))
    elif pdu_type == SCAN_RSP:
        adv_a = payload[:6][::-1]
        addrs = [{
            'BD_ADDR': adv_a,
            'type': 'public' if tx_add == 0b0 else 'random'
        }]
        print("[{}]".format(blue('SCAN_RSP')))
        print("{} AdvA: {}".format(
            'public' if tx_add == 0b0 else 'random', ':'.join('%02X'%b for b in adv_a)))
        # print("ScanRspData:", payload[6:])
    elif pdu_type == CONNECT_IND:
        init_a = payload[:6]
        adv_a = payload[6:12]
        print('init_a:', ':'.join('%02x'%b for b in init_a))
        print('adv_a:', ':'.join('%02x'%b for b in adv_a))
        addrs = [
            {
                'BD_ADDR': init_a,
                'type': 'public' if tx_add == 0b0 else 'random'
            },
            {
                'BD_ADDR': adv_a,
                'type': 'public' if rx_add == 0b0 else 'random'
            },
        ]
        print("[{}]".format(green('CONNECT_IND')))
        print("{} InitA: {}".format(
            'public' if tx_add == 0b0 else 'random', ':'.join('%02X'%b for b in init_a)))
        print("{} AdvA: {}".format(
            'public' if rx_add == 0b0 else 'random', ':'.join('%02X'%b for b in adv_a)))
        # print("LLData:", payload[12:])
    else:
        logger.warning("Unknown PDU type 0x%02x'%pdu_type")

    return addrs
