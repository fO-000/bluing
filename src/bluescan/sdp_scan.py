#!/usr/bin/env python3

import re
import sys
import logging
import subprocess
from bluetooth import find_service
from xml.etree import ElementTree

from pyclui import Logger
from pyclui import green, blue, yellow, red
from halo import Halo

from . import BlueScanner
from .service_record import ServiceRecord


logger = Logger(__name__, logging.INFO)


class SDPScanner(BlueScanner):
    def scan(self, addr:str):
        spinner = Halo(text="Scanning", spinner={'interval': 200,
                                                 'frames': ['', '.', '.'*2, '.'*3]},
                       placement='right')
        spinner.start()
        # exitcode, output = subprocess.getstatusoutput('sdptool records --xml ' + addr)
        exitcode, output = subprocess.getstatusoutput('sdptool browse --xml ' + addr)
        if exitcode != 0:
            spinner.fail()
            sys.exit(exitcode)
        spinner.stop()
        
        # print('[DEBUG] output:', output)
        self.pp_sdptool_output(output)
        
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
    def pp_sdptool_output(cls, output:str):
        '''Split the string output by sdptool into individual servcie records 
        and processes them separately.'''
        # print(DEBUG, 'parse_sdptool_output')
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
