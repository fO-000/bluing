#!/usr/bin/env python3

from pyclui import blue, green, yellow, red, \
    DEBUG, INFO, WARNING, ERROR

from . import ServiceRecord


class HFServiceRecord(ServiceRecord):
    '''Hands-Free unit Service Record
    
    HFP Specification v1.8, Table 5.1: Service Record for the HF
    '''
    service_clses = [
        {'UUID': 0x111E, 'name': 'Handsfree'},
        {'UUID': 0x1203, 'name': 'GenericAudio'}
    ]
    
    SUPPORTED_FEATURES = 0x0311

    # See HFP Specification v1.8, Table 5.2: “SupportedFeatures” attribute bit 
    # mapping for the HF
    supported_features_bitmap = {
        0: 'EC and/or NR function', # LSB
        1: 'Call waiting or three-way calling',
        2: 'CLI presentation capability',
        3: 'Voice recognition activation',
        4: 'Remote volume control',
        5: 'Wide band speech',
        6: 'Enhanced Voice Recognition Status',
        7: 'Voice Recognition Text'
    }

    def __init__(self, record_xml:str):
        self.attrs = {
            self.SUPPORTED_FEATURES: {
                'Name': 'SupportedFeatures',
                'Parser': self.pp_supported_features
            }
        }
        super().__init__(record_xml)


    def pp_supported_features(self, val:int):
        '''Parse and print SupportedFeatures service attribute.
    
        val - Value of SupportedFeatures, Uint16
        '''
        print('\t0x%04X'%val)
        for i in range(len(self.supported_features_bitmap)):
            feature_name = self.supported_features_bitmap[i]
            print('\t\t'+(green(feature_name) if val >> i & 0x0001 else red(feature_name)))