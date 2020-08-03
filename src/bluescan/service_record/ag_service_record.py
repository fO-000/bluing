#!/usr/bin/env python3

from pyclui import blue, green, yellow, red, \
    DEBUG, INFO, WARNING, ERROR

from . import ServiceRecord


class AGServiceRecord(ServiceRecord):
    '''Autio Gateway Service Record
    
    See HFP Specification v1.8, Table 5.3: Service Record for the AG
    '''
    service_clses = [
        {'UUID': 0x111F, 'name': 'HandsfreeAudioGateway'},
        {'UUID': 0x1203, 'name': 'GenericAudio'}
    ]

    NETWORK            = 0x0301
    SUPPORTED_FEATURES = 0x0311

    network = {
        0x01: green('Ability to reject a call'),
        0x00: red('No ability to reject a call')
    }

    # See HFP Specification v1.8, Table 5.4: "SupportedFeatures" attribute bit 
    # mapping for the AG
    supported_features_bitmap = {
        0: 'Three-way calling', # LSB
        1: 'EC and/or NR function',
        2: 'Voice recognition function',
        3: 'In-band ring tone capability',
        4: 'Attach a phone number to a voice tag',
        5: 'Wide band speech',
        6: 'Enhanced Voice Recognition Status',
        7: 'Voice Recognition Text'
    }


    def __init__(self, record_xml:str):
        '''
        record_xml - Service record XML for Autio Gateway
        '''
        self.attrs = {
            self.NETWORK: {
                'Name': 'Network',
                'Parser': self.pp_network
            },

            self.SUPPORTED_FEATURES: {
                'Name': 'SupportedFeatures',
                'Parser': self.pp_supported_features
            },
        }

        super().__init__(record_xml)


    def pp_network(self, val:int):
        '''Parse and print Network service attribute.

        val - Value of Network, Uint8
        '''
        print('\t0x%02X'%val)
        print('\t\t'+self.network[val])


    def pp_supported_features(self, val:int):
        '''Parse and print SupportedFeatures service attribute.

        val  - Value of SupportedFeatures, Uint16
        '''
        print('\t0x%04X'%val)
        for i in range(len(self.supported_features_bitmap)):
            feature_name = self.supported_features_bitmap[i]
            print('\t\t'+(green(feature_name) if val >> i & 0x0001 else red(feature_name)))
