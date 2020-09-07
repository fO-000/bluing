# bluescan ---- A powerful Bluetooth scanner

> This document is also available in Chinese. See [README-Chinese.md](https://github.com/fO-000/bluescan/blob/master/README-Chinese.md)
>
> bluescan is a open source project by Sourcell Xu from DBAPP Security HatLab. Anyone may redistribute copies of bluescan to anyone under the terms stated in the GPL-3.0 license.

Aren't the previous Bluetooth scanning tools scattered and in disrepair? So we have this powerful Bluetooth scanner based on modern Python 3 ---- bluescan.

When hacking new Bluetooth targets, the scanner can help us to collect intelligence, such as:

* BR devices
* LE devices
* LMP features
* GATT services
* SDP services
* Vulnerabilities (demo)

## Requirements

This tool is based on BlueZ, the official Linux Bluetooth stack. The following packages need to be installed:

```sh
sudo apt install libglib2.0-dev libbluetooth-dev
```

When you play this tool in a Linux virtual machine, **making a USB Bluetooth adapter exclusive to it is recommended**, like the [Ostran Bluetooth USB Adapter OST-105 CSR 8150 v4.0](https://item.taobao.com/item.htm?spm=a230r.1.14.14.21b6705fm5gjj3&id=38948169460&ns=1&abbucket=6#detail) for 99 RMB. Of course, the best one to use is the little bit expensive [Parani UD100-G03](https://item.taobao.com/item.htm?spm=a230r.1.14.16.19bcf4b2koxeWN&id=561488544550&ns=1&abbucket=19#detail), 560 RMB. And if you want to try the vulnerability scanning, see `README.md` of [ojasookert/CVE-2017-0785](https://github.com/ojasookert/CVE-2017-0785).

## Install

The lastest bluescan will be uploaded to PyPI, so the following command can install bluescan:

```sh
sudo pip3 install bluescan
```

## Usage

```txt
$ bluescan -h
bluescan v0.2.2

A powerful Bluetooth scanner.

Author: Sourcell Xu from DBAPP Security HatLab.

License: GPL-3.0

Usage:
    bluescan (-h | --help)
    bluescan (-v | --version)
    bluescan [-i <hcix>] -m br [--inquiry-len=<n>]
    bluescan [-i <hcix>] -m lmp BD_ADDR
    bluescan [-i <hcix>] -m sdp BD_ADDR
    bluescan [-i <hcix>] -m le [--timeout=<sec>] [--le-scan-type=<type>] [--sort=<key>]
    bluescan [-i <hcix>] -m gatt [--include-descriptor] --addr-type=<type> BD_ADDR
    bluescan [-i <hcix>] -m vuln --addr-type=br BD_ADDR

Arguments:
    BD_ADDR    Target Bluetooth device address. FF:FF:FF:00:00:00 means local device.

Options:
    -h, --help                  Display this help.
    -v, --version               Show the version.
    -i <hcix>                   HCI device for scan. [default: hci0]
    -m <mode>                   Scan mode, support BR, LE, LMP, SDP, GATT and vuln.
    --inquiry-len=<n>           Inquiry_Length parameter of HCI_Inquiry command. [default: 8]
    --timeout=<sec>             Duration of LE scan. [default: 10]
    --le-scan-type=<type>       Active or passive scan for LE scan. [default: active]
    --sort=<key>                Sort the discovered devices by key, only support RSSI now. [default: rssi]
    --include-descriptor        Fetch descriptor information.
    --addr-type=<type>          Public, random or BR.
```

### Scan BR devices `-m br`

Classic Bluetooth devices may use three technologies: BR (Basic Rate), EDR (Enhanced Data Rate), and AMP (Alternate MAC/PHY). Since they all belong to the Basic Rate system, so when scanning these devices we call them BR device scanning:

![BR scan](https://github.com/fO-000/bluescan/blob/master/res/example-br-scan.png)

As shown above, through BR device scanning, we can get the address, page scan repetition mode, class of device, clock offset, RSSI, and the extended inquiry response (Name, TX power, and so on) of the surrounding classic Bluetooth devices.

### Scan LE devices `-m le`

Bluetooth technology, in addition to the Basic Rate system, is Low Energy (LE) system. When scanning Bluetooth low energy devices, it is called LE device scanning:

![LE scan](https://github.com/fO-000/bluescan/blob/master/res/example-le-scan.png)

As shown above, through LE device scanning, we can get the address, address type, connection status, RSSI, and GAP data of the surrounding LE devices.

### Scan SDP services

Classic Bluetooth devices tell the outside world about their open services through SDP. After SDP scanning, we can get service records of the specified classic Bluetooth device:

![SDP scan](https://github.com/fO-000/bluescan/blob/master/res/example-sdp-scan.png)

You can try to connect to these services for further hacking.

### Scan LMP features

Detecting the LMP features of classic Bluetooth devices allows us to judge the underlying security features of the classic Bluetooth device:

![LMP scan](https://github.com/fO-000/bluescan/blob/master/res/example-lmp-scan.png)

### Scan GATT services

LE devices tell the outside world about their open services through GATT. After GATT scanning, we can get the GATT service of the specified LE device. You can try to read and write these GATT data for further hacking:

![GATT scan](https://github.com/fO-000/bluescan/blob/master/res/example-gatt-scan.png)

### Vulnerabilities scanning (demo)

Vulnerability scanning is still in the demo stage, and currently only supports CVE-2017-0785:

```txt
$ sudo bluescan -m vuln --addr-type=br ??:??:??:??:??:??
... ...
CVE-2017-0785
```

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
  # rfkill from util-linux 2.36
  ```
