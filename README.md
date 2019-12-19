# bluescan

A Bluetooth device scanner, support both BR and LE!

## Requirements

```sh
apt install libglib2.0-dev
pip3 install pybluez bluepy docopt termcolor
```

## Install

```sh
pip3 install bluescan

# or
make clean
# The following BLUEPY_PATH is an example, replace it with your own path.
make BLUEPY_PATH='/usr/local/lib/python3.7/dist-packages/bluepy'
make install
# reopen bash

# or don't install, just using script
./src/bluescan.py
```

## Uninstall

```sh
# when installed by pip3
pip3 uninstall bluescan

# when installed by make
make uninstall

# when installed by setup.py
xargs rm -rf < install.rec
```

## Usage

```txt
# ./bluescan -h
bluescan v0.0.3

Usage:
    bluescan (-h | --help)
    bluescan (-v | --version)
    bluescan [-i <hcix>] -m br [--inquiry-len=<n>] [--async]
    bluescan [-i <hcix>] -m le [--timeout=<sec>] [--le-scan-type=<type>] [--sort=<key>]

Options:
    -h, --help               Display this help
    -v, --version            Show the version
    -i <hcix>                HCI device for scan [default: hci0]
    -m <mode>                Scan mode, BR or LE
    --inquiry-len=<n>        Inquiry_Length parameter of HCI_Inquiry command [default: 8]
    --timeout=<sec>          Duration of LE scan [default: 10]
    --le-scan-type=<type>    Active or passive scan for LE scan [default: active]
    --sort=<key>             Sort the discovered devices by key, only support RSSI now [default: rssi]
    --async                  Asynchronous scan for BR scan
```

## Example

LE scan:

```txt
# bluescan -m le
[Warnning] Before doing active scan, make sure you spoof your BD_ADDR.
LE active scanning on hci0...timeout 10 sec

BD_ADDR:     4c:34:78:26:ad:71
Addr type:   random
Connectable: True
RSSI:        -94 dB
General Access Profile:
        Flags (0x01): 06
        Manufacturer (0xFF): 4c0010054b1c3debf9


BD_ADDR:     08:b7:f3:52:71:3f
Addr type:   random
Connectable: False
RSSI:        -91 dB
General Access Profile:
        Manufacturer (0xFF): 060001092002001ae3ed568b370c29c336e1451d0a1309dd6982e7863d


BD_ADDR:     28:11:a5:41:28:27
Addr type:   public
Connectable: True
RSSI:        -91 dB
General Access Profile:
        Flags (0x01): 19
        Complete 16b Services (0x03): 0000febe-0000-1000-8000-00805f9b34fb,0000fe26-0000-1000-8000-00805f9b34fb
        Manufacturer (0xFF): 010951100d8851abf2f196f2
        Tx Power (0x0A): f6
```

BR scan:

```txt
# bluescan -m br
BR scanning on hci0...timeout 10.24 sec

[BR scan] discovered new device
addr: EC:51:BC:ED:6E:DC
name: OPPO R11
class: 0x5A020C


[BR scan] discovered new device
addr: 9C:2E:A1:43:EB:5F
name: 360syh
class: 0x5A020C
```
