#!/usr/bin/env python3


import re
import sys
import subprocess
from bluetooth import find_service
from xml.etree import ElementTree



# 仅供测试使用
#sys.path.append('/mnt/hgfs/OneDrive/Projects/bluescan/src/')

from bluescan import BlueScanner
from .service_record import ServiceRecord
from .ui import blue
from .ui import green
from .ui import yellow
from .ui import red
from .ui import DEBUG
from .ui import INFO
from .ui import WARNING
from .ui import ERROR


class SDPScanner(BlueScanner):
    def scan(self, addr:str):
        print(INFO, 'Scanning...')
        exitcode, output = subprocess.getstatusoutput('sdptool records --xml ' + addr)
        if exitcode != 0:
            sys.exit(exitcode)

        # print('[DEBUG] output:', output)
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
        '''Split the string output by sdptool into individual servcie records 
        and processes them separately.'''
        pattern = r'Failed to connect to SDP server on[\da-zA-Z :]*'
        pattern = re.compile(pattern)
        result = pattern.findall(output)
        for i in result:
            output = output.replace(i, '')

        record_xmls = output.split('<?xml version="1.0" encoding="UTF-8" ?>\n\n')[1:]
        print('Number of service records:', len(record_xmls), '\n\n')
        for record_xml in record_xmls:
            print(blue('Service Record'))
            try:
                sr = ServiceRecord(record_xml)
                sr.pp()
            except ElementTree.ParseError as e:
                print(record_xml)
            print('\n')


def __test():
    with open('../res/sdp_record_xml_sample/2.xml') as f:
        records_xml = f.read()
        SDPScanner.parse_sdptool_output(records_xml)


if __name__ == "__main__":
    __test()
