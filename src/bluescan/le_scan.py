#!/usr/bin/env python3

from bluepy.btle import Scanner
from bluepy.btle import DefaultDelegate
from bluescan import BlueScanner
from termcolor import cprint

import re


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
    def scan(self, timeout=8, scan_type='active', sort='rssi'):
        '''        
        scan_type
            指定执行的 LE scan，是 active scan 还是 passive scan。
        '''
        scanner = Scanner(self.iface).withDelegate(LEDelegate())
        #print("[Debug] timeout =", timeout)

        # scan() 返回的 devs 是 dictionary view。
        if scan_type == 'active': # Active scan 会在 LL 发送 SCAN_REQ PDU
            print("[Warnning] Before doing active scan, make sure you spoof your BD_ADDR.")
            print("LE active scanning on hci%d...timeout %d sec\n" % (self.iface, timeout))
            devs = scanner.scan(timeout)
        elif scan_type == 'passive':
            print("LE passive scanning on hci%d...timeout %d sec\n" % (self.iface, timeout))
            devs = scanner.scan(timeout, passive=True)
        else:
            print("[Error] Unknown LE scan type.")
            return

        if sort == 'rssi':
            devs = list(devs) # 将 dictionary view 转换为 list
            devs.sort(key=lambda d:d.rssi)
        
        for dev in devs:
            print("BD_ADDR:    ", dev.addr)
            print("Addr type:  ", dev.addrType)
            if dev.connectable: 
                # link 层定义的 ADV_IND、ADV_DIRECT_IND 是可连接的
                # 可连接用高亮绿色前景显示，背景色不变
                print("\x1B[1;32m", end='') 
                
                # cprint() 中 on_color 即设置背景色。这个背景色被 termcolor 理解为
                # 涂荧光笔，highlight。而 "\x1B[1;31m]" 中的第一个 1 也表示 
                # highlight 不过此时的含义是把前景色的亮度调高
                #cprint("Connectable: " + str(dev.connectable), "green")
            else:
                # 不可连接用高亮红色前景显示，背景色不变
                print("\x1B[1;31m", end='')
                #cprint("Connectable: " + str(dev.connectable), "red")
            # 注意末尾需要恢复终端的默认值颜色
            print("Connectable:", dev.connectable, "\x1B[0m") 
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
                print("        " + desc + ' (' + '0x%02X' % adtype + '):', val)
            print("\n")


if __name__ == "__main__":
    pass
