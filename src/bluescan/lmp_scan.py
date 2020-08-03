#!/usr/bin/env python3

from pyclui import blue, green, blue, red, \
    DEBUG, INFO, WARNING, ERROR

from bthci import HCI

from . import BlueScanner
from .ll import ll_vers


lm_vers = {
    0:  'Bluetooth Core Specification 1.0b (Withdrawn)',
    1:  'Bluetooth Core Specification 1.1 (Withdrawn)',
    2:  'Bluetooth Core Specification 1.2 (Withdrawn)',
    3:  'Bluetooth Core Specification 2.0 + EDR (Withdrawn)',
    4:  'Bluetooth Core Specification 2.1 + EDR (Deprecated, to be withdrawn)',
    5:  'Bluetooth Core Specification 3.0 + HS (Deprecated, to be withdrawn)',
    6:  'Bluetooth Core Specification 4.0',
    7:  'Bluetooth Core Specification 4.1',
    8:  'Bluetooth Core Specification 4.2',
    9:  'Bluetooth Core Specification 5.0',
    10: 'Bluetooth Core Specification 5.1',
    11: 'Bluetooth Core Specification 5.2'
}


class LMPScanner(BlueScanner):
    def scan(self, remote_bd_addr:str):
        hci = HCI(self.iface)
        event_params = hci.create_connection({
            'BD_ADDR': remote_bd_addr,
            'Packet_Type': 0xcc18,
            'Page_Scan_Repetition_Mode': 0x02,
            'Reserved': 0x00,
            'Clock_Offset': 0x0000,
            'Allow_Role_Switch': 0x01
        })

        if event_params['Status'] != 0:
            print(ERROR, 'Failed to create ACL connection')
            sys.exit(1)

        event_params = hci.read_remote_version_information(cmd_params={
            'Connection_Handle': event_params['Connection_Handle']
        })

        if event_params['Status'] != 0:
            print(ERROR, 'Failed to read remote version')
            sys.exit(1)

        print(blue('Version'))
        print('    Version:')
        print(' '*8+lm_vers[event_params['Version']], '(LMP)')
        print(' '*8+ll_vers[event_params['Version']], '(LL)')
        print('    Manufacturer name:', event_params['Manufacturer_Name'])
        print('    Subversion:', event_params['Subversion'], '\n')

        event_params = hci.read_remote_supported_features({
            'Connection_Handle': event_params['Connection_Handle']
        })
        if event_params['Status'] != 0:
            print(ERROR, 'Failed to read remote supported features')
        else:
            print(blue('LMP features'))
            pp_lmp_features(event_params['LMP_Features'])
            print()

        if not True if (event_params['LMP_Features'][7] >> 7) & 0x01 else False:
            sys.exit(1)

        print(blue('Extended LMP features'))
        event_params = hci.read_remote_extended_features({
            'Connection_Handle': event_params['Connection_Handle'],
            'Page_Number': 0x00
        })
        if event_params['Status'] != 0:
            print(ERROR, 'Failed to read remote extented features')
        else:
            pp_ext_lmp_features(event_params['Extended_LMP_Features'], 0)
            for i in range(1, event_params['Maximum_Page_Number']+1):
                event_params = hci.read_remote_extended_features({
                    'Connection_Handle': event_params['Connection_Handle'],
                    'Page_Number': i})
                if event_params['Status'] != 0:
                    print(ERROR, 'Failed to read remote extented features, page', i)
                else:
                    pp_ext_lmp_features(event_params['Extended_LMP_Features'], i)


