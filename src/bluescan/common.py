#!/usr/bin/env python3

from dbus.exceptions import DBusException
from gi.repository import GObject

APP_NAME = 'bluescan'
BLUEZ_NAME = 'org.bluez' # The well-known name of bluetoothd

IFACE_PROP = 'org.freedesktop.DBus.Properties'

mainloop = GObject.MainLoop()

class InvalidArgsException(DBusException):
    _dbus_error_name = 'org.freedesktop.DBus.Error.InvalidArgs'

class NotSupportedException(DBusException):
    _dbus_error_name = 'org.bluez.Error.NotSupported'

class NotPermittedException(DBusException):
    _dbus_error_name = 'org.bluez.Error.NotPermitted'

class InvalidValueLengthException(DBusException):
    _dbus_error_name = 'org.bluez.Error.InvalidValueLength'

class FailedException(DBusException):
    _dbus_error_name = 'org.bluez.Error.Failed'

class Rejected(DBusException):
    _dbus_error_name = "org.bluez.Error.Rejected"
