# bluescan ---- A Bluetooth scanner for hacking

<p align="center">
    <a href="https://github.com/fO-000/bluescan/blob/master/README.md">English</a> · <a href="https://github.com/fO-000/bluescan/blob/master/README-cn.md">简体中文</a>
</p>

<p align="center">
    <img src="https://img.shields.io/badge/python-3.10-blue">
    <a href="https://pypi.org/project/bluescan/"><img src="https://img.shields.io/pypi/v/bluescan?color=blue"></a>
    <!-- <img src="https://static.pepy.tech/personalized-badge/bluescan?period=total&units=none&left_color=black&right_color=orange&left_text=Downloads"> -->
    <a href="https://pepy.tech/badge/bluescan"><img src="https://pepy.tech/badge/bluescan"></a>
    <a href="https://github.com/fO-000/bluescan/blob/master/LICENSE"><img src="https://img.shields.io/github/license/fO-000/bluescan"></a>
</p>

<p align="center">
    <img src="https://img.shields.io/badge/Tested%20on-Ubuntu%2022.04%20(x64)%20%7C%20Kali%202022.3%20(x64)%20%7C%20Kali%20on%20Raspberry%20Pi%204%202022.3%20(aarch64)-brightgreen">
</p>

## TL;DR

```sh
# Install dependencies
sudo apt install python3-pip python3-dev libcairo2-dev libgirepository1.0-dev \
                 libbluetooth-dev libdbus-1-dev bluez-tools python3-cairo-dev \
                 rfkill meson patchelf bluez

# Install bluescan
sudo pip install bluescan

# Have fun!
bluescan --help
sudo bluescan -m <br|le|sdp|gatt> [opt]... [BD_ADDR]
```

## Introduction

Bluetooth is a complex protocol, and a good scanner can quickly help us peek inside its secrets. But previous Bluetooth scanners suffered from a number of problems such as incomplete functionality, unintuitive information and out of repair. So we came up with this powerful Bluetooth scanner based on modern Python 3 ---- bluescan.

When hacking Bluetooth targets, bluescan can be very useful for **intelligence collecting**. It can collect the following information:

* BR devices
* LE devices
* BR LMP features
* LE LL features
* SMP Pairing features
* Real-time advertising physical channel PDU
* SDP services
* GATT services
* Vulnerabilities (deprecated and will be presented in another way)

## Requirements

bluescan is based on BlueZ, the official Linux Bluetooth stack. It only supports running on Linux, and the following packages need to be installed:

```sh
sudo apt install python3-pip python3-dev libcairo2-dev libgirepository1.0-dev \
                 libbluetooth-dev libdbus-1-dev bluez-tools python3-cairo-dev \
                 rfkill meson patchelf bluez
```

