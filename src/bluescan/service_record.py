import io
import pkg_resources
from xml.etree import ElementTree

from .ui import DEBUG, INFO, WARNING, ERROR
from .ui import blue, green, yellow, red

# https://www.bluetooth.com/specifications/assigned-numbers/service-discovery/
#     Table 2: Service Class Profile Identifiers
#
#     For historical reasons, some UUIDs in Table 2 are used to identify 
#     profiles in a BluetoothProfileDescriptorList universal attribute as well 
#     as service classes in a ServiceClassIDList universal attribute. However, 
#     for new profiles, Service Class UUIDs shall not be used in a 
#     BluetoothProfileDescriptorList universal attribute and Profile UUIDs 
#     shall not be used in a ServiceClassIDList universal attribute.
#
# Include both service class UUID (32-bit) and profile UUID (32-bit), and other
# information. 
service_cls_profile_ids_file = pkg_resources.resource_stream(__name__, 
    'res/service-class-profile-ids.txt')
service_cls_profile_ids_file = io.TextIOWrapper(
    service_cls_profile_ids_file)
service_cls_profile_ids = {}

# 需要手动编辑的 Service Class 如下：
#     IrMCSyncCommand
#     Headset – HS
# 同时注意去掉可能出现的 E2 80 8B
for line in service_cls_profile_ids_file:
    items = line.strip().split('\t')
    if items[0] == 'Service Class Name':
        continue
    # print(items)
    uuid = int(items.pop(1)[2:], base=16)
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

    # See https://www.bluetooth.com/specifications/assigned-numbers/service-discovery/
    # Table 5: Attribute Identifiers and BLUETOOTH CORE SPECIFICATION Version 
    # 5.2 | Vol 3, Part B page 1247
    SERVICE_NAME        = 0x0000
    SERVICE_DESCRIPTION = 0x0001
    PROVIDER_NAME       = 0x0002
    universal_attr_offsets = {
        SERVICE_NAME:        'ServiceName',
        SERVICE_DESCRIPTION: 'ServiceDescription',
        PROVIDER_NAME:       'ProviderName'
    }


    def __init__(self, record_xml:str):
        '''
        record_xml - A single service record XML.
        '''
        self.record_xml = record_xml
        self.service_clses = []
        self.attr_id_bases = []


    def pp(self):
        '''Parse and print the service record.

        xml -- XML for a single service record.
        '''
        attrs = ElementTree.fromstring(self.record_xml).findall('./attribute')
        for attr in attrs: # Parse service attributes one by one.
            try:
                self.pp_universal_attr(attr)
            except KeyError:
                self.pp_non_universal_attr(attr)


    def pp_universal_attr(self, attr:ElementTree.Element):
        '''The code for parsing a service attribute is divided into two parts.
        One of the part is parsing the universal attribute and the other part is 
        parsing the non universal attribute. This is the first part.
        '''
        attr_id = int(attr.attrib['id'][2:], base=16)

        # Parse three universal attribute ID offsets
        for base in self.attr_id_bases:
            if attr_id == base + self.SERVICE_NAME:
                name = attr.find('./text').attrib['value']
                print('0x%04x:'%attr_id, self.universal_attr_offsets[self.SERVICE_NAME])
                print('\t' + name)
                return
            elif attr_id == base + self.SERVICE_DESCRIPTION:
                description = attr.find('./text').attrib['value']
                print('0x%04x:'%attr_id, self.universal_attr_offsets[self.SERVICE_DESCRIPTION])
                print('\t' + description)
                return
            elif attr_id == base + self.PROVIDER_NAME:
                name = attr.find('./text').attrib['value']
                print('0x%04x:'%attr_id, self.universal_attr_offsets[self.PROVIDER_NAME])
                print('\t' + name)
                return
    
        print('0x%04X:'%attr_id, self.universal_attrs[attr_id]+' ', end='')
        if attr_id == self.SERVICE_RECORD_HANDLE:
            print('(uint32)')
            self.pp_service_record_hdl(attr)
        elif attr_id == self.SERVICE_CLASS_ID_LIST:
            print('(sequence)')
            self.pp_service_cls_list(attr)
        elif attr_id == self.SERVICE_RECORD_STATE:
            print('ServiceRecordState (to be parsed)')
        elif attr_id == self.SERVICE_ID:
            print('ServiceID (to be parsed)')
        elif attr_id == self.PROTOCOL_DESCRIPTOR_LIST:
            print('(sequence)')
            self.pp_protocol_descp_list(attr)
        elif attr_id == self.BROWSE_GROUP_LIST:
            print('(sequence)')
            self.pp_browse_group_list(attr)
        elif attr_id == self.LANGUAGE_BASE_ATTRIBUTE_ID_LIST:
            print('(sequence)')
            self.pp_lang_base_attr_id_list(attr)
        elif attr_id == self.SERVICE_INFO_TIME_TO_LIVE:
            print('ServiceInfoTimeToLive (to be parsed)')
        elif attr_id == self.SERVICE_AVAILABILITY:
            print('ServiceAvailability (to be parsed)')
        elif attr_id == self.BLUETOOTH_PROFILE_DESCRIPTOR_LIST:
            print('(sequence)')
            self.pp_bt_profile_descp_list(attr)
        elif attr_id == self.DOCUMENTATION_URL:
            print('DocumentationURL (to be parsed)')
        elif attr_id == self.CLIENT_EXECUTABLE_URL:
            print('ClientExecutableURL (to be parsed)')
        elif attr_id == self.ICON_URL:
            print('IconURL (to be parsed)')
        elif attr_id == self.ADDITIONAL_PROTOCOL_DESCRIPTOR_LISTS:
            print('(sequence)')
            self.pp_additional_protocol_descp_lists(attr)


    def pp_non_universal_attr(self, attr:ElementTree.Element):
        '''The code that parses a service attribute is divided into two parts.
        One of the part is parsing the universal attribute and the other part is 
        parsing the non universal attribute. This is the second part.
        '''
        attr_id = int(attr.attrib['id'][2:], base=16)

        if attr_id == 0x0100 + self.SERVICE_NAME:
            name = attr.find('./text').attrib['value']
            print('0x%04x: %s (guess)'%(attr_id, 
                self.universal_attr_offsets[self.SERVICE_NAME]))
            print('\t' + name)
        elif attr_id == 0x0100 + self.SERVICE_DESCRIPTION:
            description = attr.find('./text').attrib['value']
            print('0x%04x: %s (guess)'%(attr_id, 
                self.universal_attr_offsets[self.SERVICE_DESCRIPTION]))
            print('\t' + description)
        elif attr_id == 0x0100 + self.PROVIDER_NAME:
            print('0x%04x: %s (guess)'%(attr_id, 
                self.universal_attr_offsets[self.PROVIDER_NAME]))
        elif self.service_clses[0] == HFServiceRecord.service_classes[0]['UUID']:
            if attr_id == HFServiceRecord.SUPPORTED_FEATURES:
                val = int(attr.find('./uint16').attrib['value'][2:], base=16)
                HFServiceRecord.pp_supported_features(val)
        elif self.service_clses[0] == AGServiceRecord.service_classes[0]['UUID']:
            if attr_id == AGServiceRecord.NETWORK:
                val = int(attr.find('./uint8').attrib['value'][2:], base=16)
                AGServiceRecord.pp_network(val)
            if attr_id == AGServiceRecord.SUPPORTED_FEATURES:
                val = int(attr.find('./uint16').attrib['value'][2:], base=16)
                AGServiceRecord.pp_supported_features(val)
        elif self.service_clses[0] == MSEServiceRecord.service_classes[0]['UUID']:
            if attr_id == MSEServiceRecord.GOEP_L2CAP_PSM:
                print('0x%04x:'%attr_id, MSEServiceRecord.attrs[attr_id], '(uint16)')
                val = int(attr.find('./uint16').attrib['value'][2:], base=16)
                MSEServiceRecord.pp_goep_l2cap_psm(val)
            elif attr_id == MSEServiceRecord.MAS_INSTANCE_ID:
                print('0x%04x:'%attr_id, MSEServiceRecord.attrs[attr_id], '(uint8)')
                val = int(attr.find('./uint8').attrib['value'][2:], base=16)
                MSEServiceRecord.pp_mas_instance_id(val)
            elif attr_id == MSEServiceRecord.SUPPORTED_MESSAGE_TYPES:
                print('0x%04x:'%attr_id, MSEServiceRecord.attrs[attr_id], '(uint8)')
                val = int(attr.find('./uint8').attrib['value'][2:], base=16)
                MSEServiceRecord.pp_supported_msg_types(val)
            elif attr_id == MSEServiceRecord.MAP_SUPPORTED_FEATURES:
                print('0x%04x:'%attr_id, MSEServiceRecord.attrs[attr_id], '(uint32)')
                val = int(attr.find('./uint32').attrib['value'][2:], base=16)
                MSEServiceRecord.pp_map_supported_features(val)
        elif self.service_clses[0] == MCEServiceRecord.service_classes[0]['UUID']:
            print('Message Notification Server (to be parsed)')
            if attr_id == MCEServiceRecord.GOEP_L2CAP_PSM:
                print('0x%04x:'%attr_id, MCEServiceRecord.attrs[attr_id], '(uint16)')
                val = int(attr.find('./uint16').attrib['value'][2:], base=16)
                MSEServiceRecord.pp_goep_l2cap_psm(val)
            elif attr_id == MCEServiceRecord.MAP_SUPPORTED_FEATURES:
                print('0x%04x:'%attr_id, MCEServiceRecord.attrs[attr_id], '(uint32)')
                val = int(attr.find('./uint32').attrib['value'][2:], base=16)
                MCEServiceRecord.pp_map_supported_features(val)
        else:
            print('0x%04x: unknown'%attr_id)
            for elem in list(attr):
                s = [i.strip() for i in ElementTree.tostring(elem).decode().strip().replace('\t', '').split('\n')]
                # print('DEBUG', s)
                for i in s:
                    print('\t' + i)


    def pp_service_record_hdl(self, attr:ElementTree.Element):
        '''Parse and print ServiceRecordHandle (0x0000).
        
        XML example:
            <attribute id="0x0000">
                <uint32 value="0x00010001" />
            </attribute>
        '''
        handle = attr.find('./uint32')
        
        # Value is a attribute of the uint32 element  
        print('\t' + handle.attrib['value'])


    def pp_service_cls_list(self, attr:ElementTree.Element):
        '''Parse and print ServiceClassIDList (0x0001).
        
        XML example:
            <attribute id="0x0001">
                <sequence>
                    <uuid value="0x110e" />
                    <uuid value="0x110f" />
                </sequence>
            </attribute>
        '''
        sequence = attr.find('./sequence')
        uuids = sequence.findall('./uuid')
        for uuid in uuids:
            uuid = uuid.attrib['value']
            print('\t'+uuid+':', end=' ')
            try:
                uuid = int(uuid[2:], base=16)
            except ValueError:
                pass

            try:
                if 'Service Class' in service_cls_profile_ids[uuid]['Allowed Usage']:
                    self.service_clses.append(uuid)
                    name = service_cls_profile_ids[uuid]['Name']
                    print(green(name))
                else:
                    print(red('Unknown'))
            except KeyError:
                if uuid == 0x1800:
                    print(green('Generic Access'))
                elif uuid == 0x1801:
                    print(green('Generic Attribute'))
                else:
                    print(red('Unknown'))


    def pp_protocol_descp_list(self, attr:ElementTree.Element):
        '''Parse and print ProtocolDescriptorList (0x0004).
        
        XML example:
            <attribute id="0x0004">
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
            </attribute>
        '''
        sequence = attr.find('./sequence')
        protocols = sequence.findall('./sequence')
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


    def pp_browse_group_list(self, attr:ElementTree.Element):
        '''Parse and print BrowseGroupList (0x0005).

        XML example:
            <attribute id="0x0005">
                <sequence>
                    <uuid value="0x1002" />
                </sequence>
            </attribute>
        '''
        sequence = attr.find('./sequence')
        uuids = sequence.findall('./uuid')
        for uuid in uuids:
            uuid  = uuid.attrib['value']
            print('\t'+uuid+':', end=' ')
            
            if uuid == "0x1002":
                print('PublicBrowseRoot')
            else:
                print('Unknown')


    def pp_lang_base_attr_id_list(self, attr:ElementTree.Element):
        '''Parse and print LanguageBaseAttributeIDList (0x0006).

        XML example:
            <attribute id="0x0006">
                <sequence>
                    <uint16 value="0x656e" />
                    <uint16 value="0x006a" />
                    <uint16 value="0x0100" />
                </sequence>
            </attribute>
        '''
        values = attr.find('./sequence').findall('./uint16')
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


    def pp_bt_profile_descp_list(self, attr:ElementTree.Element):
        '''Parse and print BluetoothProfileDescriptorList (0x0009).
        
        XML example:
            <attribute id="0x0009">
                <sequence>
                    <sequence>
                        <uuid value="0x1108" />
                        <uint16 value="0x0102" />
                    </sequence>
                </sequence>
            </attribute>
        '''
        sequence = attr.find('./sequence')
        profiles = sequence.findall('./sequence')
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
                    print(red('Unknown'), end=' ')
                version = int(profile.find('./uint16').attrib['value'][2:], base=16)
                print(green('v%d.%d'%(version>>8, version&0xFF)))
            except KeyError:
                print(red('Unknown'))


    def pp_additional_protocol_descp_lists(self, attr:ElementTree.Element):
        '''Parse and print AdditionalProtocolDescriptorLists (0x000D).
        
        XML example:
    	    <attribute id="0x000d">
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
            </attribute>
        '''
        sequences = attr.find('./sequence').findall('./sequence')
        for sequence in sequences:
            pseudo_attr = ElementTree.Element('attribute')
            pseudo_attr.append(sequence)
            self.pp_protocol_descp_list(pseudo_attr)


