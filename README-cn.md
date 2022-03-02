# bluescan：一个强大的蓝牙扫描器

<p align="center">
    <a href="https://github.com/fO-000/bluescan/blob/master/README.md">English</a> · <a href="https://github.com/fO-000/bluescan/blob/master/README-cn.md">简体中文</a>
</p>

<p align="center">
    <img src="https://img.shields.io/badge/python-3.9-blue">
    <!-- <a href="https://github.com/fO-000/bluescan/releases/latest"><img src="https://img.shields.io/github/v/release/fO-000/bluescan?style=plastic"></a> -->
    <a href="https://pypi.org/project/bluescan/"><img src="https://img.shields.io/pypi/v/bluescan?color=blue"></a>
    <img src="https://static.pepy.tech/personalized-badge/bluescan?period=total&units=none&left_color=black&right_color=orange&left_text=Downloads">
    <a href="https://github.com/fO-000/bluescan/blob/master/LICENSE"><img src="https://img.shields.io/github/license/fO-000/bluescan"></a>
</p>

<p align="center">
    <img src="https://img.shields.io/badge/Tested%20on-Ubuntu%2021.10%20(x64)%20%7C%20Kali%202021.4%20(x64)-brightgreen">
</p>

> 本项目由 Sourcell Xu（杭州安恒信息 海特实验室）维护。

蓝牙是一个复杂的协议，一个好用的扫描器可以快速帮我们窥探其内部的秘密。但先前的蓝牙扫描器存在功能不全、信息不直观以及年久失修等诸多问题。于是我们就有了这个基于现代 Python 3 开发的强大蓝牙扫描器 —— bluescan。

在 hacking 蓝牙目标时，bluescan 可以很好地帮助我们完成**情报收集**工作。它的主要功能如下：

* BR 设备扫描
* LE 设备扫描
* BR LMP 特性扫描
* LE LL 特性扫描
* SMP Pairing 特性扫描
* 嗅探 advertising physical channel PDU
* SDP 服务扫描
* GATT 服务扫描
* 漏洞扫描 (demo)

## 依赖

bluescan 基于 Linux 官方的 BlueZ 蓝牙协议栈开发。它仅支持在 Linux 上运行，且需要安装如下依赖包：

```sh
sudo apt install python3-pip python3-dev libcairo2-dev libgirepository1.0-dev \
                 libbluetooth-dev libdbus-1-dev bluez-tools python3-bluez
```

