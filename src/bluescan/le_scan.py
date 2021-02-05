#!/usr/bin/env python3

import re
import sys
import signal
import struct
import logging
import subprocess
from subprocess import STDOUT

from bluepy.btle import Scanner
from bluepy.btle import DefaultDelegate

from scapy.layers.bluetooth import HCI_Cmd_LE_Create_Connection
from scapy.layers.bluetooth import HCI_Cmd_LE_Read_Remote_Used_Features as HCI_Cmd_LE_Read_Remote_Features

from serial import Serial

from bthci import HCI, ERR_REMOTE_USER_TERMINATED_CONNECTION
import btsmp
from btsmp import *

from pyclui import Logger
from pyclui import blue, green, red

from . import service_cls_profile_ids
from . import gap_type_name_pairs, \
    COMPLETE_16_BIT_SERVICE_CLS_UUID_LIST, \
    COMPLETE_32_BIT_SERVICE_CLS_UUID_LIST, \
    COMPLETE_128_BIT_SERVICE_CLS_UUID_LIST, COMPLETE_LOCAL_NAME, \
    SHORTENED_LOCAL_NAME, TX_POWER_LEVEL, MANUFACTURER_SPECIFIC_DATA

from .serial_protocol import serial_reset
from .serial_protocol import SerialEventHandler

logger = Logger(__name__, logging.INFO)


microbit_infos = {}


# 这个字典暂时没用，以后可能用来判断收到的 advertising 类型
HCI_LE_ADVERTISING_REPORT_EVENT_EVENT_TYPE_DESCPS = {
    0x00: "Connectable undirected advertising (ADV_IND, 0x00)",
    0x01: "Connectable directed advertising (ADV_DIRECT_IND, 0x01)",
    0x02: "Scannable undirected advertising (ADV_SCAN_IND, 0x02)",
    0x03: "Non connectable undirected advertising (ADV_NONCONN_IND, 0x03)",
    0x04: "Scan Response (SCAN_RSP, 0x04)"
}


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