class HFServiceRecord(ServiceRecord):
    '''Hands-Free unit Service Record
    
    HFP Specification v1.8, Table 5.1: Service Record for the HF
    '''
    service_classes = [
        {'UUID': 0x111E, 'name': 'Handsfree'},
        {'UUID': 0x1203, 'name': 'GenericAudio'}
    ]
    
    SUPPORTED_FEATURES = 0x0311
    attrs = {
        SUPPORTED_FEATURES: 'SupportedFeatures'
    }

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

    @classmethod
    def pp_supported_features(cls, val:int):
        '''Parse and print SupportedFeatures service attribute.
    
        val - Value of SupportedFeatures, Uint16
        '''
        print('0x%04x:'%cls.SUPPORTED_FEATURES, cls.attrs[cls.SUPPORTED_FEATURES], '(uint16)')
        print('\t0x%04X'%val)
        for i in range(len(cls.supported_features_bitmap)):
            feature_name = cls.supported_features_bitmap[i]
            print('\t\t'+(green(feature_name) if val >> i & 0x0001 else red(feature_name)))


class AGServiceRecord(ServiceRecord):
    '''Autio Gateway Service Record
    
    See HFP Specification v1.8, Table 5.3: Service Record for the AG
    '''
    service_classes = [
        {'UUID': 0x111F, 'name': 'HandsfreeAudioGateway'},
        {'UUID': 0x1203, 'name': 'GenericAudio'}
    ]

    NETWORK            = 0x0301
    SUPPORTED_FEATURES = 0x0311
    attrs = {
        NETWORK: 'Network',
        SUPPORTED_FEATURES: 'SupportedFeatures'
    }

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


    @classmethod
    def pp_network(cls, val:int):
        '''Parse and print Network service attribute.

        val - Value of Network, Uint8
        '''
        print('0x%04x:'%cls.NETWORK, cls.attrs[cls.NETWORK], '(uint8)')
        print('\t0x%02X'%val)
        print('\t\t'+cls.network[val])


    @classmethod
    def pp_supported_features(cls, val:int):
        '''Parse and print SupportedFeatures service attribute.

        val  - Value of SupportedFeatures, Uint16
        '''
        print('0x%04x:'%cls.SUPPORTED_FEATURES, cls.attrs[cls.SUPPORTED_FEATURES], '(uint16)')
        print('\t0x%04X'%val)
        for i in range(len(cls.supported_features_bitmap)):
            feature_name = cls.supported_features_bitmap[i]
            print('\t\t'+(green(feature_name) if val >> i & 0x0001 else red(feature_name)))


