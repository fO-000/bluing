# bluescan：一个强大的蓝牙扫描器

> bluescan 是一个由 Sourcell Xu（杭州安恒信息 海特实验室）维护的开源项目。任何人都可以在 GPL-3.0 许可下分享该项目的源码。

先前的蓝牙扫描工具都是零零散散，而且年久失修对吗？于是我们有了这个基于现代 Python 3 开发的强大蓝牙扫描器 —— bluescan。

在测试新的蓝牙目标时，该扫描器可以帮助我们做好情报收集工作，比如：

* BR 设备扫描
* LE 设备扫描
* SDP 服务扫描
* LMP 特性扫描
* GATT 服务扫描
* 漏洞扫描 (demo)

## 依赖

bluescan 在底层基于 Linux 官方的 BlueZ 蓝牙协议栈。如下依赖的包需要被安装：

```sh
sudo apt install libglib2.0-dev libbluetooth-dev
```

当在 Linux 虚拟机中使用该工具时，**建议让虚拟机独占一个 USB 蓝牙适配器**，比如售价 99 块的 [Ostran 奥视通 USB 蓝牙适配器 OST-105 CSR 8150 v4.0](https://item.taobao.com/item.htm?spm=a230r.1.14.14.21b6705fm5gjj3&id=38948169460&ns=1&abbucket=6#detail)。当然最好用的还是有点小贵的 [Parani UD100-G03](https://item.taobao.com/item.htm?spm=a230r.1.14.16.19bcf4b2koxeWN&id=561488544550&ns=1&abbucket=19#detail)，560 元。如果你想尝试下漏洞扫描 (demo)，请参考 [ojasookert/CVE-2017-0785](https://github.com/ojasookert/CVE-2017-0785) 的 `README.md` 来解决依赖问题。

## 安装

最新的 bluescan 会被上传到 PyPI 上，因此执行如下命令即可安装 bluescan：

```sh
sudo pip3 install bluescan
```

## 功能和使用方法

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

### BR 设备扫描 `-m br`

经典蓝牙设备可能使用三种技术：BR (Basic Rate)、EDR (Enhanced Data Rate) 以及 AMP (Alternate MAC/PHY)。由于它们都属于 Basic Rate system，因此在扫描这些设备时统称为 BR 设备扫描：

![BR scan](https://github.com/fO-000/bluescan/blob/master/res/example-br-scan.png)

如上图，通过 BR 设备扫描，我们可以拿到周围经典蓝牙设备的地址、page scan 重复模式、类型、时钟偏移、RSSI 以及扩展 inquiry 结果。

### LE 设备扫描 `-m le`

蓝牙除了 Basic Rate system 就是 Low Energy (LE) system 了。当扫描周围的低功耗蓝牙设备时，称为 LE 设备扫描：

![LE scan](https://github.com/fO-000/bluescan/blob/master/res/example-le-scan.png)

如上图，通过 LE 扫描，我们可以拿到周围低功耗蓝牙设备的地址、地址类型、连接状态、RSSI 以及 GAP 数据。

### SDP 服务扫描 `-m sdp`

经典蓝牙设备通过 SDP 告诉外界自己开放的服务。通过 SDP 扫描，我们可以拿到指定经典蓝牙设备的 service record：

![SDP scan](https://github.com/fO-000/bluescan/blob/master/res/example-sdp-scan.png)

之后可以尝试连接这些 service，做进一步的安全测试。

### LMP 特性扫描 `-m lmp`

探测经典蓝牙设备的 LMP 特性，可以让我们判断目标设备底层的安全特性：

![LMP scan](https://github.com/fO-000/bluescan/blob/master/res/example-lmp-scan.png)

### GATT 服务扫描 `-m gatt`

低功耗蓝牙设备通过 GATT 告诉外界自己开放的服务。通过 GATT 扫描，我们可以拿到指定低功耗蓝牙设备的 GATT 数据。之后可以尝试读写这些 GATT 数据，做进一步的安全测试：

![GATT scan](https://github.com/fO-000/bluescan/blob/master/res/example-gatt-scan.png)

### 漏洞扫描 `-m vul` (demo)

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
  # rfkill from util-linux 2.36
  ```
