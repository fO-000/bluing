#!/usr/bin/env python3

from pyclui import blue, green, yellow, red, \
    DEBUG, INFO, WARNING, ERROR
from . import ServiceRecord


class MCEServiceRecord(ServiceRecord):
    '''Message Client Equipment Service Record
    
    See MAP Specification v1.4.2, Table 7.2: SDP Record for the Message 
    Notification Service on the MCE Device
    '''
    service_clses = [
        {'UUID': 0x1133, 'name': 'Message Notification Server'}
    ]
    
    GOEP_L2CAP_PSM         = 0x0200
    MAP_SUPPORTED_FEATURES = 0x0317

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
        19: 'Reserved', # The only difference from MapSupportedFeatures of MSE
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
                'Parser': lambda val: print('\t0x%04X'%val)
            },

            self.MAP_SUPPORTED_FEATURES: { # MAP v1.2 and later
                'Name':'MapSupportedFeatures',
                'Parser': self.pp_map_supported_features
            }
        }
        
        super().__init__(record_xml)


    @classmethod
    def pp_map_supported_features(cls, val: int):
        '''Parse and print MapSupportedFeatures (MAP v1.2 and later).
        
        val - Value of MapSupportedFeatures, uint32
        '''
        print('\t0x%08X'%val)
        for i in range(len(cls.map_supported_features_bitmap)):
            feature_name = cls.map_supported_features_bitmap[i]
            print('\t\t', end=' ')
            if i < 23:
                print(green(feature_name) if val >> i & 0x01 else red(feature_name))
            else:
                print(val >> i & 0x01, 'RFU')