def pp_lmp_features(lmp_features:bytes):
    '''Parse and print LMP Features
    
    lmp_features -- 8 bytes
    '''
    for i in range(8):
        b  = lmp_features[i]
        if i == 0:
            print('    3 slot packets:', green('True') if b & 0x01 else red('False'))
            print('    5 slot packets:', green('True') if (b >> 1) & 0x01 else red('False'))
            print('    Encryption:', green('True') if (b >> 2) & 0x01 else red('False'))
            print('    Slot offset:', green('True') if (b >> 3) & 0x01 else red('False'))
            print('    Timing accuracy:', green('True') if (b >> 4) & 0x01 else red('False'))
            print('    Role switch:', green('True') if (b >> 5) & 0x01 else red('False'))
            print('    Hold mode:', green('True') if (b >> 6) & 0x01 else red('False'))
            print('    Sniff mode:', green('True') if (b >> 7) & 0x01 else red('False'))
        elif i == 1:
            print('    Previously used:', green('True') if b & 0x01 else red('False'))
            print('    Power control requests:', green('True') if (b >> 1) & 0x01 else red('False'))
            print('    Channel quality driven data rate (CQDDR):', green('True') if (b >> 2) & 0x01 else red('False'))
            print('    SCO link:', green('True') if (b >> 3) & 0x01 else red('False'))
            print('    HV2 packets:', green('True') if (b >> 4) & 0x01 else red('False'))
            print('    HV3 packets:', green('True') if (b >> 5) & 0x01 else red('False'))
            print('    μ-law log synchronous data:', green('True') if (b >> 6) & 0x01 else red('False'))
            print('    A-law log synchronous data:', green('True') if (b >> 7) & 0x01 else red('False'))
        elif i == 2:
            print('    CVSD synchronous data:', green('True') if b & 0x01 else red('False'))
            print('    Paging parameter negotiation:', green('True') if (b >> 1) & 0x01 else red('False'))
            print('    Power control:', green('True') if (b >> 2) & 0x01 else red('False'))
            print('    Transparent synchronous data:', green('True') if (b >> 3) & 0x01 else red('False'))
            print('    Flow control lag:', (b & 0x70) >> 4)
            print('    Broadcast Encryption:', green('True') if (b >> 7) & 0x01 else red('False'))
        elif i == 3:
            print('    Reserved for future use:', green('True') if b & 0x01 else red('False'))
            print('    Enhanced Data Rate ACL 2 Mb/s mode:', green('True') if (b >> 1) & 0x01 else red('False'))
            print('    Enhanced Data Rate ACL 2 Mb/s mode:', green('True') if (b >> 2) & 0x01 else red('False'))
            print('    Enhanced inquiry scan:', green('True') if (b >> 3) & 0x01 else red('False'))
            print('    Interlaced inquiry scan:', green('True') if (b >> 4) & 0x01 else red('False'))
            print('    Interlaced page scan:', green('True') if (b >> 5) & 0x01 else red('False'))
            print('    RSSI with inquiry results:', green('True') if (b >> 6) & 0x01 else red('False'))
            print('    Extended SCO link (EV3 packets):', green('True') if (b >> 7) & 0x01 else red('False'))
        elif i == 4:
            print('    EV4 packets:', green('True') if b & 0x01 else red('False'))
            print('    EV5 packets:', green('True') if (b >> 1) & 0x01 else red('False'))
            print('    Reserved for future use:', green('True') if (b >> 2) & 0x01 else red('False'))
            print('    AFH capable slave:', green('True') if (b >> 3) & 0x01 else red('False'))
            print('    AFH classification slave:', green('True') if (b >> 4) & 0x01 else red('False'))
            print('    BR/EDR Not Supported:', green('True') if (b >> 5) & 0x01 else red('False'))
            print('    LE Supported (Controller):', green('True') if (b >> 6) & 0x01 else red('False'))
            print('    3-slot Enhanced Data Rate ACL packets:', green('True') if (b >> 7) & 0x01 else red('False'))
        elif i == 5:
            print('    5-slot Enhanced Data Rate ACL packets:', green('True') if b & 0x01 else red('False'))
            print('    Sniff subrating:', green('True') if (b >> 1) & 0x01 else red('False'))
            print('    Pause encryption:', green('True') if (b >> 2) & 0x01 else red('False'))
            print('    AFH capable master:', green('True') if (b >> 3) & 0x01 else red('False'))
            print('    AFH classification master:', green('True') if (b >> 4) & 0x01 else red('False'))
            print('    Enhanced Data Rate eSCO 2 Mb/s mode:', green('True') if (b >> 5) & 0x01 else red('False'))
            print('    Enhanced Data Rate eSCO 3 Mb/s mode:', green('True') if (b >> 6) & 0x01 else red('False'))
            print('    3-slot Enhanced Data Rate eSCO packets:', green('True') if (b >> 7) & 0x01 else red('False'))
        elif i == 6:
            print('    Extended Inquiry Response:', green('True') if b & 0x01 else red('False'))
            print('    Simultaneous LE and BR/EDR to Same Device Capable (Controller):', green('True') if (b >> 1) & 0x01 else red('False'))
            print('    Reserved for future use:', green('True') if (b >> 2) & 0x01 else red('False'))
            print('    Secure Simple Pairing (Controller Support):', green('True') if (b >> 3) & 0x01 else red('False'))
            print('    Encapsulated PDU:', green('True') if (b >> 4) & 0x01 else red('False'))
            print('    Erroneous Data Reporting:', green('True') if (b >> 5) & 0x01 else red('False'))
            print('    Non-flushable Packet Boundary Flag:', green('True') if (b >> 6) & 0x01 else red('False'))
            print('    Reserved for future use:', green('True') if (b >> 7) & 0x01 else red('False'))
        elif i == 7:
            print('    HCI_Link_Supervision_Timeout_Changed event:', green('True') if b & 0x01 else red('False'))
            print('    Variable Inquiry TX Power Level:', green('True') if (b >> 1) & 0x01 else red('False'))
            print('    Enhanced Power Control:', green('True') if (b >> 2) & 0x01 else red('False'))
            print('    Reserved for future use:', green('True') if (b >> 3) & 0x01 else red('False'))
            print('    Reserved for future use:', green('True') if (b >> 4) & 0x01 else red('False'))
            print('    Reserved for future use:', green('True') if (b >> 5) & 0x01 else red('False'))
            print('    Reserved for future use:', green('True') if (b >> 6) & 0x01 else red('False'))
            print('    Extended features:', green('True') if (b >> 7) & 0x01 else red('False'))