If you still encounter errors when [installing](https://github.com/fO-000/bluescan#install) bluescan, please try to install the following packages to solve: 

```sh
sudo apt install libglib2.0-dev gir1.2-gtk-3.0 \
                 python3-dbus python3-gi python3-gi-cairo
```

When you play this tool in a Linux virtual machine, **making a USB Bluetooth adapter exclusive to it is recommended**; If you play this tool in a Raspberry Pi, it is also recommended to connect a better USB Bluetooth adapter, although the Raspberry Pi itself has one.

The recommended USB Bluetooth adapter is [Parani UD100-G03](https://item.taobao.com/item.htm?spm=a230r.1.14.16.19bcf4b2koxeWN&id=561488544550&ns=1&abbucket=19#detail)：

![Parani UD100-G03](https://raw.githubusercontent.com/fO-000/bluescan//master/res/Parani-UD100-G03.jpg)

### Dedicated firmware for [micro:bit](https://microbit.org/)

If you want to use bluescan to sniff the advertising physical channel PDU (`-m le --adv`), you need to execute the following command to download the dedicated firmware `bin/bluescan-advsniff-combined.hex` to 1 or 3 micro:bit(s). It is recommended to use 3 micro:bits at the same time.

```sh
cd bluescan
cp bin/bluescan-advsniff-combined.hex /media/${USER}/MICROBIT
cp bin/bluescan-advsniff-combined.hex /media/${USER}/MICROBIT1
cp bin/bluescan-advsniff-combined.hex /media/${USER}/MICROBIT2
```

![3 micro:bit](https://raw.githubusercontent.com/fO-000/bluescan//master/res/3-microbit.jpg)

If you want to compile the firmware yourself, first install the following packages:

```sh
sudo apt install yotta ninja-build
```

Then execute the following command, it will automatically compile (**requires network to automatically resolve dependencies**) and download the firmware to the micro:bit(s) which connected to your PC:

```sh
cd bluescan
make flash
```

## Install

> Please read the "[Requirements](https://github.com/fO-000/bluescan#requirements)" section first to avoid installation and runtime errors.

The lastest bluescan will be uploaded to PyPI, so the following command can install bluescan:

```sh
sudo pip install bluescan
```

If you do not use the system default Python, but install Python 3.10 yourself, then you need to install bluescan like this: 

```txt
sudo python3.10 -m pip install bluescan
```

## Usage

```txt
$ bluescan -h
bluescan

A Bluetooth scanner for hacking.

Author: Sourcell Xu

License: GPL-3.0

Usage:
    bluescan (-h | --help)
    bluescan (-v | --version)
    bluescan [-i <hci>] --clean BD_ADDR
    bluescan [-i <hci>] -m br [--inquiry-len=<n>]
    bluescan [-i <hci>] -m br --lmp-feature BD_ADDR
    bluescan [-i <hci>] -m le [--scan-type=<type>] [--timeout=<sec>] [--sort=<key>]
    bluescan [-i <hci>] -m le [--ll-feature|--smp-feature] [--timeout=<sec>] --addr-type=<type> BD_ADDR
    bluescan -m le --adv [--channel=<num>]
    bluescan [-i <hci>] -m sdp BD_ADDR
    bluescan [-i <hci>] -m gatt [--io-capability=<name>] [--addr-type=<type>] BD_ADDR
    bluescan --list-installed-plugins
    bluescan --install-plugin=<path>
    bluescan --uninstall-plugin=<name>
    bluescan --plugin=<name> [--] [<plugin-opt>...]

Arguments:
    BD_ADDR       Target Bluetooth device address. FF:FF:FF:00:00:00 means local 
                  device.
    plugin-opt    Options for a plugin.

Options:
    -h, --help                   Display this help.
    -v, --version                Show the version.
    -i <hci>                     HCI device used for subsequent scans. [default: The default HCI device]
    -m <mode>                    Scan mode, support br, le, sdp and gatt.
    --inquiry-len=<n>            Inquiry_Length parameter of HCI_Inquiry command. [default: 8]
    --lmp-feature                Scan LMP features of the remote BR/EDR device.
    --scan-type=<type>           Scan type used for scanning LE devices, active or 
                                 passive. [default: active]
    --timeout=<sec>              Duration of the LE scanning, but may not be precise. [default: 10]
    --sort=<key>                 Sort the discovered devices by key, only support 
                                 RSSI now. [default: rssi]
    --adv                        Sniff advertising physical channel PDU. Need at 
                                 least one micro:bit.
    --ll-feature                 Scan LL features of the remote LE device.
    --smp-feature                Detect pairing features of the remote LE device.
    --channel=<num>              LE advertising physical channel, 37, 38 or 39). [default: 37,38,39]
    --addr-type=<type>           Type of the LE address, public or random.
    --io-capability=<name>       Set IO capability of the agent. Available value: DisplayOnly, DisplayYesNo, 
                                 KeyboardOnly, NoInputNoOutput, KeyboardDisplay (KeyboardOnly) [default: NoInputNoOutput]
    --clean                      Clean the cached data of a remote device.
    --list-installed-plugins     List plugins in local system
    --install-plugin=<path>      Install a plugin
    --uninstall-plugin=<name>    Uninstall a plugin
    --plugin=<name>              Execute plugin by name.
```

### Scan BR devices `-m br`

Classic Bluetooth devices may use three technologies: BR (Basic Rate), EDR (Enhanced Data Rate), and AMP (Alternate MAC/PHY). Since they all belong to the Basic Rate system, so when scanning these devices we call them BR device scanning:

![BR dev scan](https://raw.githubusercontent.com/fO-000/bluescan//master/res/example-br-dev-scan.png)

As shown above, through BR device scanning, we can get the address, page scan repetition mode, class of device, clock offset, RSSI, and the extended inquiry response (Name, TX power, and so on) of the surrounding classic Bluetooth devices.

### Scan LE devices `-m le`

Bluetooth technology, in addition to the Basic Rate system, is Low Energy (LE) system. When scanning Bluetooth low energy devices, it is called LE device scanning:

![LE dev scan](https://raw.githubusercontent.com/fO-000/bluescan//master/res/example-le-dev-scan.png)

As shown above, through LE device scanning, we can get the address, address type, connection status, RSSI, and GAP data of the surrounding LE devices.

### Scan BR LMP features `-m br --lmp-feature`

Detecting the LMP features of classic Bluetooth devices allows us to judge the underlying security features of them:

![BR LMP feature scan](https://raw.githubusercontent.com/fO-000/bluescan//master/res/example-br-lmp-feature-scan.png)

### Scan LE LL features `-m le --ll-feature`

Detecting the LL (Link Layer) features fo the LE devices:

![LE LL feature scan](https://raw.githubusercontent.com/fO-000/bluescan//master/res/example-le-ll-feature-scan.png)

### Detect SMP Pairing features `-m le --smp-feature`

Detecting the SMP Pairing features of the remote LE device:

![SMP feature scan](https://raw.githubusercontent.com/fO-000/bluescan/master/res/smp-feature-scan.png)

### Sniffing advertising physical channel PDU `-m le --adv`

Compared with scanning adove the HCI, using micro:bit to sniff the advertising physical channel PDU at the link layer, you can get richer LE device activity information:

![LE adv sniff](https://raw.githubusercontent.com/fO-000/bluescan//master/res/example-le-adv-sniff.png)

:bulb: The scan mode has a hidden function.

### Scan SDP services `-m sdp`

Classic Bluetooth devices tell the outside world about their open services through SDP. After SDP scanning, we can get service records of them:

![SDP scan](https://raw.githubusercontent.com/fO-000/bluescan//master/res/example-sdp-scan.png)

You can try to connect to these services for further hacking.

### Scan GATT services `-m gatt`

LE devices tell the outside world about their open services through GATT. After GATT scanning, we can get the GATT service of them. You can try to read and write these GATT data for further hacking:

![GATT scan](https://raw.githubusercontent.com/fO-000/bluescan//master/res/example-gatt-scan.png)

## FAQ

* Exception: "Can't find the ID of hci0 in rfkill"

  Some old versions of rfkill do not support `-r` and `-n` options, like:
  
  ```sh
  # Ubuntu 16.04.1
  rfkill --version
  # rfkill 0.5-1ubuntu3 (Ubuntu)"
  ```
  
  Please upgrade rfkill or OS to solve this problem.

  PS: My system is Kali, and the version of rfkill is:
  
  ```sh
  # Kali
  rfkill --version
  # rfkill from util-linux 2.37.2
  ```

If you encounter the following error, restart bluetooth service to recover (`sudo systemctl restart bluetooth.service`):

* `[ERROR] Failed to execute management command 'scanend' (code: 11, error: Rejected)`
