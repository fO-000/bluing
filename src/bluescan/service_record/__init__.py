#!/usr/bin/env python3

import io
import pkg_resources
from xml.etree import ElementTree

from pyclui import blue, green, yellow, red, \
    DEBUG, INFO, WARNING, ERROR

from .. import service_cls_profile_ids


__all__ = ['ag_service_record', 'hf_service_record', 'hid_service_record', 
    'mce_service_record', 'mse_service_record']



# Only used in the ProfileDescriptorList attribute
protocol_ids_file = pkg_resources.resource_stream(__name__, "../res/sdp_ProfileDescriptorList_protocol_ids.txt")
protocol_ids_file = io.TextIOWrapper(protocol_ids_file)
protocol_ids = {}

for line in protocol_ids_file:
    items = line.strip().split('\t')
    if items[0] == 'Protocol Name':
        continue
    # print(items)
    uuid = items.pop(1).lower()
    protocol_ids[uuid] = {
        'Name': items[0],
        'spec': items[1]
    }


class ServiceRecord:
    '''SDP service record'''

    # Universal Attributes
    SERVICE_RECORD_HANDLE                = 0x0000
    SERVICE_CLASS_ID_LIST                = 0x0001
    SERVICE_RECORD_STATE                 = 0x0002
    SERVICE_ID                           = 0x0003
    PROTOCOL_DESCRIPTOR_LIST             = 0x0004
    BROWSE_GROUP_LIST                    = 0x0005
    LANGUAGE_BASE_ATTRIBUTE_ID_LIST      = 0x0006
    SERVICE_INFO_TIME_TO_LIVE            = 0x0007
    SERVICE_AVAILABILITY                 = 0x0008
    BLUETOOTH_PROFILE_DESCRIPTOR_LIST    = 0x0009
    DOCUMENTATION_URL                    = 0x000a
    CLIENT_EXECUTABLE_URL                = 0x000b
    ICON_URL                             = 0x000c
    ADDITIONAL_PROTOCOL_DESCRIPTOR_LISTS = 0x000d


    # See https://www.bluetooth.com/specifications/assigned-numbers/service-discovery/
    # Table 5: Attribute Identifiers and BLUETOOTH CORE SPECIFICATION Version 
    # 5.2 | Vol 3, Part B page 1247
    SERVICE_NAME        = 0x0000
    SERVICE_DESCRIPTION = 0x0001
    PROVIDER_NAME       = 0x0002

    def __init__(self, record_xml:str):
        '''
        record_xml - A single service record XML.
        '''
        self.universal_attrs = {
            self.SERVICE_RECORD_HANDLE: {
                # <attribute id="0x0000">
                #     <uint32 value="0x00010001" />
                # </attribute>
                'Name': 'ServiceRecordHandle',
                'Parser': lambda val: print('\t0x%08x'%val)
            },

            self.SERVICE_CLASS_ID_LIST: {
                'Name': 'ServiceClassIDList',
                'Parser': self.pp_service_cls_list
            },

            self.SERVICE_RECORD_STATE: { # 32-bit unsigned integer
                'Name': 'ServiceRecordState',
                'Parser': lambda val: print('\t0x%08x: to be parsed'%val)
            },

            self.SERVICE_ID: { # UUID
                'Name': 'ServiceID',
                'Parser': lambda val: print('\t' + val + ': to be parsed')
            },

            self.PROTOCOL_DESCRIPTOR_LIST: {
                'Name': 'ProtocolDescriptorList',
                'Parser': self.pp_protocol_descp_list
            },

            self.BROWSE_GROUP_LIST: {
                'Name': 'BrowseGroupList',
                'Parser': self.pp_browse_group_list
            },

            self.LANGUAGE_BASE_ATTRIBUTE_ID_LIST: {
                'Name': 'LanguageBaseAttributeIDList',
                'Parser': self.pp_lang_base_attr_id_list
            },

            self.SERVICE_INFO_TIME_TO_LIVE: { # 32-bit unsigned integer
                'Name': 'ServiceInfoTimeToLive',
                'Parser': lambda val: print('\t0x%08x: to be parsed'%val)
            },

            self.SERVICE_AVAILABILITY: { # 8-bit unsigned integer
                'Name': 'ServiceAvailability',
                'Parser': lambda val: print('\t0x%02x: to be parsed'%val)
            },

            self.BLUETOOTH_PROFILE_DESCRIPTOR_LIST: {
                'Name': 'BluetoothProfileDescriptorList',
                'Parser': self.pp_bt_profile_descp_list
            },

            self.DOCUMENTATION_URL: { # URL
                'Name': 'DocumentationURL',
                'Parser': lambda val: print('\t' + val + ': to be parsed')
            },

            self.CLIENT_EXECUTABLE_URL: { # URL
                'Name': 'ClientExecutableURL', 
                'Parser': lambda val: print('\t' + val + ': to be parsed')
            },

            self.ICON_URL: { # URL
                'Name': 'IconURL',
                'Parser': lambda val: print('\t' + val + ': to be parsed')
            },

            self.ADDITIONAL_PROTOCOL_DESCRIPTOR_LISTS: {
                'Name': 'AdditionalProtocolDescriptorList',
                'Parser': self.pp_additional_protocol_descp_lists
            }
        }

        self.universal_attr_offsets = {
            self.SERVICE_NAME: {
                'Name': 'ServiceName',
                'Parser': lambda val: print('\t' + val)
            },

            self.SERVICE_DESCRIPTION: {
                'Name': 'ServiceDescription',
                'Parser': lambda val: print('\t' + val)
            },

            self.PROVIDER_NAME: {
                'Name': 'ProviderName',
                'Parser': lambda val: print('\t' + val)
            }
        }

        self.record_xml = record_xml
        self.service_clses = []
        self.attr_id_bases = []


    def pp(self):
        '''Parse and print current service record.'''
        attrs = ElementTree.fromstring(self.record_xml).findall('./attribute')
        for attr in attrs: # Parse service attributes one by one.
            self.pp_attr(attr)


    def pp_attr(self, attr:ElementTree.Element):
        '''Parse and print the service attribute.

        attr - Example:
                   <attribute id="0x????">
                       ... ... 
                   </attribute>
        '''
        attr_id = int(attr.attrib['id'][2:], base=16)
        val_type = attr.find('./').tag
        if 'uint' in val_type:
            val = int(attr.find('./'+val_type).attrib['value'][2:], base=16)
        elif val_type == 'sequence':
            val = attr.find('./'+val_type)
        else:
            val = attr.find('./'+val_type).attrib['value']

        # Parse and print three universal attribute ID offsets
        for base in self.attr_id_bases:    
            offset = attr_id - base
            try:
                print('0x%04x:'%attr_id, 
                    self.universal_attr_offsets[offset]['Name'], 
                    '(%s)'%val_type)
            
                self.universal_attr_offsets[offset]['Parser'](val)
                return
            except KeyError:
                continue

        try:
            # The code for parsing a service attribute is divided into two parts.
            # One of the part is parsing the universal attribute and the other part is 
            # parsing the non universal attribute. This is the first part.
            print('0x%04x:'%attr_id, self.universal_attrs[attr_id]['Name'], 
                '(%s)'%val_type)
            self.universal_attrs[attr_id]['Parser'](val)
        except KeyError:
            # The code that parses a service attribute is divided into two parts.
            # One of the part is parsing the universal attribute and the other part is 
            # parsing the non universal attribute. This is the second part.
            from .ag_service_record import AGServiceRecord
            from .hf_service_record import HFServiceRecord
            from .hid_service_record import HIDServiceRecord
            from .mce_service_record import MCEServiceRecord
            from .mse_service_record import MSEServiceRecord

            # Guess if the attribute is one of the universal attribute offsets.
            offset = attr_id - 0x0100
            try:
                print('0x%04x:'%attr_id, 
                    self.universal_attr_offsets[offset]['Name'], '(guess)', 
                    '(%s)'%val_type)
                self.universal_attr_offsets[offset]['Parser'](val)
                return
            except KeyError:
                pass

            if self.service_clses[0] == HFServiceRecord.service_clses[0]['UUID']:
                hfsr = HFServiceRecord(self.record_xml)
                print('0x%04x:'%attr_id, hfsr.attrs[attr_id]['Name'], 
                    '(%s)'%val_type)
                hfsr.attrs[attr_id]['Parser'](val)
            elif self.service_clses[0] == AGServiceRecord.service_clses[0]['UUID']:
                agsr = AGServiceRecord(self.record_xml)
                print('0x%04x:'%attr_id, agsr.attrs[attr_id]['Name'], 
                    '(%s)'%val_type)
                agsr.attrs[attr_id]['Parser'](val)
            elif self.service_clses[0] == MSEServiceRecord.service_clses[0]['UUID']:
                msesr = MSEServiceRecord(self.record_xml)
                print('0x%04x:'%attr_id, msesr.attrs[attr_id]['Name'], 
                    '(%s)'%val_type)
                msesr.attrs[attr_id]['Parser'](val)
            elif self.service_clses[0] == MCEServiceRecord.service_clses[0]['UUID']:
                mcesr = MCEServiceRecord(self.record_xml)
                print('0x%04x:'%attr_id, mcesr.attrs[attr_id]['Name'], 
                    '(%s)'%val_type)
                mcesr.attrs[attr_id]['Parser'](val)
            elif self.service_clses[0] == HIDServiceRecord.service_clses[0]['UUID']:
                hidsr = HIDServiceRecord(self.record_xml)
                print('0x%04x:'%attr_id, hidsr.attrs[attr_id]['Name'], 
                    '(%s)'%val_type)
                hidsr.attrs[attr_id]['Parser'](val)
            else:
                print('0x%04x:'%attr_id, red('unknown'))
                for elem in list(attr):
                    s = [i.strip() for i in ElementTree.tostring(elem).decode().strip().replace('\t', '').split('\n')]
                    # print('DEBUG', s)
                    for i in s:
                        print('\t' + i)


    def pp_service_cls_list(self, seq:ElementTree.Element):
        '''Parse and print ServiceClassIDList (0x0001).
        
        seq - Example:
                  <sequence>
                      <uuid value="0x110e" />
                      <uuid value="0x110f" />
                  </sequence>
        '''
        uuids = seq.findall('./uuid')
        for uuid in uuids:
            uuid = uuid.attrib['value']
            print('\t'+uuid+':', end=' ')
            
            try:
                uuid = int(uuid[2:], base=16)
            except ValueError: # Full UUID
                pass

            self.service_clses.append(uuid)

            try:
                if 'Service Class' in service_cls_profile_ids[uuid]['Allowed Usage']:
                    name = service_cls_profile_ids[uuid]['Name']
                    print(green(name))
                else:
                    print(red('unknown'))
            except KeyError:
                if uuid == 0x1800:
                    print(green('Generic Access'))
                elif uuid == 0x1801:
                    print(green('Generic Attribute'))
                else:
                    print(red('unknown'))


    def pp_protocol_descp_list(self, seq:ElementTree.Element):
        '''Parse and print ProtocolDescriptorList (0x0004).
        
        seq - Example:
                  <sequence>
                      <sequence>
                          <uuid value="0x0100" />
                          <uint16 value="0x001f" />
                      </sequence>
                    
                      <sequence>
                          <uuid value="0x0007" />
                          <uint16 value="0x0001" />
                          <uint16 value="0x0003" />
                      </sequence>
                  </sequence>
        '''
        protocols = seq.findall('./sequence')
        for protocol in protocols:
            uuid = protocol.find('./uuid').attrib['value']
            print('\t'+uuid+':', end=' ')
            try:
                name = protocol_ids[uuid]['Name']
                
                print(name)
                # print('\t\t', protocol_ids[uuid]['Specification'])
                if name == 'L2CAP':
                    try:
                        psm = protocol.find('./uint16').attrib['value']
                        print('\t\t' + 'PSM:', psm)
                    except AttributeError:
                        pass
                elif name == 'RFCOMM':
                    channel = protocol.find('./uint8').attrib['value']
                    print('\t\tchannel:', channel)
                elif name in ('AVDTP', 'AVCTP'): # 音频分发、音频控制
                    version = int(protocol.find('./uint16').attrib['value'][2:], base=16)
                    print('\t\tv%d.%d'%(version>>8, version&0xFF))
                    # Stream End Point 
                    #print('\t\t' + 'SEP:', sep)
                elif name in ('BNEP'):
                    version = protocol.find('./uint16').attrib['value']
                    print('\t\tversion:', version)
                    uint16s = protocol.find('./sequence').findall('./uint16')
                    for val in uint16s:
                        print('\t\tuint16:', val.attrib['value'])
                else:
                    for elem in list(protocol)[1:]:
                        s = ElementTree.tostring(elem).decode().strip().replace('\t', '').split('\n')
                        for i in s:
                            print('\t\t' + i)
            except KeyError:
                print('(Unknown)')


    def pp_browse_group_list(self, seq:ElementTree.Element):
        '''Parse and print BrowseGroupList (0x0005).

        seq - Example:
                  <sequence>
                      <uuid value="0x1002" />
                  </sequence>
        '''
        uuids = seq.findall('./uuid')
        for uuid in uuids:
            uuid  = uuid.attrib['value']
            print('\t'+uuid+':', end=' ')
            
            if uuid == "0x1002":
                print(green('PublicBrowseRoot'))
            else:
                print('Unknown')


    def pp_lang_base_attr_id_list(self, seq:ElementTree.Element):
        '''Parse and print LanguageBaseAttributeIDList (0x0006).

        seq - Example:
                  <sequence>
                      <uint16 value="0x656e" />
                      <uint16 value="0x006a" />
                      <uint16 value="0x0100" />
                  </sequence>
        '''
        values = seq.findall('./uint16')
        triplets = []
        for i in range(0, len(values), 3):
            triplets.append(values[i:i+3])
        #print(triplets)
        
        for triplet in triplets:
            lang_name = triplet[0].attrib['value']
            encoding = triplet[1].attrib['value']
            base = triplet[2].attrib['value']
            print('\tlanguage name:', lang_name)
            print('\tencoding:', encoding)
            print('\tattribute ID base:', base)
            self.attr_id_bases.append(int(base[2:], base=16))


    def pp_bt_profile_descp_list(self, seq:ElementTree.Element):
        '''Parse and print BluetoothProfileDescriptorList (0x0009).
        
        seq - Example:
                  <sequence>
                      <sequence>
                          <uuid value="0x1108" />
                          <uint16 value="0x0102" />
                      </sequence>
                  </sequence>
        '''
        profiles = seq.findall('./sequence')
        for profile in profiles:
            uuid = profile.find('./uuid').attrib['value']
            print('\t'+uuid+':', end=' ')
            try:
                uuid = int(uuid[2:], base=16)
            except ValueError:
                pass

            try:
                if 'Profile' in service_cls_profile_ids[uuid]['Allowed Usage']:
                    name = service_cls_profile_ids[uuid]['Name']
                    print(green(name), end=' ')
                    # print('\t\t', service_cls_profile_ids[uuid]['Specification'])
                else:
                    print(red('unknown'), end=' ')
                version = int(profile.find('./uint16').attrib['value'][2:], base=16)
                print(green('v%d.%d'%(version>>8, version&0xFF)))
            except KeyError:
                print(red('unknown'))


    def pp_additional_protocol_descp_lists(self, seq:ElementTree.Element):
        '''Parse and print AdditionalProtocolDescriptorLists (0x000D).
        
        seq - Example:
                  <sequence>
                      <sequence>
                          <sequence>
                              <uuid value="0x0100" />
                              <uint16 value="0x001b" />
                          </sequence>

                          <sequence>
                              <uuid value="0x0017" />
                              <uint16 value="0x0103" />
                          </sequence>
                      </sequence>
                  </sequence>
        '''
        sequences = seq.findall('./sequence')
        for sequence in sequences:
            self.pp_protocol_descp_list(sequence)


def __test():
    record_xml = '''<?xml version="1.0" encoding="UTF-8" ?>
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
    ServiceRecord(record_xml).pp()


if __name__ == '__main__':
    __test()
