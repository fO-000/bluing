#!/usr/bin/env python3

from bluescan import BlueScanner
from bluetooth import find_service

class SDPScanner(BlueScanner):
    def scan(self, addr):
        services = find_service(address=addr)
        for service in services:
            print('Name:', service['name'] )
            print('Protocol', service['protocol'])
            print('Port', service['port'])
            print('Service Class:', service['service-classes'])
            print('Profiles:', service['profiles'])
            print('Description:', service['description'])
            print('Provider:', service['provider'])
            print('Service-id', service['service-id'])
            print()
