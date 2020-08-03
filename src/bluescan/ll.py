#!/usr/bin/env python3

from pyclui import blue, green, yellow, red, \
    DEBUG, INFO, WARNING, ERROR

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
ADV_IND         = 0b0000
ADV_DIRECT_IND  = 0b0001
ADV_NONCONN_IND = 0b0010
SCAN_REQ        = 0b0011
SCAN_RSP        = 0b0100
CONNECT_IND     = 0b0101
ADV_SCAN_IND    = 0b0110
ADV_EXT_IND     = 0b0111



def pp_adv_phy_channel_pdu(pdu:bytes):
    '''Parse and print advertising physical channel PDU'''
    header = pdu[:2]
    payload = pdu[2:]
    
    tx_add = header[0] & TX_ADD_MSK >> TX_ADD_POS
    rx_add = header[0] & RX_ADD_MSK >> RX_ADD_POS
    pdu_type = header[0] & PDU_TYPE_MSK >> PDU_TYPE_POS

    if tx_add != 0b0 and rx_add != 0b0:
        return

    if pdu_type == ADV_IND:
        adv_a = payload[:6]
        print('[ADV_IND]', 'AdvA:', adv_a)
    elif pdu_type == ADV_DIRECT_IND:
        adv_a = payload[:6]
        target_a = payload[6:]
        print('[ADV_DIRECT_IND]', 'AdvA:', adv_a, 'TargetA:', target_a)
    elif pdu_type == ADV_NONCONN_IND:
        adv_a = payload[:6]
        print('[ADV_NONCONN_IND]', 'AdvA:', adv_a)
    elif pdu_type == SCAN_REQ:
        scan_a = payload[:6]
        adv_a = payload[6:]
        print('[SCAN_REQ]', 'ScanA:', scan_a, 'AdvA:', adv_a)
    elif pdu_type == SCAN_RSP:
        adv_a = payload[:6]
        print('[SCAN_RSP]', 'AdvA:', adv_a)
    elif pdu_type == CONNECT_IND:
        init_a = payload[:6]
        adv_a = payload[6:]
        print('[CONNECT_IND]', 'InitA:', init_a, 'AdvA:', adv_a)
    elif pdu_type == ADV_SCAN_IND:
        adv_a = payload[:6]
        print('[ADV_SCAN_IND]', 'AdvA:', adv_a)
    elif pdu_type == ADV_EXT_IND:
        print('[ADV_EXT_IND]')
    else:
        print('[WARNING] Unknown PDU type 0x%02x'%pdu_type)