class LEScanner:
    """
    Provide three scanning functions:

    1. LE devices scanning
    2. LL features scanning
    3. Advertising physical channel PDU sniffing.
    """
    def __init__(self, hci='hci0', microbit_devpaths=None):
        """
        hci               - HCI device for scaning LE devices and LL features.
        microbit_devpaths - When sniffing advertising physical channel PDU, we 
                            need at least one micro:bit.
        """
        self.hci = hci
        self.devid = HCI.hcistr2devid(self.hci)
        self.microbit_devpaths = microbit_devpaths


    def scan_devs(self, timeout=8, scan_type='active', sort='rssi'):
        """LE devices scanning

        scan_type  - Indicate the type of LE scan：active, passive, adv or 
                     features.
        """
        if scan_type == 'adv':
            return

        scanner = Scanner(self.devid).withDelegate(LEDelegate())
        #print("[Debug] timeout =", timeout)

        # scan() 返回的 devs 是 dictionary view。
        if scan_type == 'active': # Active scan 会在 LL 发送 SCAN_REQ PDU
            logger.warning('Before doing an active scan, make sure you spoof your BD_ADDR.')
            logger.info('LE active scanning on %s with timeout %d sec\n' % \
                (blue('hci%d'%self.devid), timeout))
            devs = scanner.scan(timeout)
        elif scan_type == 'passive':
            logger.info('LE passive scanning on %s with timeout %d sec\n' % \
                (blue('hci%d'%self.devid), timeout))
            devs = scanner.scan(timeout, passive=True)
        else:
            logger.error('Unknown LE scan type')
            return

        if sort == 'rssi':
            devs = list(devs) # 将 dictionary view 转换为 list
            devs.sort(key=lambda d:d.rssi)
        
        for dev in devs:
            print('Addr:       ', blue(dev.addr.upper()))
            print('Addr type:  ', blue(dev.addrType))
            print('Connectable:', 
                green('True') if dev.connectable else red('False'))
            print("RSSI:        %d dB" % dev.rssi)
            print("General Access Profile:")
            for (adtype, desc, val) in dev.getScanData():
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
                print('\t'+desc+': ', end='')
                if adtype == COMPLETE_16_BIT_SERVICE_CLS_UUID_LIST:
                    print()
                    for uuid in val.split(','):
                        if len(uuid) == 36:
                            # 这里拿到的是完整的 128-bit uuid，但我们需要 16-bit uuid。
                            print('\t\t'+blue(uuid[4:8]))
                        else:
                            print('\t\t'+blue(uuid))
                    continue
                elif adtype == COMPLETE_32_BIT_SERVICE_CLS_UUID_LIST:
                    print()
                    for uuid in val.split(','): 
                        if len(uuid) == 36:
                            # 这里拿到的是完整的 128-bit uuid，但我们需要 32-bit uuid。
                            print('\t\t'+blue(uuid[0:8]))
                        else:
                            print('\t\t'+blue(uuid))
                    continue
                elif adtype == MANUFACTURER_SPECIFIC_DATA:
                    val = bytes.fromhex(val)
                    if len(val) > 2:
                        print()
                        print('\t\tCompany ID:', '0x%04x'%int.from_bytes(val[0:2], 'little', signed=False))
                        print('\t\tData:', val[2:])
                    else:
                        print(val)
                    continue
                print(val)
            print("\n")


    def scan_ll_feature(self, paddr, patype, timeout:int=10):
        """LL feature scanning

        paddr   - Peer addresss for scanning LL features.
        patype  - Peer address type, public or random.
        timeout - sec
        """
        hci = HCI(self.hci)
        logger.info('Scanning LE LL Features of %s, using %s\n'%(blue(paddr), blue(self.hci)))

        try:
            event_params = hci.le_create_connection(
                HCI_Cmd_LE_Create_Connection(paddr=bytes.fromhex(
                    paddr.replace(':', ''))[::-1], patype=patype), timeout)
            logger.debug(event_params)
        except RuntimeError as e:
            logger.error(e)
            return
        except TimeoutError as e:
            logger.info("Timeout")
            # logger.error("TimeoutError {}".format(e))
            return

        event_params = hci.le_read_remote_features(HCI_Cmd_LE_Read_Remote_Features(
            handle=event_params['Connection_Handle']))
        logger.debug(event_params)
        print(blue('LE LL Features:'))
        pp_le_features(event_params['LE_Features'])

        event_params = hci.disconnect({
            'Connection_Handle': event_params['Connection_Handle'],
            'Reason': ERR_REMOTE_USER_TERMINATED_CONNECTION})
        logger.debug(event_params)
        return


    def detect_pairing_feature(self, paddr, patype, timeout:int=10):
        """ """
        hci = HCI(self.hci)
        logger.info("Detecting SMP pairing feature of %s, using %s\n"%(blue(paddr), blue(self.hci)))

        pairing_req = SM_Hdr(sm_command=btsmp.CmdCode.PAIRING_REQUEST) / \
            SM_Pairing_Request(iocap="NoInputNoOutput", oob='Not Present', 
                authentication=(0b00 << AUTHREQ_RFU_POS) | (0 << CT2_POS) | \
                    (0 << KEYPRESS_POS) | (1 << SC_POS) | (0 << MITM_POS) | \
                    (BONDING << BONDING_FLAGS_POS), max_key_size=16,
                initiator_key_distribution=(0b0000 << INIT_RESP_KEY_DIST_RFU_POS) \
                    | (1 << LINKKEY_POS) | (1 << SIGNKEY_POS) | (1 << IDKEY_POS) \
                    | (1 << ENCKEY_POS),
                responder_key_distribution=(0b0000 << INIT_RESP_KEY_DIST_RFU_POS) \
                    | (1 << LINKKEY_POS) | (1 << SIGNKEY_POS) | (1 << IDKEY_POS) \
                    | (1 << ENCKEY_POS))

        event_params = None
        try:
            event_params = hci.le_create_connection(
                HCI_Cmd_LE_Create_Connection(paddr=bytes.fromhex(
                    paddr.replace(':', ''))[::-1], patype=patype), timeout)
            logger.debug(event_params)


            result = btsmp.send_pairing_request(event_params['Connection_Handle'], pairing_req, self.hci)
            logger.debug("detect_pairing_feature(), result: {}".format(result))

            rsp = btsmp.recv_pairing_response(timeout, self.hci)
            logger.debug("detect_pairing_feature(), rsp: {}".format(rsp))

            pp_smp_pkt(rsp)
        except RuntimeError as e:
            logger.error(e)
        except TimeoutError as e:
            output = subprocess.check_output(' '.join(['hciconfig', self.hci, 'reset']), 
                stderr=STDOUT, timeout=60, shell=True)
            event_params = None
            logger.info("Timeout")
            # logger.error("detect_pairing_feature(), TimeoutError {}".format(e))

        if event_params != None:
            hci.disconnect({
                'Connection_Handle': event_params['Connection_Handle'],
                'Reason': 0x1A
            })

        return


    def sniff_adv(self, channels=[37, 38, 39]):
        """Advertising physical channel PDU sniffing

        channel - The channel index(es) used when sniffing advertising 
                   physical channel PDU.

                   In addition to the primary advertising channel (37, 38, 
                   and 39), these PDUs may also appear in other channels. But 
                   at present we only focus on the primary advertising 
                   channel.
        """
        logger.debug("LEScanner.sniff_adv")

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
                logger.debug("LEScanner.scan, close()")
                serial_reset(dev)
                dev.close()


