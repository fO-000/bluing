#!/usr/bin/env python

import re
import sys
import subprocess
from xml.etree import ElementTree

from xpycommon.log import Logger
from xpycommon.ui import blue
from halo import Halo

from .. import BlueScanner, LOG_LEVEL
from ..service_record import ServiceRecord


logger = Logger(__name__, LOG_LEVEL)


class SdpScanner(BlueScanner):
    def scan(self, addr:str):
        spinner = Halo(text="Scanning", placement='right')
        spinner.start()

        exitcode, output = subprocess.getstatusoutput('sdptool browse --xml ' + addr)
        if output == "Browsing {} ...".format(addr.upper()):
            exitcode, output = subprocess.getstatusoutput('sdptool records --xml ' + addr)
        else:
            lines = output.split('\n')
            lines = list(filter("Browsing {} ...".format(addr.upper()).__ne__, lines))
            lines = list(filter("Service Search failed: Invalid argument".__ne__, lines))
            
            output = '\n'.join(lines)
            
        if exitcode != 0:
            spinner.fail()
            sys.exit(exitcode)
            
        spinner.stop()
        
        logger.debug("output: {}".format(output))
        self.pp_sdptool_output(output)


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
        SdpScanner.parse_sdptool_output(records_xml)


if __name__ == '__main__':
    __test()