如果后续在[安装](https://github.com/fO-000/bluescan/blob/master/README-cn.md#%E5%AE%89%E8%A3%85) bluescan 时仍遇到错误，请尝试继续安装如下 package 来解决：

```sh
sudo apt install libglib2.0-dev gir1.2-gtk-3.0 \
                 python3-dbus python3-gi python3-gi-cairo
```

更重要的，**bluescan 至少需要 Python 3.9 的支持**。如果系统默认的 Python 版本低于 3.9，那么你需要做些额外的操作。比如在 Ubuntu 20.04.2 LTS (Focal Fossa) 中，系统默使用 Python 3.8，此时**额外的操作**如下：

```sh
sudo apt install python3.9 python3.9-dev

# To solve the runtime error "No module named '_dbus_bindings'"
cd /usr/lib/python3/dist-packages
sudo cp _dbus_bindings.cpython-38-x86_64-linux-gnu.so \
        _dbus_bindings.cpython-39-x86_64-linux-gnu.so
sudo cp _dbus_glib_bindings.cpython-38-x86_64-linux-gnu.so \
        _dbus_glib_bindings.cpython-39-x86_64-linux-gnu.so
```

若在 Linux 虚拟机中使用该工具，则建议让虚拟机**独占一个 USB 蓝牙适配器**。比如售价 99 块的 [Ostran 奥视通 USB 蓝牙适配器 OST-105 CSR 8150 v4.0](https://item.taobao.com/item.htm?spm=a230r.1.14.14.21b6705fm5gjj3&id=38948169460&ns=1&abbucket=6#detail)：

![OST-105](https://raw.githubusercontent.com/fO-000/bluescan/master/res/OST-105.jpg)

[Parani UD100-G03](https://item.taobao.com/item.htm?spm=a230r.1.14.16.19bcf4b2koxeWN&id=561488544550&ns=1&abbucket=19#detail) 比上面奥视通的适配器好用一些，但 560 元的价格有点小贵：

![Parani UD100-G03](https://raw.githubusercontent.com/fO-000/bluescan/master/res/Parani-UD100-G03.jpg)

如果你想尝试下漏洞扫描 (demo)，请参考 [ojasookert/CVE-2017-0785](https://github.com/ojasookert/CVE-2017-0785) 的 `README.md` 来解决依赖问题。

### [micro:bit](https://microbit.org/) 以及专用固件

若想使用 bluescan 嗅探 advertising physical channel PDU (`-m le --adv`)，我们需要执行如下命令，把构建好的固件 `bin/bluescan-advsniff-combined.hex` 下载到 1 到 3 块 micro:bit(s) 中（推荐同时用 3 块）：

```sh
cd bluescan
cp bin/bluescan-advsniff-combined.hex /media/${USER}/MICROBIT
cp bin/bluescan-advsniff-combined.hex /media/${USER}/MICROBIT1
cp bin/bluescan-advsniff-combined.hex /media/${USER}/MICROBIT2
```

![3 micro:bit](https://raw.githubusercontent.com/fO-000/bluescan/master/res/3-microbit.jpg)

如果你想自己编译固件，则需要安装如下依赖包：

```sh
sudo apt install yotta ninja-build
```

然后执行下面的命令即可自动编译（**需要网络自动解决依赖**）并下载固件到已接入 PC 的 micro:bit(s)：

```sh
cd bluescan
make flash
```

## 安装

> 请先阅读“[依赖](https://github.com/fO-000/bluescan/blob/master/README-cn.md#%E4%BE%9D%E8%B5%96)”一节，以避免安装时和运行时错误。

最新的 bluescan 会被上传到 PyPI 上，因此执行如下命令即可安装 bluescan：

```sh
sudo pip3 install bluescan
```

如果你没有使用系统默认的 Python，而是自己安装的 Python 3.9，那么需要这样安装 bluescan：

```sh
sudo python3.9 -m pip install bluescan
```

## 使用

```txt
$ bluescan -h
bluescan

A powerful Bluetooth scanner.

Author: Sourcell Xu from DBAPP Security HatLab.

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
    bluescan [-i <hci>] -m gatt [--io-capability=<name>] --addr-type=<type> BD_ADDR
    bluescan [-i <hci>] -m vuln [--addr-type=<type>] BD_ADDR

Arguments:
    BD_ADDR    Target Bluetooth device address. FF:FF:FF:00:00:00 means local 
               device.

Options:
    -h, --help                Display this help.
    -v, --version             Show the version.
    -i <hci>                  HCI device used for subsequent scans. [default: The first HCI device]
    -m <mode>                 Scan mode, support BR, LE, SDP, GATT and vuln.
    --inquiry-len=<n>         Inquiry_Length parameter of HCI_Inquiry command. [default: 8]
    --lmp-feature             Scan LMP features of the remote BR/EDR device.
    --scan-type=<type>        Scan type used for scanning LE devices, active or 
                              passive. [default: active]
    --timeout=<sec>           Duration of the LE scanning, but may not be precise. [default: 10]
    --sort=<key>              Sort the discovered devices by key, only support 
                              RSSI now. [default: rssi]
    --adv                     Sniff advertising physical channel PDU. Need at 
                              least one micro:bit.
    --ll-feature              Scan LL features of the remote LE device.
    --smp-feature             Detect pairing features of the remote LE device.
    --channel=<num>           LE advertising physical channel, 37, 38 or 39). [default: 37,38,39]
    --addr-type=<type>        Type of the LE address, public or random.
    --io-capability=<name>    Set IO capability of the agent. Available value: DisplayOnly, DisplayYesNo, 
                              KeyboardOnly, NoInputNoOutput, KeyboardDisplay (KeyboardOnly) [default: NoInputNoOutput]
    --clean                   Clean the cached data of a remote device.
```

### BR 设备扫描 `-m br`

经典蓝牙设备可能使用三种技术：BR (Basic Rate)、EDR (Enhanced Data Rate) 以及 AMP (Alternate MAC/PHY)。由于它们都属于 Basic Rate system，因此在扫描这些设备时统称为 BR 设备扫描：

![BR dev scan](https://raw.githubusercontent.com/fO-000/bluescan/master/res/example-br-dev-scan.png)

如上图，通过 BR 设备扫描，我们可以拿到周围经典蓝牙设备的地址、page scan 重复模式、类型、时钟偏移、RSSI 以及扩展 inquiry 结果。

### LE 设备扫描 `-m le`

蓝牙除了 Basic Rate system 就是 Low Energy (LE) system 了。当扫描周围的低功耗蓝牙设备时，称为 LE 设备扫描：

![LE dev scan](https://raw.githubusercontent.com/fO-000/bluescan/master/res/example-le-dev-scan.png)

如上图，通过 LE 扫描，我们可以拿到周围低功耗蓝牙设备的地址、地址类型、连接状态、RSSI 以及 GAP 数据。

### BR LMP 特性扫描 `-m br --lmp-feature`

探测经典蓝牙设备的 LMP 特性，可以帮我们测试其底层安全性：

![BR LMP feature scan](https://raw.githubusercontent.com/fO-000/bluescan/master/res/example-br-lmp-feature-scan.png)

### LE LL 特性扫描 `-m le --ll-feature`

探测低功耗蓝牙设备的链路层特性：

![LE LL feature scan](https://raw.githubusercontent.com/fO-000/bluescan/master/res/example-le-ll-feature-scan.png)

### SMP Pairing 特性扫描 `-m le --smp-feature`

探测远端低功耗蓝牙设备的配对特征：

![SMP feature scan](https://raw.githubusercontent.com/fO-000/bluescan/master/res/smp-feature-scan.png)

### 嗅探 advertising physical channel PDU `-m le --adv`

相比 HCI 之上的扫描，利用 micro:bit 站在链路层嗅探 advertising physical channel PDU，可拿到更丰富的 LE 设备活动信息：

![LE adv sniff](https://raw.githubusercontent.com/fO-000/bluescan/master/res/example-le-adv-sniff.png)

:bulb: 该扫描模式有隐藏功能。

### SDP 服务扫描 `-m sdp`

经典蓝牙设备通过 SDP 告诉外界自己开放的服务。通过 SDP 扫描，我们可以拿到它们的 service record：

![SDP scan](https://raw.githubusercontent.com/fO-000/bluescan/master/res/example-sdp-scan.png)

之后可以尝试连接这些 service，做进一步的安全测试。

### GATT 服务扫描 `-m gatt`

低功耗蓝牙设备通过 GATT 告诉外界自己开放的服务。通过 GATT 扫描，我们可以拿到它们的 GATT 数据。之后可以尝试读写这些 GATT 数据，做进一步的安全测试：

![GATT scan](https://raw.githubusercontent.com/fO-000/bluescan/master/res/example-gatt-scan.png)

### 漏洞扫描 `-m vuln` (demo)

漏洞扫描还处于 demo 阶段，目前仅支持 CVE-2017-0785：

```txt
$ sudo bluescan -m vuln --addr-type=br ??:??:??:??:??:??
... ...
CVE-2017-0785
```

## FAQ

* Exception: "Can't find the ID of hci0 in rfkill"

  有一些老版本的 rfkill 不支持 `-r` 或 `-n` 选项，比如：
  
  ```sh
  # Ubuntu 16.04.1
  rfkill --version
  # rfkill 0.5-1ubuntu3 (Ubuntu)"
  ```
  
  请升级 rfkill 或者操作系统来解决该问题。

  PS：我使用的操作系统是 Kali，其中 rfkill 的版本是:
  
  ```sh
  # Kali
  rfkill --version
  # rfkill from util-linux 2.37.2
  ```

如果遇到如下错误，可重启 bluetooth 服务恢复 (`sudo systemctl restart bluetooth.service`)：

* `[ERROR] Failed to execute management command 'scanend' (code: 11, error: Rejected)`
