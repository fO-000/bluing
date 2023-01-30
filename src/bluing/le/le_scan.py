#!/usr/bin/env python

import sys
import pickle

from bluepy.btle import Scanner
from bluepy.btle import DefaultDelegate
from halo import Halo
from serial import Serial

from xpycommon.bluetooth import IoCapabilities
from bthci import HCI, ControllerErrorCodes, HciRuntimeError, ADDR_TYPE_PUBLIC
from btsm import SecurityManager
from btsm.commands import OOBDataFlags, BondingFlags, AuthReq, KeyDist
from xpycommon.log import Logger
from xpycommon.ui import blue, green, red

from .. import ScanResult
from ..ui import INDENT
from ..common import bdaddr_to_company_name
from ..gap_data import SERVICE_DATA_128_BIT_UUID, SERVICE_DATA_16_BIT_UUID, SERVICE_DATA_32_BIT_UUID, gap_type_names, company_names, \
    COMPLETE_LIST_OF_16_BIT_SERVICE_CLASS_UUIDS, INCOMPLETE_LIST_OF_16_BIT_SERVICE_CLASS_UUIDS, \
    COMPLETE_LIST_OF_32_BIT_SERVICE_CLASS_UUIDS, INCOMPLETE_LIST_OF_32_BIT_SERVICE_CLASS_UUIDS,\
    COMPLETE_LIST_OF_128_BIT_SERVICE_CLASS_UUIDS, INCOMPLETE_LIST_OF_128_BIT_SERVICE_CLASS_UUIDS, \
    TX_POWER_LEVEL, MANUFACTURER_SPECIFIC_DATA, FLAGS

from . import LE_DEVS_SCAN_RESULT_CACHE, LOG_LEVEL
from .serial_protocol import serial_reset
from .serial_protocol import SerialEventHandler

logger = Logger(__name__, LOG_LEVEL)

microbit_infos = {}


# 这个字典暂时没用，以后可能用来判断收到的 advertising 类型
HCI_LE_ADVERTISING_REPORT_EVENT_EVENT_TYPE_DESCPS = {
    0x00: "Connectable undirected advertising (ADV_IND, 0x00)",
    0x01: "Connectable directed advertising (ADV_DIRECT_IND, 0x01)",
    0x02: "Scannable undirected advertising (ADV_SCAN_IND, 0x02)",
    0x03: "Non connectable undirected advertising (ADV_NONCONN_IND, 0x03)",
    0x04: "Scan Response (SCAN_RSP, 0x04)"
}

class AdStruct:
    def __init__(self, type: int, value: bytes) -> None:
        self.length = None
        self.type = type
        self.value = value


class LEDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
    
    def handleDiscovery(self, scanEntry, isNewDev, isNewData):
        # a callback function
        if isNewDev:
            #print("[LE scan] discovered new device")
            pass
        elif isNewData:
            #print("Received new data from " + scanEntry.addr)
            pass


class LeDeviceInfo:
    def __init__(self, addr: str, addr_type: str, connectable : bool, rssi : int) -> None:
        """
        addr - Upper case
        """
        self.addr = addr.upper()
        self.addr_type = addr_type
        self.connectable = connectable
        self.rssi = rssi
        self.ad_structs = []
        
    def add_ad_structs(self, ad: AdStruct):
        self.ad_structs.append(ad)