def pp_ext_lmp_features(ext_lmp_features:bytes, page_num:int):
    '''Parse and print Extended LMP Features

    ext_lmp_features -- when page_num is 0, 8 bytes;
                        when page_num is 1, 1 bytes;
                        when page_num is 2, 2 bytes.
    '''
    if page_num == 0:
        print('Page 0')
        pp_lmp_features(ext_lmp_features)
    elif page_num == 1:
        b = ext_lmp_features[0]
        print('Page 1')
        print('    Secure Simple Pairing (Host Support):', green('True') if b & 0x01 else red('False'))
        print('    LE Supported (Host):', green('True') if (b >> 1) & 0x01 else red('False'))
        print('    Simultaneous LE and BR/EDR to Same Device Capable (Host):', green('True') if (b >> 2) & 0x01 else red('False'))
        print('    Secure Connections (Host Support):', green('True') if (b >> 3) & 0x01 else red('False'))
    elif page_num == 2:
        print('Page 2')
        for i in range(0, 2):
            b = ext_lmp_features[i]
            if i == 0:
                print('    Connectionless Slave Broadcast - Master Operation:', green('True') if b & 0x01 else red('False'))
                print('    Connectionless Slave Broadcast - Slave Operation:', green('True') if (b >> 1) & 0x01 else red('False'))
                print('    Synchronization Train:', green('True') if (b >> 2) & 0x01 else red('False'))
                print('    Synchronization Scan:', green('True') if (b >> 3) & 0x01 else red('False'))
                print('    HCI_Inquiry_Response_Notification event: ', green('True') if (b >> 4) & 0x01 else red('False'))
                print('    Generalized interlaced scan:', green('True') if (b >> 5) & 0x01 else red('False'))
                print('    Coarse Clock Adjustment:', green('True') if (b >> 6) & 0x01 else red('False'))
                print('    Reserved for future use:', green('True') if (b >> 7) & 0x01 else red('False'))
            elif i == 1:
                print('    Secure Connections (Controller Support):', green('True') if b & 0x01 else red('False'))
                print('    Ping:', green('True') if (b >> 1) & 0x01 else red('False'))
                print('    Slot Availability Mask:', green('True') if (b >> 2) & 0x01 else red('False'))
                print('    Train nudging:', green('True') if (b >> 3) & 0x01 else red('False'))
    else:
        print(WARNING, 'Unknown page number', page_num)
