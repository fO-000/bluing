#!/usr/bin/env python3

from . import ServiceRecord
from xml.etree import ElementTree

from pyclui import blue, green, yellow, red, \
    DEBUG, INFO, WARNING, ERROR


class HIDServiceRecord(ServiceRecord):
    '''Human Input Device Service Record.'''
    HID_DEVICE_RELEASE_NUMBER = 0x0200 # Deprecated
    HID_PARSER_VERSION        = 0x0201
    HID_DEVICE_SUBCLASS       = 0x0202
    HID_COUNTRY_CODE          = 0x0203
    HID_VIRTUAL_CABLE         = 0x0204
    HID_RECONNECT_INITIATE    = 0x0205
    HID_DESCRIPTOR_LIST       = 0x0206
    HID_LANGID_BASE_LIST      = 0x0207
    HID_SDP_DISABLE           = 0x0208 # Deprecated
    HID_BATTERY_POWER         = 0x0209
    HID_REMOTE_WAKE           = 0x020A
    HID_PROFILE_VERSION       = 0x020B
    HID_SUPERVISION_TIMEOUT   = 0x020C
    HID_NORMALLY_CONNECTABLE  = 0x020D
    HID_BOOT_DEVICE           = 0x020E
    HID_SSR_HOST_MAX_LATENCY  = 0x020F
    HID_SSR_HOST_MIN_TIMEOUT  = 0x0210
 
    service_clses = [
        {'UUID': 0x1124, 'name': 'HumanInterfaceDeviceService'}
    ]

    def __init__(self, record_xml:str):
        self.attrs = {
            self.HID_DEVICE_RELEASE_NUMBER: {
                'Name': 'HIDDeviceReleaseNumber (Deprecated)',
                'Parser': lambda val: print('\t0x%04X'%val)},
            self.HID_PARSER_VERSION: {
                # HIDP v1.1.1, 5.3.4.2 HIDParserVersion
                # 
                # Example
                #     <attribute id="0x0201">
                #         <uint16 value="0x0111" />
                #     </attribute>
                'Name': 'HIDParserVersion',
                'Parser': lambda val: print('\t0x%04x:'%val, 
                    green('USB HID specification ' + 'v' + \
                    ('%04x'%val)[:2].lstrip('0') + '.' + ('%04x.'%val)[2] + '.' + \
                    ('%04x.'%val)[3]))},

            self.HID_DEVICE_SUBCLASS: {
                # HIDP v1.1.1, 5.3.4.3 HIDDeviceSubclass
                #
                # Example
                #     <attribute id="0x0203">
                #         <uint8 value="0x00" />
                #     </attribute>
                'Name': 'HIDDeviceSubclass',
                'Parser': lambda val: print('\t0x%02X'%val)},
            self.HID_COUNTRY_CODE: {
                'Name': 'HIDCountryCode',
                'Parser': lambda val: print('\t0x%02X'%val)},
            self.HID_VIRTUAL_CABLE: {
                'Name': 'HIDVirtualCable',
                'Parser': lambda val: print(green('\tTrue') if val == 'true' \
                    else red('\tFalse'))},
            self.HID_RECONNECT_INITIATE:{
                'Name': 'HIDReconnectInitiate',
                'Parser': lambda val: print(green('\tTrue') if val == 'true' \
                    else red('\tFalse'))},
            self.HID_DESCRIPTOR_LIST:{
                'Name': 'HIDDescriptorList',
                'Parser': self.pp_hid_descriptor_list},
            self.HID_LANGID_BASE_LIST:{
                'Name': 'HIDLANGIDBaseList',
                'Parser': lambda val: print('\t', val)},
            self.HID_SDP_DISABLE:{
                'Name': 'HIDSDPDisable (Deprecated)',
                'Parser': lambda val: print(green('\tTrue') if val == 'true' \
                    else red('\tFalse'))},
            self.HID_BATTERY_POWER:{
                'Name': 'HIDBatteryPower',
                'Parser': lambda val: print(green('\tTrue') if val == 'true' \
                    else red('\tFalse'))},
            self.HID_REMOTE_WAKE:{
                'Name': 'HIDRemoteWake', 
                'Parser': lambda val: print(green('\tTrue') if val == 'true' \
                    else red('\tFalse'))},
            self.HID_PROFILE_VERSION:{
                'Name': 'HIDProfileVersion',
                'Parser': lambda val: print('\t0x%04X'%val)},
            self.HID_SUPERVISION_TIMEOUT:{
                'Name': 'HIDSupervisionTimeout',
                'Parser': lambda val: print('\t0x%04X'%val)},
            self.HID_NORMALLY_CONNECTABLE:{
                'Name': 'HIDNormallyConnectable',
                'Parser': lambda val: print(green('\tTrue') if val == 'true' \
                    else red('\tFalse'))},
            self.HID_BOOT_DEVICE: {
                'Name': 'HIDBootDevice',
                'Parser': lambda val: print(green('\tTrue') if val == 'true' \
                    else red('\tFalse'))},
            self.HID_SSR_HOST_MAX_LATENCY:{
                'Name': 'HIDSSRHostMaxLatency',
                'Parser': lambda val: print('\t0x%04X'%val)},
            self.HID_SSR_HOST_MIN_TIMEOUT:{
                'Name': 'HIDSSRHostMinTimeout',
                'Parser': lambda val: print('\t0x%04X'%val)
            },
            # HIDSSRHostMinTimeout 0x0211-0x03FF
            # Available for HID Language Strings 0x0400-0xFFFF
        }

        super().__init__(record_xml)


    def pp_hid_descriptor_list(self, val:ElementTree.Element):
        """
        val - data element sequence, include several HIDDescriptor
        """
        hid_descriptors =  val.findall('./sequence')
        for hid_descriptor in hid_descriptors:
            print("\tHIDDescriptor")
            cls_descpt_type = int(hid_descriptor.find('./uint8').attrib['value'], base=16)
            print("\t\tClassDescriptorType:", "Report" if cls_descpt_type == 0x22 else "Physical" if cls_descpt_type == 0x23 else "Reserved")
            encoding = hid_descriptor.find('./text').attrib['encoding']
            print("\t\tClassDescriptorData:", hid_descriptor.find('./text').attrib['value'], "(encoding " + encoding +")")
