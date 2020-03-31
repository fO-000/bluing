#!/usr/bin/env python3

import xml.etree.ElementTree as ET

universal_attrs = {
    '0x0000': 'ServiceRecordHandle',
    '0x0001': 'ServiceClassIDList',
    '0x0002': 'ServiceRecordState',
    '0x0003': 'ServiceID',
    '0x0004': 'ProtocolDescriptorList',
    '0x0005': 'BrowseGroupList',
    '0x0006': 'LanguageBaseAttributeIDList',
    '0x0007': 'ServiceInfoTimeToLive',
    '0x0008': 'ServiceAvailability',
    '0x0009': 'BluetoothProfileDescriptorList',
    '0x000A': 'DocumentationURL',
    '0x000B': 'ClientExecutableURL',
    '0x000C': 'IconURL',
    '0x000D': 'AdditionalProtocolDescriptorLists'
}


class MAP:
    '''Message Access Profile'''
    # Attributes
    GOEP_L2CAP_PSM = '0x0200'
    MAS_INSTANCE_ID = '0x0315'
    SUPPORTED_MESSAGE_TYPES = '0x0316'
    MAP_SUPPORTED_FEATURES = '0x0317'
    
    attrs = {
        GOEP_L2CAP_PSM: 'GoepL2capPsm (MAP v1.2 and later)',
        MAS_INSTANCE_ID: 'MASInstanceID',
        SUPPORTED_MESSAGE_TYPES: 'SupportedMessageTypes',
        MAP_SUPPORTED_FEATURES: 'MapSupportedFeatures (MAP v1.2 and later)'}
    attrs.update(universal_attrs)
    
    service_class = {
        '0x1132': 'Message Access Server',
        '0x1133': 'Message Notification Server'}

    def __init__(self):
        self.msg_format_ver1_1 = False

    @classmethod
    def parse_sdp_record(cls, xml:str):
        root = ET.fromstring(xml)
        attrs = root.findall('./attribute')
        print()
        for attr in attrs:
            try:
                print(attr.attrib['id']+':', MAP.attrs[attr.attrib['id']])
                if attr.attrib['id'] == cls.SUPPORTED_MESSAGE_TYPES:
                    uint8 = attr.find('./uint8')
                    print('    uint8 value =', uint8.attrib['value'])
                    value = int(uint8.attrib['value'][2:], base=16)
                    cls.parse_supported_msg_types(value)

                elif attr.attrib['id'] == cls.MAP_SUPPORTED_FEATURES:
                    uint32 = attr.find('./uint32')
                    print('    uint32 value =', uint32.attrib['value'])
                    value = int(uint32.attrib['value'][2:], base=16)
                    cls.parse_map_supported_features(value)


            except KeyError as e:
                print(e)

    @classmethod
    def parse_supported_msg_types(cls, value:int):
        '''The value parameter is uint8.'''
        print('    RFU (7-5)', value>>5)
        print('    Bit 4 = IM', (value>>4)&0x01)
        print('    Bit 3 = MMS', (value>>3)&0x01)
        print('    Bit 2 = SMS_CDMA', (value>>2)&0x01)
        print('    Bit 1 = SMS_GSM', (value>>1)&0x01)
        print('    Bit 0 = EMAIL', (value)&0x01)

    
    @classmethod
    def parse_map_supported_features(cls, value:int):
        '''The value parameter is uint32.'''
        #print('        [DEBUG] value', value)
        print('    RFU (31-23)', value>>23)
        print('    Bit 22 = Message Forwarding', (value>>22)&0x00000001)
        print('    Bit 21 = Owner Status', (value>>21)&0x00000001)
        print('    Bit 20 = Conversationlisting', (value>>20)&0x00000001)
        print('    Bit 19 = MapSupportedFeatures in Connect Request', (value>>19)&0x00000001)
        print('    Bit 18 = UTC Offset Timestamp Format', (value>>18)&0x00000001)
        print('    Bit 17 = Notification Filtering', (value>>17)&0x00000001)
        print('    Bit 16 = PBAP Contact Cross Reference', (value>>16)&0x00000001)
        print('    Bit 15 = Participant Chat State Change Notification', (value>>15)&0x00000001)
        print('    Bit 14 = Participant Presence Change Notification', (value>>14)&0x00000001)
        print('    Bit 13 = Conversation Version Counters', (value>>13)&0x00000001)
        print('    Bit 12 = Folder Version Counter', (value>>12)&0x00000001)
        print('    Bit 11 = Database Identifier', (value>>11)&0x00000001)
        print('    Bit 10 = Persistent Message Handles', (value>>10)&0x00000001)
        print('    Bit 9 = MessagesListing Format Version 1.1', (value>>9)&0x00000001)
        
        print('    Bit 8 = Message Format Version 1.1', (value>>8)&0x00000001)
        # self.msg_format_ver1_1 = bool((value>>8)&0x00000001)

        print('    Bit 7 = Event Report Version 1.2', (value>>7)&0x00000001)
        print('    Bit 6 = Extended Event Report 1.1', (value>>6)&0x00000001 )
        print('    Bit 5 = Instance Information Feature', (value>>5)&0x00000001)
        print('    Bit 4 = Delete Feature', (value>>4)&0x00000001)
        print('    Bit 3 = Uploading Feature', (value>>3)&0x00000001)
        print('    Bit 2 = Browsing Feature', (value>>2)&0x00000001)
        print('    Bit 1 = Notification Feature', (value>>1)&0x00000001)
        print('    Bit 0 = Notification Registration Feature', value&0x00000001)


def __test():
    xml_str = '''<?xml version="1.0" encoding="UTF-8" ?>
<record>
    <attribute id="0x0000">
        <uint32 value="0x00010009" />
    </attribute>
    <attribute id="0x0001">
        <sequence>
            <uuid value="0x1132" />
        </sequence>
    </attribute>
    <attribute id="0x0004">
        <sequence>
            <sequence>
                <uuid value="0x0100" />
            </sequence>
            <sequence>
                <uuid value="0x0003" />
                <uint8 value="0x1a" />
            </sequence>
            <sequence>
                <uuid value="0x0008" />
            </sequence>
        </sequence>
    </attribute>
    <attribute id="0x0005">
        <sequence>
            <uuid value="0x1002" />
        </sequence>
    </attribute>
    <attribute id="0x0009">
        <sequence>
            <sequence>
                <uuid value="0x1134" />
                <uint16 value="0x0102" />
            </sequence>
        </sequence>
    </attribute>
    <attribute id="0x0100">
        <text value="SMS/MMS " />
    </attribute>
    <attribute id="0x0200">
        <uint16 value="0x1029" />
    </attribute>
    <attribute id="0x0315">
        <uint8 value="0x00" />
    </attribute>
    <attribute id="0x0316">
        <uint8 value="0x0e" />
    </attribute>
    <attribute id="0x0317">
        <uint32 value="0x0000007f" />
    </attribute>
</record>
'''
    MAP.parse_sdp_record(xml_str)


if __name__ == "__main__":
    __test()
