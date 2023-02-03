#!/usr/bin/env python

import dbus
from xpycommon.log import Logger
from xpycommon.bluetooth.bluez import BtAgent

from .. import APP_NAME
from . import LOG_LEVEL


logger = Logger(__name__, LOG_LEVEL)


class GattScanBtAgent(BtAgent):
    def __init__(self, io_cap: str = 'NoInputNoOutput', suffix: int = 0) -> None:
        super().__init__(APP_NAME, io_cap, suffix)
    
    @dbus.service.method(BtAgent.agent_iface, in_signature='o', out_signature='s')
    def RequestPinCode(self, device):
        logger.info('Agent, RequestPinCode (%s)' % (device))
        self.set_trusted(device)
        return '0000'

    @dbus.service.method(BtAgent.agent_iface, in_signature='o', out_signature='u')
    def RequestPasskey(self, device):
        logger.debug("Entered RequestPasskey(self, device={})".format(device))
        self.set_trusted(device)
        passkey = 00000000
        return dbus.UInt32(passkey)

    @dbus.service.method(BtAgent.agent_iface, in_signature='ou', out_signature='')
    def RequestConfirmation(self, device, passkey):
        logger.debug("Entered RequestConfirmation(self, device={}, passkey={:06})".format(device, passkey))
        logger.info("Passkey {:06} automatically comfirmed".format(passkey))
        self.set_trusted(device)
        return

    @dbus.service.method(BtAgent.agent_iface, in_signature='o', out_signature='')
    def RequestAuthorization(self, device):
        logger.debug("Entered RequestAuthorization(self, device={})".format(device))
        self.set_trusted(device)
        return

    @dbus.service.method(BtAgent.agent_iface, in_signature='os', out_signature='')
    def AuthorizeService(self, device, uuid):
        logger.debug("Entered AuthorizeService(self, device={}, uuid={})".format(device, uuid))
        self.set_trusted(device)
        return
