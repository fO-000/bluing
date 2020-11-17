#!/usr/bin/env python3

import re
import logging

from bluepy.btle import Scanner
from bluepy.btle import DefaultDelegate
from pyclui import Logger
from pyclui import blue, green, yellow, red
from scapy.layers.bluetooth import HCI_Cmd_LE_Create_Connection
from scapy.layers.bluetooth import HCI_Cmd_LE_Read_Remote_Used_Features as HCI_Cmd_LE_Read_Remote_Features

from bthci import HCI, ERR_REMOTE_USER_TERMINATED_CONNECTION

from . import BlueScanner
from . import service_cls_profile_ids
from . import gap_type_name_pairs, \
    COMPLETE_16_BIT_SERVICE_CLS_UUID_LIST, \
    COMPLETE_32_BIT_SERVICE_CLS_UUID_LIST, \
    COMPLETE_128_BIT_SERVICE_CLS_UUID_LIST, COMPLETE_LOCAL_NAME, \
    SHORTENED_LOCAL_NAME, TX_POWER_LEVEL, MANUFACTURER_SPECIFIC_DATA


logger = Logger(__name__, logging.INFO)


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


class LEScanner(BlueScanner):
    def scan(self, timeout=8, scan_type='active', sort='rssi', paddr=None, patype='public'):
        '''
        scan_type - Indicate the type of LE scan：active, passive or features.
        paddr     - peer addresss, 配合 features 扫描类型使用。
        patype    - peer address type, public or random。
        '''
        if scan_type == 'features':
            hci = HCI(self.iface)
            logger.info('Scanning LE LL Features of %s, using %s\n'%(blue(paddr), blue(self.iface)))
            try:
                event_params = hci.le_create_connection(HCI_Cmd_LE_Create_Connection(
                    paddr=bytes.fromhex(paddr.replace(':', ''))[::-1], patype=patype))
                logger.debug(event_params)
            except RuntimeError as e:
                logger.error(e)
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
                    for uuid in val.split(','):
                        print()
                        if len(uuid) == 36:
                            # 这里拿到的是完整的 128-bit uuid，但我们需要 16-bit uuid。
                            print('\t\t'+blue(uuid[4:8]))
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


def pp_le_features(features:bytes):
    '''
    features - LE LL features. The Bluetooth specification calls this FeatureSet.
    待处理 Valid from Controller to Controller, Masked to Peer, Host Controlled
    '''
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
