#!/usr/bin/env python3

import io
import sys
import subprocess
import pkg_resources
from xml.etree import ElementTree as ET

from bluetooth import find_service

#sys.path.append('/mnt/hgfs/OneDrive/Projects/bluescan/src/')
from bluescan import BlueScanner
from bluescan.ui import blue
from bluescan.ui import yellow
from bluescan.ui import red


service_cls_profile_ids_file = pkg_resources.resource_stream(__name__, "res/sdp-service-class-and-profile-ids.txt")
service_cls_profile_ids_file = io.TextIOWrapper(service_cls_profile_ids_file)
service_cls_profile_ids = {}

# 需要手动编辑的 Service Class 如下：
#     IrMCSyncCommand
#     Headset – HS
for line in service_cls_profile_ids_file:
    items = line.strip().split('\t')
    if items[0] == 'Service Class Name':
        continue
    #print(items)
    uuid = items.pop(1).lower()
    service_cls_profile_ids[uuid] = {
        'Name': items[0],
        'Specification': items[1],
        'Allowed Usage': items[2]
    }


# Only used in the ProfileDescriptorList attribute
protocol_ids_file = pkg_resources.resource_stream(__name__, "res/sdp_ProfileDescriptorList_protocol_ids.txt")
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

# Universal Attributes
SERVICE_RECORD_HANDLE                = '0x0000'
SERVICE_CLASS_ID_LIST                = '0x0001'
SERVICE_RECORD_STATE                 = '0x0002' 
SERVICE_ID                           = '0x0003' 
PROTOCOL_DESCRIPTOR_LIST             = '0x0004' 
BROWSE_GROUP_LIST                    = '0x0005' 
LANGUAGE_BASE_ATTRIBUTE_ID_LIST      = '0x0006' 
SERVICE_INFO_TIME_TO_LIVE            = '0x0007' 
SERVICE_AVAILABILITY                 = '0x0008' 
BLUETOOTH_PROFILE_DESCRIPTOR_LIST    = '0x0009' 
DOCUMENTATION_URL                    = '0x000a'
CLIENT_EXECUTABLE_URL                = '0x000b'
ICON_URL                             = '0x000c'
ADDITIONAL_PROTOCOL_DESCRIPTOR_LISTS = '0x000d'

universal_attrs = {
    SERVICE_RECORD_HANDLE:                'ServiceRecordHandle',
    SERVICE_CLASS_ID_LIST:                'ServiceClassIDList',
    SERVICE_RECORD_STATE:                 'ServiceRecordState',
    SERVICE_ID:                           'ServiceID',
    PROTOCOL_DESCRIPTOR_LIST:             'ProtocolDescriptorList',
    BROWSE_GROUP_LIST:                    'BrowseGroupList',
    LANGUAGE_BASE_ATTRIBUTE_ID_LIST:      'LanguageBaseAttributeIDList',
    SERVICE_INFO_TIME_TO_LIVE:            'ServiceInfoTimeToLive',
    SERVICE_AVAILABILITY:                 'ServiceAvailability',
    BLUETOOTH_PROFILE_DESCRIPTOR_LIST:    'BluetoothProfileDescriptorList',
    DOCUMENTATION_URL:                    'DocumentationURL',
    CLIENT_EXECUTABLE_URL:                'ClientExecutableURL',
    ICON_URL:                             'IconURL',
    ADDITIONAL_PROTOCOL_DESCRIPTOR_LISTS: 'AdditionalProtocolDescriptorLists'
}


class SDPScanner(BlueScanner):

    def scan(self, addr:str):
        exitcode, output = subprocess.getstatusoutput('sdptool records --xml ' + addr)
        if exitcode != 0:
            sys.exit(exitcode)

        self.parse_sdptool_output(output)
        
        # services = find_service(address=addr)
        # # print(services)
        # # print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        # for service in services:
        #     print('Name:', service['name'] )
        #     print('ProtocolDescriptorList', service['protocol'])
        #     print('channel/PSM', service['port'])
        #     print('ServiceClassIDList:', service['service-classes'])
        #     print('Profiles:', service['profiles'])
        #     print('Description:', service['description'])
        #     print('Provider:', service['provider'])
        #     print('ServiceID', service['service-id'])
        #     print()


    @classmethod
    def parse_sdptool_output(cls, output:str):
        record_xmls = output.split('<?xml version="1.0" encoding="UTF-8" ?>\n\n')[1:]
        print('Number of service records:', len(record_xmls), '\n\n')

        for record_xml in record_xmls:
            print(blue('Service Record'))
            cls.pp_record_xml(record_xml)
            print('\n')


    @classmethod
    def pp_record_xml(cls, xml:str):
        '''Parse and Print Service Record XML

        xml -- xml for a single service record
        '''
        root = ET.fromstring(xml)
        attrs = root.findall('./attribute')
        for attr in attrs:
            try:
                attr_id = attr.attrib['id']
                print(attr_id+':', universal_attrs[attr.attrib['id']]+' ', end='')
                if attr_id == SERVICE_RECORD_HANDLE:
                    print('(uint32)')
                    SDPParser.pp_service_record_hdl(attr)
                elif attr_id == SERVICE_CLASS_ID_LIST:
                    print('(sequence)')
                    SDPParser.pp_service_cls_list(attr)
                elif attr_id == SERVICE_RECORD_STATE:
                    pass
                elif attr_id == SERVICE_ID:
                    pass
                elif attr_id == PROTOCOL_DESCRIPTOR_LIST:
                    print('(sequence)')
                    SDPParser.pp_protocol_descp_list(attr)
                elif attr_id == BROWSE_GROUP_LIST:
                    print('(sequence)')
                    SDPParser.pp_browse_group_list(attr)
                elif attr_id == LANGUAGE_BASE_ATTRIBUTE_ID_LIST:
                    print('(sequence)')
                    SDPParser.pp_lang_base_attr_id_list(attr)
                # elif attr_id == SERVICE_INFO_TIME_TO_LIVE:
                # elif attr_id == SERVICE_AVAILABILITY:
                elif attr_id == BLUETOOTH_PROFILE_DESCRIPTOR_LIST:
                    print('(sequence)')
                    SDPParser.pp_bt_profile_descp_list(attr)
                # elif attr_id == DOCUMENTATION_URL:
                # elif attr_id == CLIENT_EXECUTABLE_URL:
                # elif attr_id == ICON_URL:
                elif attr_id == ADDITIONAL_PROTOCOL_DESCRIPTOR_LISTS:
                    print('(sequence)')
                    SDPParser.pp_additional_protocol_descp_lists(attr)

            except KeyError:
                print(attr_id+': unknown')
                for elem in list(attr):
                    print('    '+ET.tostring(elem).decode().strip())


