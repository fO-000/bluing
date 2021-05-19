#!/usr/bin/env python3

import sys
import pickle
import io
import logging
import threading
import subprocess
from subprocess import STDOUT

import pkg_resources
from bluepy.btle import Peripheral # TODO: Get out of bluepy
from bluepy.btle import BTLEException, BTLEDisconnectError
from pyclui import green, blue, yellow, red, \
                   INFO_INDENT, ERROR_INDENT, WARNING_INDENT
from pyclui import Logger

import dbus
import dbus.service
import dbus.mainloop.glib
from dbus import SystemBus, ObjectPath

from btgatt import ServiceDef, CharacDef, CharacDescriptorDeclar, \
    declar_names, service_names, charac_names, descriptor_names, descriptor_permissions, \
    PRIMARY_SERVICE

from . import BlueScanner, ScanResult
from .le_scan import LeScanner, LE_DEVS_SCAN_RESULT_CACHE
from .common import BLUEZ_NAME, mainloop
from .agent import Agent
from .ui import INDENT

logger = Logger(__name__, logging.INFO)

IFACE_AGENT_MGR_1 = 'org.bluez.AgentManager1'

# char_uuid = pkg_resources.resource_string()
# service_uuid = pkg_resources.resource_string()

service_uuid_file = pkg_resources.resource_stream(__name__, "res/gatt-service-uuid.txt")
service_uuid_file = io.TextIOWrapper(service_uuid_file)

char_uuid_file = pkg_resources.resource_stream(__name__, 'res/gatt-characteristic-uuid.txt')
char_uuid_file = io.TextIOWrapper(char_uuid_file)

descriptor_uuid_file = pkg_resources.resource_stream(__name__, 'res/gatt-descriptor-uuid.txt')
descriptor_uuid_file = io.TextIOWrapper(descriptor_uuid_file)

services_spec = {}
characteristics_spec = {}
descriptors_spec = {}

BT_BASE_UUID = '00000000-0000-1000-8000-00805F9B34FB'
BT_BASE_UUID_SUFFIX = "-0000-1000-8000-00805F9B34FB"

for line in service_uuid_file:
    items = line.strip().split('\t')
    uuid = items.pop(2)
    services_spec[uuid] = {
        'Name': items[0],
        'Uniform Type Identifier': items[1],
        'Specification': items[2]
    }

for line in char_uuid_file:
    items = line.strip().split('\t')
    uuid = items.pop(2)
    characteristics_spec[uuid] = {
        'Name': items[0],
        'Uniform Type Identifier': items[1],
        'Specification': items[2]
    }

for line in descriptor_uuid_file:
    items = line.strip().split('\t')
    uuid = items.pop(2)
    descriptors_spec[uuid] = {
        'Name': items[0],
        'Uniform Type Identifier': items[1],
        'Specification': items[2]
    }
    
def full_uuid_str_to_16_int(uuid: str):
    """return 16-bit int or original uuid """
    if uuid.startswith("0000") and uuid.endswith(BT_BASE_UUID_SUFFIX):
        uuid = int(uuid.removeprefix('0000').removesuffix(BT_BASE_UUID_SUFFIX), base=16)
    return uuid


class BluescanAgent(Agent):
    def __init__(self, bus: SystemBus, idx: int, ioc: str = 'NoInputNoOutput') -> None:
        super().__init__(bus, idx)
        self.io_capability = ioc


def attr_permissions2str(permissions: dict):
    permi_str = ''
    
    read_flags = []
    write_flags = []
    
    if permissions is None:
        return red("Unknown")

    if permissions['read']['enable']:
        permi_str += 'Read'
        
        if permissions['read']['authen'] or permissions['read']['author'] or permissions['read']['higher']:
            permi_str += "("
        
            if permissions['read']['authen']:
                read_flags.append("authen")
        
            if permissions['read']['author']:
                read_flags.append("author")

            if permissions['read']['higher']:
                read_flags.append("higher")
            
            permi_str += ' '.join(read_flags)
            permi_str += ")"
        elif not (permissions['write']['enable'] or permissions['encrypt'] or permissions['higher']):
            return "Read Only, No Authentication, No Authorization"
        
        permi_str += ' '
        
    if permissions['write']['enable']:
        permi_str += 'Write'
        
        if permissions['write']['authen'] or permissions['write']['author'] or permissions['write']['higher']:
            permi_str += "("
        
            if permissions['write']['authen']:
                write_flags.append("authen")
        
            if permissions['write']['author']:
                write_flags.append("author")

            if permissions['write']['higher']:
                write_flags.append("higher")

            permi_str += ' '.join(write_flags)
            permi_str += ")"
        
        permi_str += ' '
    
    if permissions['encrypt']:
        permi_str += 'Encrypt'
        permi_str += ' '
    
    if permissions['higher']:
        permi_str += 'Higher layer profile or implementation specific'
        permi_str += ' '
        
    return permi_str