def pp_smp_pkt(pkt:bytes):
    logger.debug("pp_smp_pkt(), pkt: {}".format(pkt))
    code = pkt[0]

    if code == btsmp.CmdCode.PAIRING_RESPONSE:
        print(blue("Pairing Response"))
        iocap, oob, auth_req, max_enc_key_size, init_key_distr, rsp_key_distr = struct.unpack('BBBBBB', pkt[1:])
        print("    IO Capability: 0x%02x - %s" % (iocap, green(IOCapability[iocap].hname)))
        print("    OOB data flag: 0x%02x - %s" % (oob, OOBDataFlag[oob].hname))
        print("    AuthReq: 0x%02x" % auth_req)
        bonding_flag = (auth_req & BONDING_FLAGS_MSK) >> BONDING_FLAGS_POS
        mitm = (auth_req & MITM_MSK) >> MITM_POS
        sc = (auth_req & SC_MSK) >> SC_POS
        keypress = (auth_req & KEYPRESS_MSK) >> KEYPRESS_POS
        ct2 = (auth_req & CT2_MSK) >> CT2_POS
        rfu = (auth_req & AUTHREQ_RFU_MSK) >> AUTHREQ_RFU_POS
        print("        Bonding Flag:      0b{:02b} - {}".format(bonding_flag, BondingFlag[bonding_flag].hname))
        print("        MitM:              {}".format(green("True") if mitm else red("False")))
        print("        Secure Connection: {}".format(green("True") if sc else red("False")))
        print("        Keypress:          {}".format(green("True") if keypress else red("False")))
        print("        CT2:               {}".format(green("True") if ct2 else red("False")))
        print("        RFU:               0b{:02b}".format(rfu))
        print("    Maximum Encryption Key Size: %d" % max_enc_key_size)
        print("    Initiator Key Distribution: 0x%02x" % init_key_distr)
        enckey = (init_key_distr & ENCKEY_MSK) >> ENCKEY_POS
        idkey = (init_key_distr & IDKEY_MSK) >> IDKEY_POS
        signkey = (init_key_distr & SIGNKEY_MSK) >> SIGNKEY_POS
        linkkey = (init_key_distr & LINKKEY_MSK) >> LINKKEY_POS
        print("        EncKey:  {}".format(green("True") if enckey else red("False")))
        print("        IdKey:   {}".format(green("True") if idkey else red("False")))
        print("        SignKey: {}".format(green("True") if signkey else red("False")))
        print("        LinkKey: {}".format(green("True") if linkkey else red("False")))
        print("        RFU:     0b{:04b}".format((init_key_distr & INIT_RESP_KEY_DIST_RFU_MSK) >> INIT_RESP_KEY_DIST_RFU_POS))
        print("    Responder Key Distribution: 0x%02x" % rsp_key_distr)
        enckey = (rsp_key_distr & ENCKEY_MSK) >> ENCKEY_POS
        idkey = (rsp_key_distr & IDKEY_MSK) >> IDKEY_POS
        signkey = (rsp_key_distr & SIGNKEY_MSK) >> SIGNKEY_POS
        linkkey = (rsp_key_distr & LINKKEY_MSK) >> LINKKEY_POS
        print("        EncKey:  {}".format(green("True") if enckey else red("False")))
        print("        IdKey:   {}".format(green("True") if idkey else red("False")))
        print("        SignKey: {}".format(green("True") if signkey else red("False")))
        print("        LinkKey: {}".format(green("True") if linkkey else red("False")))
        print("        RFU:     0b{:04b}".format((rsp_key_distr & INIT_RESP_KEY_DIST_RFU_MSK) >> INIT_RESP_KEY_DIST_RFU_POS))
    elif code == btsmp.CmdCode.PAIRING_FAILED:
        reason = pkt[1]
        print(red("Pairing Failed"))
        print("    Reason: 0x%02x (%s)"%(reason, PairingFailedReason[reason].hname))
        print("            %s"%PairingFailedReason[reason].desc)
    else:
        logger.warning("unknown SMP packet: {}".format(pkt))


def pp_le_features(features:bytes):
    """
    features - LE LL features. The Bluetooth specification calls this FeatureSet.
    待处理 Valid from Controller to Controller, Masked to Peer, Host Controlled
    """
    for i in range(8):
        b  = features[i]
        if i == 0:
            print('    LE Encryption:', green('True') if b & 0x01 else red('False'))
            print('    Connection Parameters Request Procedure:', green('True') if (b >> 1) & 0x01 else red('False'))
            print('    Extended Reject Indication:', green('True') if (b >> 2) & 0x01 else red('False'))
            print('    Slave-initiated Features Exchange:', green('True') if (b >> 3) & 0x01 else red('False'))
            print('    LE Ping: ', green('True') if (b >> 4) & 0x01 else red('False'))
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