class SDPParser:
    @classmethod
    def pp_service_record_hdl(cls, attr:ET.Element):
        handle = attr.find('./uint32')
        print(' '*4 + handle.attrib['value'])

    @classmethod
    def pp_service_cls_list(cls, attr:ET.Element):
        sequence = attr.find('./sequence')
        uuids = sequence.findall('./uuid')
        for uuid in uuids:
            uuid = uuid.attrib['value']
            try:
                print('    uuid:', uuid, end=' ')
                if 'Service Class' in service_cls_profile_ids[uuid]['Allowed Usage']:
                    print('('+service_cls_profile_ids[uuid]['Name']+')')
                else:
                    print('(Unknown)')
            except KeyError:
                print('(Unknown)')

    @classmethod
    def pp_protocol_descp_list(cls, attr:ET.Element):
        sequence = attr.find('./sequence')
        protocols = sequence.findall('./sequence')
        for protocol in protocols:
            uuid = protocol.find('./uuid').attrib['value']
            try:
                name = protocol_ids[uuid]['Name']
                print('    uuid:', uuid, end=' ')
                print('('+name+')')
                # print('         ', protocol_ids[uuid]['Specification'])
                if name == 'L2CAP':
                    try:
                        psm = protocol.find('./uint16').attrib['value']
                        print(' '*8+'PSM:', psm)
                    except AttributeError:
                        pass
                elif name == 'RFCOMM':
                    channel = protocol.find('./uint8').attrib['value']
                    print(' '*8+'channel:', channel)
                elif name in ('AVDTP', 'AVCTP'): # 音频分发、音频控制
                    # Stream End Point 
                    sep = protocol.find('./uint16').attrib['value']
                    print(' '*8+'SEP:', sep)
                else:
                    for elem in list(protocol)[1:]:
                        print(' '*8+ET.tostring(elem).decode().strip())
            except KeyError:
                print('(Unknown)')

    @classmethod
    def pp_browse_group_list(cls, attr:ET.Element):
        sequence = attr.find('./sequence')
        uuids = sequence.findall('./uuid')
        for uuid in uuids:
            uuid  = uuid.attrib['value']
            print('    uuid:', uuid, end=' ')
            if uuid == "0x1002":
                print('(PublicBrowseRoot)')
            else:
                print('(Unknown)')

    @classmethod
    def pp_bt_profile_descp_list(cls, attr:ET.Element):
        sequence = attr.find('./sequence')
        profiles = sequence.findall('./sequence')
        for profile in profiles:
            uuid = profile.find('./uuid').attrib['value']
            try:
                print('    uuid:', uuid, end=' ')
                if 'Profile' in service_cls_profile_ids[uuid]['Allowed Usage']:
                    print('('+service_cls_profile_ids[uuid]['Name']+')')
                    # print('         ', service_cls_profile_ids[uuid]['Specification'])
                else:
                    print('(Unknown)')
                value = profile.find('./uint16')
                print(' '*8+ET.tostring(value).decode().strip())
            except KeyError:
                print('(Unknown)')

    @classmethod
    def pp_lang_base_attr_id_list(cls, attr:ET.Element):
        for elem in list(attr):
            print(' '*4+ET.tostring(elem).decode().strip())

    @classmethod
    def pp_additional_protocol_descp_lists(cls, attr:ET.Element):
        sequences = attr.find('./sequence').findall('./sequence')
        for sequence in sequences:
            pseudo_attr = ET.Element('attribute')
            pseudo_attr.append(sequence)
            cls.pp_protocol_descp_list(pseudo_attr)


def test():
    sys.path.append('/mnt/hgfs/OneDrive/Projects/bluescan/src/')
    with open('./res/xml_records_sample.xml') as f:
        records_xml = f.read()
        SDPScanner.parse_sdptool_output(records_xml)


if __name__ == "__main__":
    test()

