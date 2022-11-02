#!/usr/bin/env python

import sys
import os
import subprocess
from traceback import format_exception
from subprocess import STDOUT, CalledProcessError
from pathlib import PosixPath

from xpycommon.log import Logger
from xpycommon.ui import blue
from bthci import HCI, ControllerErrorCodes, HciError
from bluepy.btle import BTLEException
from xpycommon.bluetooth import restart_bluetooth_service, find_rfkill_devid

from . import BlueScanner, LOG_LEVEL
from .ui import parse_cmdline
from .helper import get_microbit_devpaths
from .plugin import BluescanPluginManager, BluescanPluginError
from .br_scan import BRScanner
from .le_scan import LeScanner
from .gatt_scan import GattScanner
from .sdp_scan import SDPScanner


PLUGIN_PATH = '/root/.bluescan/plugins'
logger = Logger(__name__, LOG_LEVEL)


def prepare_hci(iface: str = 'hci0'):
    """
    Exceptions
        RuntimeError
            当读取 HCI device 的 BD_ADDR 失败时，将抛出该异常。
    """
    # hciconfig <hci> up 的前提是 rfkill 先 unblock
    subprocess.check_output('rfkill unblock %d' % find_rfkill_devid(iface), 
                            stderr=STDOUT, timeout=5, shell=True)
    try:
        restart_bluetooth_service()
    except CalledProcessError as e:
        logger.warning("Failed to restart bluetooth service")

    try:
        subprocess.check_output('hciconfig {} up'.format(iface),
                            stderr=STDOUT, timeout=5, shell=True)
    except CalledProcessError as e:
        raise RuntimeError('hciconfig {} up failed. Consider replugging the Bluetooth adapter.'.format(iface))

    hci = HCI(iface)

    # 下面在发送各种 HCI command 时，如果出现如下异常：
    #     BlockingIOError: [Errno 11] Resource temporarily unavailable
    # 那么可能是 hci socket 被设为了 non-blocking mode。
    logger.debug("Sending hci.inquiry_cancel()")
    cmd_complete = hci.inquiry_cancel()
    if cmd_complete.status not in (ControllerErrorCodes.SUCCESS, ControllerErrorCodes.COMMAND_DISALLOWED):
        logger.warning("Failed to inquiry cancel\n"
                       "    command complete status: 0x{:02x} - {}".format(
                           cmd_complete.status, cmd_complete.status.name))
        
    logger.debug("Sending hci.exit_periodic_inquiry_mode()")
    cmd_complete = hci.exit_periodic_inquiry_mode()
    if cmd_complete.status not in (ControllerErrorCodes.SUCCESS, ControllerErrorCodes.COMMAND_DISALLOWED):
        logger.warning("Failed to exit periodic inquiry mode\n"
                       "    command complete status: 0x{:02x} - {}".format(
                           cmd_complete.status, cmd_complete.status.name))
    
    hci.write_scan_enable() # No scan enabled
    if cmd_complete.status not in (ControllerErrorCodes.SUCCESS, ControllerErrorCodes.COMMAND_DISALLOWED):
        logger.warning("Failed to write scan enable\n"
                       "    command complete status: 0x{:02x} - {}".format(
                           cmd_complete.status, cmd_complete.status.name))
    
    cmd_complete = hci.le_set_advertising_enable() # Advertising is disabled
    if cmd_complete.status not in (ControllerErrorCodes.SUCCESS, ControllerErrorCodes.COMMAND_DISALLOWED):
        logger.warning("Failed to le set advertising enable\n"
                       "    command complete status: 0x{:02x} - {}".format(
                           cmd_complete.status, cmd_complete.status.name))
    
    cmd_complete = hci.le_set_scan_enable(False, True)
    if cmd_complete.status not in (ControllerErrorCodes.SUCCESS, ControllerErrorCodes.COMMAND_DISALLOWED):
        logger.warning("Failed to le set scan enable\n"
                       "    command complete status: 0x{:02x} - {}".format(
                           cmd_complete.status, cmd_complete.status.name))

    cmd_complete = hci.set_event_filter(0x00) # Clear All Filters
    if cmd_complete.status != ControllerErrorCodes.SUCCESS:
        logger.warning("Failed to set event filter\n"
                       "    command complete status: 0x{:02x} - {}".format(
                           cmd_complete.status, cmd_complete.status.name))

    cmd_complete = hci.read_bd_addr()
    if cmd_complete.status != ControllerErrorCodes.SUCCESS:
        raise RuntimeError("Failed to read BD_ADDR\n"
                           "    command complete status: 0x{:02x} - {}".format(
                               cmd_complete.status, cmd_complete.status.name))
    else:
        local_bd_addr = cmd_complete.bd_addr

    # Clear bluetoothd cache
    cache_path = PosixPath('/var/lib/bluetooth/')/local_bd_addr.upper()/'cache'
    if cache_path.exists():
        for file in cache_path.iterdir():
            os.remove(file)

    hci.close()