class LeDevicesScanResult(ScanResult):
    def __init__(self) -> None:
        super().__init__('LE Devices')
        self.devices_info = []
    
    def add_device_info(self, info: LeDeviceInfo):
        self.devices_info.append(info)
        
    def print(self):
        for dev_info in self.devices_info:
            print('Addr:       ', blue(dev_info.addr), 
                  "("+bdaddr_to_company_name(dev_info.addr)+")" if dev_info.addr_type == 'public' else "")
            print('Addr type:  ', blue(dev_info.addr_type))
            print('Connectable:', 
                green('True') if dev_info.connectable else red('False'))
            print("RSSI:        {} dBm".format(dev_info.rssi))
            print("General Access Profile:")
            
            # TODO: Unify the gap type name parsings of BR and LE
            for ad in dev_info.ad_structs:
                try:
                    type_names = gap_type_names[ad.type]
                except KeyError:
                    type_names = "0x{:02X} ".format(ad.type)+"("+ red("Unknown")+")"

                print(INDENT+"{}: ".format(type_names), end='')
                # print(INDENT+"0x{:02X} ({}): ".format(ad.type, type_names), end='')
                
                # Parses AD structure based on https://www.bluetooth.com/specifications/specs/
                # -> Core Specification Supplement
                if ad.type == COMPLETE_LIST_OF_16_BIT_SERVICE_CLASS_UUIDS or \
                    ad.type == INCOMPLETE_LIST_OF_16_BIT_SERVICE_CLASS_UUIDS:
                    print()
                    for uuid in ad.value.split(','):
                        if len(uuid) == 36:
                            # 这里拿到的是完整的 128-bit uuid，但我们需要 16-bit uuid。
                            print(INDENT*2 + blue("0x"+uuid[4:8].upper()))
                        else:
                            print(INDENT*2 + blue(uuid))
                elif ad.type == COMPLETE_LIST_OF_32_BIT_SERVICE_CLASS_UUIDS or \
                    ad.type == INCOMPLETE_LIST_OF_32_BIT_SERVICE_CLASS_UUIDS:
                    print()
                    for uuid in ad.value.split(','): 
                        if len(uuid) == 36:
                            # 这里拿到的是完整的 128-bit uuid，但我们需要 32-bit uuid。
                            print(INDENT*2 + blue("0x"+uuid[0:8].upper()))
                        else:
                            print(INDENT*2 + blue(uuid))
                elif ad.type == COMPLETE_LIST_OF_128_BIT_SERVICE_CLASS_UUIDS or \
                    ad.type == INCOMPLETE_LIST_OF_128_BIT_SERVICE_CLASS_UUIDS:
                        print()
                        for uuid in ad.value.split(','): 
                            print(INDENT*2 + blue(uuid).upper())
                elif ad.type == SERVICE_DATA_16_BIT_UUID:
                    print()
                    print(INDENT*2 + "UUID: 0x{}".format(ad.value[0:2*2].upper()))
                    print(INDENT*2 + "Data:", ad.value[2*2:])
                elif ad.type == SERVICE_DATA_32_BIT_UUID:
                    print()
                    print(INDENT*2 + "UUID: {}".format(ad.value[0:4*2].upper()))
                    print(INDENT*2 + "Data:", ad.value[4*2:])
                elif ad.type == SERVICE_DATA_128_BIT_UUID:
                    print()
                    print(INDENT*2 + "UUID: {}".format(ad.value[0:16*2].upper()))
                    print(INDENT*2 + "Data: ", ad.value[16*2:])
                elif ad.type == FLAGS:
                    print()
                    try:
                        value = bytes.fromhex(ad.value)
                        print(INDENT*2 + "LE Limited Discoverable Mode\n" if value[0] & 0x01 else "", end="")
                        print(INDENT*2 + "LE General Discoverable Mode\n" if value[0] & 0x02 else "", end="")
                        print(INDENT*2 + "BR/EDR Not Supported\n" if value[0] & 0x04 else "", end="") # Bit 37 of LMP Feature Mask Definitions (Page 0)
                        print(INDENT*2 + "Simultaneous LE + BR/EDR to Same Device Capable (Controller)\n" if value[0] & 0x08 else "", end="") # Bit 49 of LMP Feature Mask Definitions (Page 0)
                        print(INDENT*2 + "Simultaneous LE + BR/EDR to Same Device Capable (Host)\n" if value[0] & 0x10 else "", end="") # Bit 66 of LMP Feature Mask Definitions (Page 1)
                    except (ValueError, IndexError) as e:
                        logger.debug("LeDevicesScanResult.print(), parse ad.type == FLAGS")
                        print(ad.value, "("+red("Raw")+")")
                elif ad.type == MANUFACTURER_SPECIFIC_DATA:
                    value = bytes.fromhex(ad.value)
                    company_id = int.from_bytes(value[0:2], 'little', signed=False)
                    try:
                        company_name = blue(company_names[company_id])
                    except KeyError:
                        company_name = red("Unknown")
                    
                    if len(value) >= 2:
                        print()
                        print(INDENT*2+"Company ID:", '0x{:04X} ({})'.format(company_id,company_name))
                        try:
                            
                            print(INDENT*2+'Data:      ', ''.join(["{:02X}".format(b) for b in value[2:]]))
                        except IndexError:
                            print(INDENT*2+'Data:', None)
                    else:
                        print(value)
                elif ad.type == TX_POWER_LEVEL:
                    value = int.from_bytes(bytes.fromhex(ad.value), 'little', signed=True)
                    print(value, "dBm", "(pathloss {} dBm)".format(value - dev_info.rssi))
                else:
                    print(ad.value)

            print()  
            print() # Two empty lines before next LE device information

    def store(self):
        with open(LE_DEVS_SCAN_RESULT_CACHE, 'wb') as result_file:
            pickle.dump(self, result_file)