class GattScanResult(ScanResult):
    """A series of service definitions constitute the main part of this result."""
    def __init__(self, addr: str = None, addr_type: str = None):
        """
        addr      - Bluetooth address of the scanned device
        addr_type - public or random
        """
        super().__init__('GATT')

        self.addr = addr
        self.addr_type = addr_type
        self.service_defs = []

    def add_service_def(self, service_def: ServiceDef):
        self.service_defs.append(service_def)

    def print(self):
        if self.addr is None or self.addr_type is None:
            return

        print("Number of services: {}".format(len(self.service_defs)))
        print()
        print() # Two empty lines before Service Group
        
        # Prints each service group
        for service_def in self.service_defs:
            uuid = service_def.declar.value
            if type(uuid) is int:
                uuid = "0x{:04X}".format(uuid)

            try:
                service_name = green(service_names[service_def.declar.value])
            except KeyError:
                service_name = red("Unknown")

            print(blue("Service"), "(0x{:04X} - 0x{:04X}, {} characteristics)".format(
                service_def.start_handle, service_def.end_handle, len(service_def.charac_defs)))
            print(INDENT + "Handle: 0x{:04X}".format(service_def.start_handle))
            print(INDENT + "Type:  ", green("0x{:04X}".format(service_def.declar.type)), "("+green("{}".format(declar_names[service_def.declar.type]))+")")
            print(INDENT + "Value:  {} ({})".format(green(uuid), service_name))
            print(INDENT + "Permissions:", attr_permissions2str(service_def.declar.permissions))
            print() # An empty line before Characteristic Group
            
            # Prints each Gharacteristic group
            for charac_def in service_def.charac_defs:
                uuid = charac_def.declar.value['UUID']
                if type(uuid) is int:
                    uuid = "0x{:04X}".format(uuid)
                    
                value_declar_uuid = charac_def.value_declar.type
                if type(value_declar_uuid) is int:
                    value_declar_uuid = "0x{:04X}".format(value_declar_uuid)
                    
                if charac_def.declar.value['UUID'] != charac_def.value_declar.type:
                    logger.warning("charac_def.declar.value['UUID'] != charac_def.value_declar.type")
                    
                try:
                    charac_name = green(charac_names[charac_def.declar.value['UUID']])
                except KeyError:
                    charac_name = red("Unknown")

                try:
                    value_declar_name = charac_names[charac_def.value_declar.type]
                except KeyError:
                    value_declar_name = "Unknown"
                
                if charac_def.value_declar.value is None:
                    value_print = red('Unknown')
                else:
                    value_print = green(str(charac_def.value_declar.value))
                
                print(INDENT + yellow("Characteristic"), '({} descriptors)'.format(len(charac_def.descriptor_declars)))
                print(INDENT*2 + "Handle: 0x{:04X}".format(charac_def.declar.handle))
                print(INDENT*2 + "Type:   0x2803 (Characteristic)")
                print(INDENT*2 + "Value:")
                print(INDENT*3 + "Properties:", green(charac_def.declar.value['Properties']))
                print(INDENT*3 + "Handle:    ", green("0x{:04X}".format(charac_def.declar.value['Handle'])))
                print(INDENT*3 + "UUID:       {} ({})".format(green(uuid), charac_name))
                print(INDENT*2 + "Permissions:", attr_permissions2str(charac_def.declar.permissions))

                print(INDENT + yellow("Value"))
                print(INDENT*2 + "Handle: 0x{:04X}".format(charac_def.value_declar.handle))
                print(INDENT*2 + "Type:   {} ({})".format(value_declar_uuid, value_declar_name))
                print(INDENT*2 + "Value: ", value_print)
                print(INDENT*2 + "Permissions:", attr_permissions2str(charac_def.value_declar.permissions))
                
                # Prints each Characteristic Descriptor
                for descriptor_declar in charac_def.descriptor_declars:
                    uuid = descriptor_declar.type
                    if type(uuid) is int:
                        uuid = "0x{:04X}".format(uuid)
                        
                    try:
                        descriptor_name = green(descriptor_names[descriptor_declar.type])
                    except KeyError:
                        descriptor_name = red("Unknown")

                    if descriptor_declar.value is None:
                        value_print = red('Unknown')
                    else:
                        value_print = green(str(descriptor_declar.value))
                              
                    print(INDENT + yellow("Descriptor"))
                    print(INDENT*2 + "Handle:", green('0x{:04X}'.format(descriptor_declar.handle)))
                    print(INDENT*2 + "Type:   {} ({})".format(green(uuid), descriptor_name))
                    print(INDENT*2 + "Value: ", value_print)
                    print(INDENT*2 + "Permissions:", attr_permissions2str(descriptor_declar.permissions))
                    
                print() # An empty line before next Characteristic Group
            print() # An empty line before next Service Group
    
    def to_dict(self) -> dict:
        j = {
            "Addr": self.addr,
            "Addr_Type": self.addr_type,
            "services": []
        }
        for service_def in self.service_defs:
            j["services"].append(service_def.json())

    def to_json(self) -> str:
        self.to_dict()