class MSEServiceRecord(ServiceRecord):
    '''Message Server Equipment Service Record

    See MAP Specification v1.4.2, Table 7.1: SDP Record for the Message Access 
    Service on the MSE Device
    '''
    service_classes = [
        {'UUID': 0x1132, 'name': 'Message Access Server'}
    ]

    GOEP_L2CAP_PSM          = 0x0200
    MAS_INSTANCE_ID         = 0x0315
    SUPPORTED_MESSAGE_TYPES = 0x0316
    MAP_SUPPORTED_FEATURES  = 0x0317
    attrs = {
        GOEP_L2CAP_PSM:          '​GoepL2capPsm', # MAP v1.2 and later
        MAS_INSTANCE_ID:         'MASInstanceID',
        SUPPORTED_MESSAGE_TYPES: 'SupportedMessageTypes',
        MAP_SUPPORTED_FEATURES:  'MapSupportedFeatures' # MAP v1.2 and later
    }

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

    @classmethod
    def pp_goep_l2cap_psm(cls, val:int):
        '''Parser and print GoepL2capPsm (MAP v1.2 and later)
        
        val - Value of GoepL2capPsm, uint16
        '''
        print('\t0x%04X'%val)

    @classmethod
    def pp_mas_instance_id(cls, val:int):
        '''Parse and print MASInstanceID service attribute

        val - Value of MASInstanceID, uint8
        '''
        print('\t0x%02X'%val)


    @classmethod
    def pp_supported_msg_types(cls, val:int):
        '''Parse and print SupportedMessageTypes service attribute.
        
        val - Value of SupportedMessageTypes, uint8
        '''
        print('\t0x%02X'%val)
        for i in range(len(cls.supported_msg_types_bitmap)):
            type_name = cls.supported_msg_types_bitmap[i]
            print('\t\t', end=' ')
            if i < 5:
                print(green(type_name) if val >> i & 0x01 else red(type_name))
            else:
                print(val >> i & 0x01, 'RFU')


    @classmethod
    def pp_map_supported_features(cls, val: int):
        '''Parse and print MapSupportedFeatures (MAP v1.2 and later) service 
        attribute.
        
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


class MCEServiceRecord(ServiceRecord):
    '''Message Client Equipment Service Record
    
    See MAP Specification v1.4.2, Table 7.2: SDP Record for the Message 
    Notification Service on the MCE Device
    '''
    service_classes = [
        {'UUID': 0x1133, 'name': 'Message Notification Server'}
    ]
    
    GOEP_L2CAP_PSM         = 0x0200
    MAP_SUPPORTED_FEATURES = 0x0317
    attrs = {
        GOEP_L2CAP_PSM:         '​GoepL2capPsm', # MAP v1.2 and later
        MAP_SUPPORTED_FEATURES: 'MapSupportedFeatures' # MAP v1.2 and later
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


    @classmethod
    def pp_goep_l2cap_psm(cls, val:int):
        '''Parser and print GoepL2capPsm (MAP v1.2 and later)
        
        val - Value of GoepL2capPsm, uint16
        '''
        print('\t0x%04X'%val)


    @classmethod
    def pp_map_supported_features(cls, val: int):
        '''Parse and print MapSupportedFeatures (MAP v1.2 and later).
        
        val - Value of MapSupportedFeatures, uint32
        '''
        print('\t0x%08X'%val)
        for i in range(len(cls.map_supported_features_bitmap)):
            feature_name = cls.map_supported_features_bitmap
            print('\t\t', end=' ')
            if i < 23:
                print(green(feature_name) if val >> i & 0x01 else red(feature_name))
            else:
                print(val >> i & 0x01, 'RFU')


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