class LeScanner:
    """
    Provide three scanning functions:

    1. LE devices scanning
    2. LL features scanning
    3. Advertising physical channel PDU sniffing.
    """
    def __init__(self, iface: str ='hci0', microbit_devpaths=None):
        """
        hci               - HCI device for scaning LE devices and LL features.
        microbit_devpaths - When sniffing advertising physical channel PDU, we 
                            need at least one micro:bit.
        """
        self.devs_scan_result = LeDevicesScanResult()
        self.iface = iface
        self.devid = HCI.hcistr2devid(self.iface)
        self.microbit_devpaths = microbit_devpaths

    @staticmethod
    def determine_addr_type(iface: str, addr: str):
        """For user not provide the remote LE address type."""
        logger.debug("Entered determine_addr_type(cls, iface={}, addr={})".format(
            iface, addr))

        try:
            atype = LeScanner.cached_addr_to_atype(addr)
            if atype is not None:
                return atype
        except FileNotFoundError:
            logger.warning("No cached LE device information available")
        else:
            logger.info("The cached LE device information dose not match")
        
        logger.info("Start scanning nearby LE devices")
                
        le_devs_scan_result = LeScanner(iface).scan_devs(scan_type='passive')
        le_devs_scan_result.store()
        for dev_info in le_devs_scan_result.devices_info:
            if addr == dev_info.addr:
                return dev_info.addr_type

        raise RuntimeError("Failed to automatically determine the LE address type")
    
    @staticmethod
    def cached_addr_to_atype(addr: str) -> str | None:
        addr = addr.upper()

        with open(LE_DEVS_SCAN_RESULT_CACHE, 'rb') as le_devs_scan_result_cache:
            le_devs_scan_result = pickle.load(le_devs_scan_result_cache)
            for dev_info in le_devs_scan_result.devices_info:
                if addr == dev_info.addr:
                    return dev_info.addr_type

    def scan_devs(self, timeout=8, scan_type='active', sort='rssi') -> LeDevicesScanResult:
        """Perform LE Devices scanning and return scan reuslt as LeDevicesScanResult

        scan_type  - 'active' or 'passive'
        """
        if scan_type == 'active':
            logger.warning("You might want to spoof your LE address before doing "
                           "an active scan")

        scanner = Scanner(self.devid).withDelegate(LEDelegate())
        #print("[Debug] timeout =", timeout)
        
        spinner = Halo(text="Scanning", placement='right')

        # scan() 返回的 devs 是 dictionary view。
        logger.info('LE {} scanning on {} for {} sec'.format(
            blue(scan_type), blue(self.iface), blue("{}".format(timeout))))

        if scan_type == 'active': # Active scan 会在 LL 发送 SCAN_REQ PDU
            spinner.start()
            devs = scanner.scan(timeout)
            spinner.stop()
        elif scan_type == 'passive':
            spinner.start()
            devs = scanner.scan(timeout, passive=True)
            spinner.stop()
        else:
            logger.error('Unknown LE scan type')
            return

        if sort == 'rssi':
            devs = list(devs) # 将 dictionary view 转换为 list
            devs.sort(key=lambda d:d.rssi)
        
        for dev in devs:
            dev_info = LeDeviceInfo(dev.addr.upper(), dev.addrType.lower(), dev.connectable, dev.rssi)
            self.devs_scan_result.add_device_info(dev_info)
            
            # print('Addr:       ', blue(dev.addr.upper()))
            # print('Addr type:  ', blue(dev.addrType))
            # print('Connectable:', 
            #     green('True') if dev.connectable else red('False'))
            # print("RSSI:        %d dB" % dev.rssi)
            # print("General Access Profile:")
            for (adtype, desc, val) in dev.getScanData():
                ad_struct = AdStruct(adtype, val)
                dev_info.add_ad_structs(ad_struct)
                # 打印当前 remote LE dev 透露的所有 GAP 数据（AD structure）。
                # 
                # 如果 bluepy.scan() 执行的是 active scan，那么这些 GAP 数据
                # 可能同时包含 AdvData 与 ScanRspData。其中 AdvData 由 remote LE 
                # dev 主动返回，ScanRspData 由 remote BLE dev 响应 SCAN_REQ 返回。
                #
                # 虽然 LL 分开定义了 Advertising PDUs (ADV_IND, ADV_DIRECT_IND...)
                # 和 Scanning PDUs (SCAN_REQ, SCAN_RSP)。但它们分别包含的 AdvData 
                # 与 ScanRspData 到了 HCI 层都被放在了 HCI_LE_Advertising_Report 
                # event 中。HCI_LE_Advertising_Report 的 Event_Type 标识了这些数
                # 据具体来源于哪个 LL 层的 PDU。另外 ScanRspData 与 AdvData 的格式
                # 完全相同，都是 GAP 协议标准定义的 AD structure。
                #
                # 在 LL 定义的 Advertising PDUs 中 ADV_DIRECT_IND 一定不会包含 
                # AdvData。其余的 ADV_IND，ADV_NONCONN_IND 以及 ADV_SCAN_IND 都
                # 可能包含 AdvData。
                #
                # 另外 getScanData() 返回的 desc 还可以通过 ScanEntry.getDescription() 
                # 单独获取；val 还可以通过 ScanEntry.getValueText() 单独获取；
                # adtype 表示当前一条 GAP 数据（AD structure）的类型。
            
        return self.devs_scan_result


    def read_ll_feature_set(self, paddr: str, patype: int = ADDR_TYPE_PUBLIC, timeout: int = 10):
        """LL feature scanning

        paddr   - Peer addresss for scanning LL features.
        patype  - Peer address type, ADDR_TYPE_PUBLIC or ADDR_TYPE_RANDOM.
        timeout - sec
        """
        logger.info("Reading LL FeatureSet of {} on {}".format(blue(paddr), blue(self.iface)))
        
        spinner = Halo(text="Reading", placement='right')
        hci = HCI(self.iface)
        
        spinner.start()

        try:
            le_conn_complete = hci.le_create_connection(paddr, patype, timeout=timeout)
            if le_conn_complete.status != ControllerErrorCodes.SUCCESS:
                logger.error("Failed to connect {} {} LE address\n"
                             "    status: 0x{:02x} - {}".format(le_conn_complete.status, ControllerErrorCodes[le_conn_complete.status]))
        except Exception as e:
            spinner.fail()
            logger.error("{}: \"{}\"".format(e.__class__.__name__, e))
            sys.exit(1)

        le_read_remote_features_complete = hci.le_read_remote_features(le_conn_complete.conn_handle)
        if le_read_remote_features_complete.status != ControllerErrorCodes.SUCCESS:
            try:
                hci.disconnect(le_conn_complete.conn_handle)
            except HciRuntimeError as e:
                logger.warning("HciRuntimeError, {}".format(e))

            logger.error("Failed to le read remote features\n"
                         "    status: 0x{:02x} - {}".format(le_read_remote_features_complete.status, ControllerErrorCodes[le_read_remote_features_complete.status].name))
            sys.exit(1)
            
        spinner.stop()
        print(blue('LE LL Features:'))
        pp_le_feature_set(le_read_remote_features_complete.le_features)

        hci.disconnect(le_conn_complete.conn_handle)
        return


    def req_pairing_feature(self, paddr, patype: int = ADDR_TYPE_PUBLIC, timeout: int = 10):
        """
        """
        # TODO Mac OS 会弹窗，需要解决。
        logger.info("Requesting pairing feature of {} on {}".format(blue(paddr), 
                                                                    blue(self.iface)))
        self.sm = SecurityManager(self.iface)
        spinner = Halo(text="Requesting", placement='right')
        spinner.start()

        try:
            self.sm.connect(paddr, patype)
        except TimeoutError as e :
            spinner.fail()
            logger.error("{}: \"{}\"".format(e.__class__.__name__, e))
            sys.exit(1)
        
        auth_req = AuthReq(BondingFlags.NO_BONDING, False, True, False, False)
        initiator_key_dist = KeyDist(True, True, True, True)
        responder_key_dist = KeyDist(True, True, True, True)
        
        try:
            self.sm.pairing_request(IoCapabilities.NoInputNoOutput, OOBDataFlags.NOT_PRESENT, 
                                    int(auth_req), 16, initiator_key_dist, responder_key_dist)
            pairing_response = self.sm.wait_pairing_response(timeout)
            print('\r' + pairing_response.to_human_readable_str(title=blue("Pairing Response")))
        except Exception as e:
            spinner.fail()
            logger.error("{}: \"{}\"".format(e.__class__.__name__, e))

        spinner.stop()
        self.sm.disconnect()
        self.sm.close()


    def sniff_adv(self, channels={37, 38, 39}):
        """Advertising physical channel PDU sniffing

        channel - The channel index(es) used when sniffing advertising 
                   physical channel PDU.

                   In addition to the primary advertising channel (37, 38, 
                   and 39), these PDUs may also appear in other channels. But 
                   at present we only focus on the primary advertising 
                   channel.
        """
        logger.debug("LeScanner.sniff_adv")
        
        channels = list(channels)

        try:
            serial_devs = []
            idx = 0
            event_handlers = []

            dev_paths = self.microbit_devpaths

            if len(channels) > 3:
                raise RuntimeError("The number of channels ({}) > 3".format(len(channels)))
            elif len(dev_paths) > len(channels):
                logger.info("Detected {} micro:bits, but only enable {} of them".format(len(dev_paths), len(channels)))
                dev_paths = dev_paths[:len(channels)]
            elif len(dev_paths) < len(channels):
                channels = channels[:len(dev_paths)]

            for dev_path in dev_paths:
                logger.info("Using micro:bit {} on channel {}".format(dev_path, channels[idx]))
                
                dev = Serial(dev_path, 115200)
                dev.reset_input_buffer()
                dev.reset_output_buffer()
                serial_devs.append(dev)

                handler = SerialEventHandler(dev, channels[idx])
                handler.start()
                event_handlers.append(handler)
                idx += 1
                
            for handler in event_handlers:
                handler.join()
        finally:
            for dev in serial_devs:
                logger.debug("LeScanner.scan, close()")
                serial_reset(dev)
                dev.close()
       