class GattScanner(BlueScanner):
    """"""
    def __init__(self, iface: str = 'hci0', ioc: str = 'NoInputNoOutput'):
        super().__init__(iface=iface)
        self.result = GattScanResult()
        
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        sys_bus = SystemBus()
        
        self.agent_registered = False
        
        def register_agent_callback():
            logger.info('Agent object registered')
            print(INFO_INDENT, "IO capability: {}".format(self.bluescan_agent.io_capability), sep='')
            self.agent_registered = True
        def register_agent_error_callback(error):
            logger.error("Failed to register agent object")
            print(ERROR_INDENT, "{}".format(error), sep='')
            print(ERROR_INDENT, "IO capability: {}".format(self.bluescan_agent.io_capability), sep='')
            self.agent_registered = False
        self.bluescan_agent = BluescanAgent(sys_bus, 0, ioc)
        self.agent_mgr_1_iface = dbus.Interface(
            sys_bus.get_object(BLUEZ_NAME, '/org/bluez'), IFACE_AGENT_MGR_1)
        self.agent_mgr_1_iface.RegisterAgent(
            ObjectPath(self.bluescan_agent.path), 
            self.bluescan_agent.io_capability,
            reply_handler=register_agent_callback,
            error_handler=register_agent_error_callback)


    def scan(self, addr: str, addr_type: str, include_descriptor: bool) -> GattScanResult:
        """Performs a GATT scan and return result as GattScanResult.

        addr               - Remote BD_ADDR
        addr_type          - 'public' or 'random'
        include_descriptor - 对每个 characteristic 都获取 descriptor 会很耗时有些设
                             备会因此断开连接。于是这里提供了一个是否获取 descriptor 的选项
        """
        # TODO: Xbox Series X controller 扫描有问题。
        # ? BTLEException: Bluetooth command failed (code: 15, error: Encryption required before read/write)
        def run_mainloop():
            mainloop.run()
        mainloop_thread = threading.Thread(target=run_mainloop, args=[])
        mainloop_thread.start()
        
        try:
            self.result.addr = addr.upper()
            self.result.addr_type = addr_type
            
            if self.result.addr_type is None:
                self.result.addr_type = self.determine_addr_type()
            
            try:
                target = Peripheral(addr, iface=self.devid, addrType=self.result.addr_type)
            except BTLEDisconnectError as e:
                logger.error("BTLEDisconnectError")
                print(ERROR_INDENT, e, sep='')
                return self.result
            
            # 这里 bluepy 只会发送 ATT_READ_BY_GROUP_TYPE_REQ 获取 primary service。
            # TODO: Using ATT_READ_BY_GROUP_TYPE_REQ get secondary service
            services = target.getServices()
            
            for service in services:
                characteristics = []

                uuid = full_uuid_str_to_16_int(str(service.uuid).upper())
                
                service_def = ServiceDef(service.hndStart, service.hndEnd)
                service_def.set_declar(service_def.start_handle, PRIMARY_SERVICE, uuid)
                self.result.add_service_def(service_def)
                
                try:
                    characteristics = service.getCharacteristics()
                except BTLEException as e:
                    logger.warning("BTLEException")
                    print(WARNING_INDENT, e, sep='')
                    # continue                    

                for characteristic in characteristics:
                    descriptors = []

                    uuid = full_uuid_str_to_16_int(str(characteristic.uuid).upper())
                    value = None

                    try:
                        if characteristic.supportsRead():
                            value = characteristic.read()
                    except BTLEDisconnectError as e:
                        logger.warning("GattScanner.scan(), BTLEDisconnectError: {}".format(e))
                        print(WARNING_INDENT + "Read characteristic value {} failed".format(characteristic.uuid))
                        print(WARNING_INDENT + yellow("The Scan results may be incomplete."))
                        return self.result # TODO: 直接返回可能会浪费很多数据，打包这些数据再返回。
                    except BTLEException as e:
                        logger.warning("GattScanner.scan(), BTLEException: {}".format(e))
                        print(WARNING_INDENT + "Read characteristic value {} failed".format(characteristic.uuid))
                        
                    charac_declar_value = {
                        'Properties' : characteristic.propertiesToString(), # TODO: get properties binary data
                        'Handle'     : characteristic.getHandle(),
                        'UUID'       : uuid
                    }
                    charac_def = CharacDef()
                    charac_def.set_declar(characteristic.getHandle() - 1, charac_declar_value)
                    charac_def.set_value_declar(characteristic.getHandle(), uuid, value)
                    service_def.add_charac_def(charac_def)
                    
                    if include_descriptor:
                        descriptors = characteristic.getDescriptors()
                        logger.debug("GattScanner.scan(), got {} descriptors".format(len(descriptors)))

                    for descriptor in descriptors:
                        logger.debug("GattScanner.scan(), descriptor: {}".format(descriptor))
                        uuid = full_uuid_str_to_16_int(str(descriptor.uuid).upper())

                        try:
                            permissions = descriptor_permissions[uuid]
                        except KeyError:
                            permissions = None
                        
                        descriptor_declar = CharacDescriptorDeclar(descriptor.handle, uuid, None, permissions)
                        charac_def.add_descriptor_declar(descriptor_declar)
                        
                        try:
                            descriptor_declar.value = descriptor.read()
                        except BTLEException as e:
                            logger.warning("GattScanner.scan(), BTLEException: {}".format(e))
                            print(WARNING_INDENT + "Read descriptor {} failed".format(descriptor.uuid))
                        except BrokenPipeError as e:
                            logger.warning("GattScanner.scan(), BrokenPipeError: {}".format(e))
                            print(WARNING_INDENT + "Read descriptor {} failed".format(descriptor.uuid))

            # Set remote device untursted
            output = subprocess.check_output(' '.join(['bluetoothctl', 'untrust', 
                                                    addr]), 
                        stderr=STDOUT, timeout=60, shell=True)
            logger.info(output.decode())

            # output = subprocess.check_output(
            #     ' '.join(['sudo', 'systemctl', 'stop', 'bluetooth.service']), 
            #     stderr=STDOUT, timeout=60, shell=True)

            # output = subprocess.check_output(
            #     ' '.join(['sudo', 'rm', '-rf', '/var/lib/bluetooth/' + \
            #               self.hci_bdaddr + '/' + addr.upper()]), 
            #     stderr=STDOUT, timeout=60, shell=True)

            # output = subprocess.check_output(
            #     ' '.join(['sudo', 'systemctl', 'start', 'bluetooth.service']), 
            #     stderr=STDOUT, timeout=60, shell=True)
        except BTLEDisconnectError as e:
            logger.warning("GattScanner.scan(), BTLEDisconnectError: {}".format(e))
            print(WARNING_INDENT + yellow("The Scan results may be incomplete."))
        finally:
            if self.agent_registered:
                self.agent_mgr_1_iface.UnregisterAgent(
                    ObjectPath(self.bluescan_agent.path))
                logger.info('Unregistered Agent object')
                
                mainloop.quit()
        
        return self.result
    

    def determine_addr_type(self):
        """For user not provide the remote LE address type."""
        try:
            with open(LE_DEVS_SCAN_RESULT_CACHE, 'rb') as le_devs_scan_result_cache:
                le_devs_scan_result = pickle.load(le_devs_scan_result_cache)
                for dev_info in le_devs_scan_result.devices_info:
                    if self.result.addr == dev_info.addr:
                        logger.debug("determine_addr_type, {} {}".format(self.result.addr, dev_info.addr_type))
                        return dev_info.addr_type
        except FileNotFoundError as e:
            logger.debug("No {} found".format(LE_DEVS_SCAN_RESULT_CACHE))
                
        le_devs_scan_result = LeScanner(self.iface).scan_devs()
        for dev_info in le_devs_scan_result.devices_info:
            if self.result.addr == dev_info.addr:
                return dev_info.addr_type

        raise RuntimeError("Couldn't determine the LE address type. Please provide it explicitly.")


if __name__ == '__main__':
    result = GattScanner().scan('6F:45:66:76:41:12', 'random', True)
    result.print()
