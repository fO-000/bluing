#!/usr/bin/env python3

import dbus
from dbus import SystemBus
import logging
from pyclui import Logger

from .common import mainloop
from .common import Rejected
from .common import APP_NAME


IFACE_AGENT1 = 'org.bluez.Agent1'

logger = Logger(__name__, logging.INFO)


def set_trusted(bus:SystemBus, path):
    props = dbus.Interface(
        bus.get_object('org.bluez', path), 'org.freedesktop.DBus.Properties')
    props.Set('org.bluez.Device1', 'Trusted', True)


class Agent(dbus.service.Object):
    exit_on_release = True

    def set_exit_on_release(self, exit_on_release):
        self.exit_on_release = exit_on_release


    def __init__(self, bus:SystemBus, idx:int) -> None:
        self.path = '/x/' + APP_NAME + '/agent' + str(idx)
        self.bus = bus
        super().__init__(bus, self.path)


    @dbus.service.method(IFACE_AGENT1, in_signature='', out_signature='')
    def Release(self):
        logger.info('Entered Agent.Release method')
        if self.exit_on_release:
            mainloop.quit()


    @dbus.service.method(IFACE_AGENT1, in_signature='os', out_signature='')
    def AuthorizeService(self, device, uuid):
        logger.info('Agent, AuthorizeService (%s, %s)' % (device, uuid))
        # authorize = input('Authorize connection (yes/no): ')
        # if authorize == 'yes':
        #     return
        return
        raise Rejected('Connection rejected by user')


    @dbus.service.method(IFACE_AGENT1, in_signature='o', out_signature='s')
    def RequestPinCode(self, device):
        logger.info('Agent, RequestPinCode (%s)' % (device))
        set_trusted(self.bus, device)
        return input('Enter PIN Code: ')


    @dbus.service.method(IFACE_AGENT1, in_signature='o', out_signature='u')
    def RequestPasskey(self, device):
        logger.info('Agent, RequestPasskey (%s)' % (device))
        set_trusted(self.bus, device)
        passkey = input('Enter passkey: ')
        return dbus.UInt32(passkey)


    @dbus.service.method(IFACE_AGENT1, in_signature='ouq', out_signature='')
    def DisplayPasskey(self, device, passkey, entered):
        logger.info('Agent, DisplayPasskey (%s, %06u entered %u)' % (device, passkey, entered))


    @dbus.service.method(IFACE_AGENT1, in_signature='os', out_signature='')
    def DisplayPinCode(self, device, pincode):
        logger.info('Agent, DisplayPinCode (%s, %s)' % (device, pincode))


    @dbus.service.method(IFACE_AGENT1, in_signature='ou', out_signature='')
    def RequestConfirmation(self, device, passkey):
        logger.debug('Agent, RequestConfirmation (%s, %06d)' % (device, passkey))
        # confirm = input('Confirm passkey (yes/no): ')
        # if confirm == 'yes':
        #     set_trusted(self.bus, device)
        #     return
        return
        raise Rejected('Passkey does not match')


    @dbus.service.method(IFACE_AGENT1, in_signature='o', out_signature='')
    def RequestAuthorization(self, device):
        logger.debug('Entered Agent.RequestAuthorization method, (%s)' % (device))
        # auth = input('Authorize? (yes/no): ')
        # if auth == 'yes':
        #     return
        return
        raise Rejected('Pairing rejected')


    @dbus.service.method(IFACE_AGENT1, in_signature='', out_signature='')
    def Cancel(self):
        logger.info('Entered Agent.Cancel method')
