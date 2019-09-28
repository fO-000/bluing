# bluescan

A Bluetooth device scanner, support both BR and LE!

## Requirements

```sh
apt install libglib2.0-dev
pip3 install pybluez bluepy docopt termcolor
```

## Install

```sh
make clean
# The following BLUEPY_PATH is an example, replace it with your own path.
make BLUEPY_PATH='/usr/local/lib/python3.7/dist-packages/bluepy'
make install
# reopen bash

# or don't install, just use script
# ./src/bluescan.py
```

## Uninstall

```sh
make uninstall
```

## Usage

```txt
# ./bluescan -h
bluescan v0.0.2

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