def pp_le_feature_set(features: bytes):
    """
    待处理 Valid from Controller to Controller, Masked to Peer, Host Controlled
    """
    for i in range(8):
        b  = features[i]
        if i == 0:
            print('    LE Encryption:', green('True') if b & 0x01 else red('False'))
            print('    Connection Parameters Request Procedure:', green('True') if (b >> 1) & 0x01 else red('False'))
            print('    Extended Reject Indication:', green('True') if (b >> 2) & 0x01 else red('False'))
            print('    Slave-initiated Features Exchange:', green('True') if (b >> 3) & 0x01 else red('False'))
            print('    LE Ping:', green('True') if (b >> 4) & 0x01 else red('False'))
            print('    LE Data Packet Length Extension:', green('True') if (b >> 5) & 0x01 else red('False'))
            print('    LL Privacy:', green('True') if (b >> 6) & 0x01 else red('False'))
            print('    Extended Scanner Filter Policies:', green('True') if (b >> 7) & 0x01 else red('False'))
        elif i == 1:
            print('    LE 2M PHY:', green('True') if b & 0x01 else red('False'))
            print('    Stable Modulation Index - Transmitter:', green('True') if (b >> 1) & 0x01 else red('False'))
            print('    Stable Modulation Index - Receiver:', green('True') if (b >> 2) & 0x01 else red('False'))
            print('    LE Coded PHY:', green('True') if (b >> 3) & 0x01 else red('False'))
            print('    LE Extended Advertising:', green('True') if (b >> 4) & 0x01 else red('False'))
            print('    LE Periodic Advertising:', green('True') if (b >> 5) & 0x01 else red('False'))
            print('    Channel Selection Algorithm #2:', green('True') if (b >> 6) & 0x01 else red('False'))
            print('    LE Power Class 1:', green('True') if (b >> 7) & 0x01 else red('False'))
        elif i == 2:
            print('    Minimum Number of Used Channels Procedure:', green('True') if b & 0x01 else red('False'))
            print('    Connection CTE Request:', green('True') if (b >> 1) & 0x01 else red('False'))
            print('    Connection CTE Response:', green('True') if (b >> 2) & 0x01 else red('False'))
            print('    Connectionless CTE Transmitter:', green('True') if (b >> 3) & 0x01 else red('False'))
            print('    Connectionless CTE Receiver:', green('True') if (b >> 4) & 0x01 else red('False'))
            print('    Antenna Switching During CTE Transmission (AoD):', green('True') if (b >> 5) & 0x01 else red('False'))
            print('    Antenna Switching During CTE Reception (AoA):', green('True') if (b >> 6) & 0x01 else red('False'))
            print('    Receiving Constant Tone Extensions:', green('True') if (b >> 7) & 0x01 else red('False'))
        elif i == 3:
            print('    Periodic Advertising Sync Transfer - Sender:', green('True') if b & 0x01 else red('False'))
            print('    Periodic Advertising Sync Transfer - Recipient:', green('True') if (b >> 1) & 0x01 else red('False'))
            print('    Sleep Clock Accuracy Updates:', green('True') if (b >> 2) & 0x01 else red('False'))
            print('    Remote Public Key Validation:', green('True') if (b >> 3) & 0x01 else red('False'))
            print('    Connected Isochronous Stream - Master:', green('True') if (b >> 4) & 0x01 else red('False'))
            print('    Connected Isochronous Stream - Slave:', green('True') if (b >> 5) & 0x01 else red('False'))
            print('    Isochronous Broadcaster:', green('True') if (b >> 6) & 0x01 else red('False'))
            print('    Synchronized Receiver:', green('True') if (b >> 7) & 0x01 else red('False'))
        elif i == 4:
            print('    Isochronous Channels (Host Support):', green('True') if b & 0x01 else red('False'))
            print('    LE Power Control Request:', green('True') if (b >> 1) & 0x01 else red('False'))
            print('    LE Power Change Indication:', green('True') if (b >> 2) & 0x01 else red('False'))
            print('    LE Path Loss Monitoring:', green('True') if (b >> 3) & 0x01 else red('False'))


def __test():
    pass


if __name__ == "__main__":
    __test()