def clean(laddr: str, raddr: str):
    output = subprocess.check_output(
        ' '.join(['sudo', 'systemctl', 'stop', 'bluetooth.service']), 
        stderr=STDOUT, timeout=60, shell=True)

    output = subprocess.check_output(
        ' '.join(['sudo', 'rm', '-rf', '/var/lib/bluetooth/' + \
                  laddr + '/' + raddr.upper()]), 
        stderr=STDOUT, timeout=60, shell=True)
    if output != b'':
        logger.info(output.decode())

    output = subprocess.check_output(
        ' '.join(['sudo', 'rm', '-rf', '/var/lib/bluetooth/' + \
                  laddr + '/' + 'cache' + '/' + raddr.upper()]), 
        stderr=STDOUT, timeout=60, shell=True)
    if output != b'':
        logger.info(output.decode())

    output = subprocess.check_output(
        ' '.join(['sudo', 'systemctl', 'start', 'bluetooth.service']), 
        stderr=STDOUT, timeout=60, shell=True)


def main():
    try:
        args = parse_cmdline()
        logger.debug("parse_cmdline() returned\n"
                     "    args: {}".format(args))

        if args['--list-installed-plugins']:
            BluescanPluginManager.list()
            return
        
        if args['--install-plugin']:
            plugin_wheel_path = args['--install-plugin']
            BluescanPluginManager.install(plugin_wheel_path)
            return
        
        if args['--uninstall-plugin']:
            plugin_name = args['--uninstall-plugin']
            BluescanPluginManager.uninstall(plugin_name)
            return

        if args['--plugin']:
            plugin_name = args['--plugin']
            BluescanPluginManager.run(plugin_name)
            return

        if not args['--adv']:
            # 在不使用 microbit 的情况下，我们需要将选中的 hci 设备配置到一个干净的状态。
            
            if args['-i'] == 'The default HCI device':
                # 当 user 没有显示指明 hci 设备情况下，我们需要自动获取一个可用的 hci 
                # 设备。注意这个设备不一定是 hci0。因为系统中可能只有 hci1，而没有 hci0。
                try:
                    args['-i'] = HCI.get_default_iface()
                except HciError:
                    logger.error('No available HCI device')
                    sys.exit(-1)

            prepare_hci(args['-i'])
            
        scan_result = None
        if args['-m'] == 'br':
            br_scanner = BRScanner(args['-i'])
            if args['--lmp-feature']:
                br_scanner.scan_lmp_feature(args['BD_ADDR'])
            else:
                br_scanner = BRScanner(args['-i'])
                br_scanner.inquiry(inquiry_len=args['--inquiry-len'])
        elif args['-m'] == 'le':
            if args['--adv']:
                dev_paths = get_microbit_devpaths()
                LeScanner(microbit_devpaths=dev_paths).sniff_adv(args['--channel'])
            elif args['--ll-feature']:
                LeScanner(args['-i']).scan_ll_feature(
                    args['BD_ADDR'], args['--addr-type'], args['--timeout'])
            elif args['--smp-feature']:
                LeScanner(args['-i']).detect_pairing_feature(
                    args['BD_ADDR'], args['--addr-type'], args['--timeout'])
            else:
                scan_result = LeScanner(args['-i']).scan_devs(args['--timeout'], 
                    args['--scan-type'], args['--sort'])
        elif args['-m'] == 'sdp':
            SDPScanner(args['-i']).scan(args['BD_ADDR'])
        elif args['-m'] == 'gatt':
            scan_result = GattScanner(args['-i'], args['--io-capability']).scan(
                args['BD_ADDR'], args['--addr-type']) 
        # elif args['-m'] == 'stack':
        #     StackScanner(args['-i']).scan(args['BD_ADDR'])
        elif args['--clean']:
            BlueScanner(args['-i'])
            clean(BlueScanner(args['-i']).hci_bd_addr, args['BD_ADDR'])
        else:
            logger.error('Invalid scan mode')
        
        # Prints scan result
        if scan_result is not None:
            print()
            print()
            print(blue("----------------"+scan_result.type+" Scan Result"+"----------------"))
            scan_result.print()
            scan_result.store()
    # except (RuntimeError, ValueError, BluetoothError) as e:
    except BluescanPluginError as e:
        logger.error("{}: {}".format(e.__class__.__name__, e))
        sys.exit(1)
    except BTLEException as e:
        logger.error(str(e) + ("\nNo BLE adapter or missing sudo?" if 'le on' in str(e) else ""))
        sys.exit(1)
    except KeyboardInterrupt:
        if args != None and args['-i'] != None:
            try:
                output = subprocess.check_output(' '.join(['hciconfig', args['-i'], 'reset']), 
                                                 stderr=STDOUT, timeout=60, shell=True)
            except CalledProcessError as e:
                logger.warning("{}: {}".format(e.__class__.__name__, e))
        print()
        logger.info("Canceled\n")
    except TimeoutError as e:
        logger.error("Timeout")
        if args != None and args['-i'] != None:
            try:
                output = subprocess.check_output(' '.join(['hciconfig', args['-i'], 'reset']), 
                                                 stderr=STDOUT, timeout=60, shell=True)
            except CalledProcessError as e:
                logger.warning("{}: {}".format(e.__class__.__name__, e))
    except Exception as e:
        e_info = ''.join(format_exception(*sys.exc_info()))
        logger.debug("e_info: {{}}".format(e_info))
        logger.error("{}: {}".format(e.__class__.__name__, e))
        sys.exit(1)


if __name__ == '__main__':
    main()
