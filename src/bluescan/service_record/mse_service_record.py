#!/usr/bin/env python3

from pyclui import blue, green, yellow, red, \
    DEBUG, INFO, WARNING, ERROR
from . import ServiceRecord


class MSEServiceRecord(ServiceRecord):
    '''Message Server Equipment Service Record

    See MAP Specification v1.4.2, Table 7.1: SDP Record for the Message Access 
    Service on the MSE Device
    '''
    service_clses = [
        {'UUID': 0x1132, 'name': 'Message Access Server'}
    ]

    GOEP_L2CAP_PSM          = 0x0200
    MAS_INSTANCE_ID         = 0x0315
    SUPPORTED_MESSAGE_TYPES = 0x0316
    MAP_SUPPORTED_FEATURES  = 0x0317

    supported_msg_types_bitmap = {
        0: 'EMAIL', # LSB
        1: 'SMS_GSM',
        2: 'SMS_CDMA',
        3: 'MMS',
        4: 'IM',
        5: 'Reserved for Future Use',
        6: 'Reserved for Future Use',
        7: 'Reserved for Future Use'
    }

    map_supported_features_bitmap = {
        0: 'Notification Registration Feature', # LSB
        1: 'Notification Feature',
        2: 'Browsing Feature',
        3: 'Uploading Feature',
        4: 'Delete Feature',
        5: 'Instance Information Feature',
        6: 'Extended Event Report 1.1', 
        7: 'Event Report Version 1.2',
        8: 'Message Format Version 1.1',
        9: 'MessagesListing Format Version 1.1',
        10: 'Persistent Message Handles',
        11: 'Database Identifier',
        12: 'Folder Version Counter',
        13: 'Conversation Version Counters',
        14: 'Participant Presence Change Notification',
        15: 'Participant Chat State Change Notification',
        16: 'PBAP Contact Cross Reference',
        17: 'Notification Filtering',
        18: 'UTC Offset Timestamp Format',

        # The only difference from MapSupportedFeatures of MSE
        19: 'MapSupportedFeatures in Connect Request',  
        20: 'Conversation listing',
        21: 'Owner Status',
        22: 'Message Forwarding',
        23: 'Reserved for Furture Use',
        24: 'Reserved for Furture Use',
        25: 'Reserved for Furture Use',
        26: 'Reserved for Furture Use',
        27: 'Reserved for Furture Use',
        28: 'Reserved for Furture Use',
        29: 'Reserved for Furture Use',
        30: 'Reserved for Furture Use',
        31: 'Reserved for Furture Use'
    }

    def __init__(self, record_xml:str):
        self.attrs = {
            self.GOEP_L2CAP_PSM: { # MAP v1.2 and later
                'Name': '​GoepL2capPsm', 
                'Parser': lambda val: print('\t0x%02x'%val)
            },

            self.MAS_INSTANCE_ID: {
                'Name': 'MASInstanceID',
                'Parser': lambda val: print('\t0x%02x'%val)
            },

            self.SUPPORTED_MESSAGE_TYPES: {
                'Name': 'SupportedMessageTypes',
                'Parser': self.pp_supported_msg_types
            },

            self.MAP_SUPPORTED_FEATURES: { # MAP v1.2 and later
                'Name': 'MapSupportedFeatures',
                'Parser': self.pp_map_supported_features
            }
        }
        super().__init__(record_xml)


    def pp_supported_msg_types(self, val:int):
        '''Parse and print SupportedMessageTypes service attribute.
        
        val - Value of SupportedMessageTypes, uint8
        '''
        print('\t0x%02X'%val)
        for i in range(len(self.supported_msg_types_bitmap)):
            type_name = self.supported_msg_types_bitmap[i]
            print('\t\t', end=' ')
            if i < 5:
                print(green(type_name) if val >> i & 0x01 else red(type_name))
            else:
                print(val >> i & 0x01, 'RFU')


    def pp_map_supported_features(self, val:int):
        '''Parse and print MapSupportedFeatures (MAP v1.2 and later) service 
        attribute.
        
        val - Value of MapSupportedFeatures, uint32
        '''
        print('\t0x%08X'%val)
        for i in range(len(self.map_supported_features_bitmap)):
            feature_name = self.map_supported_features_bitmap[i]
            print('\t\t', end=' ')
            if i < 23:
                print(green(feature_name) if val >> i & 0x01 else red(feature_name))
            else:
                print(val >> i & 0x01, 'RFU')
