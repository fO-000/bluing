# bluescan

bluescan 可以在 BR (`-m br`) 或 LE (`-m le`) 模式下扫描周围的 Bluetooth 设备。

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

# or don't install, just using script
# ./src/bluescan.py
```

## Uninstall

```sh
make uninstall
```

## Usage

```txt
# ./bluescan -h
bluescan v0.0.1

Usage:
    bluescan (-h | --help)
    bluescan (-v | --version)
    bluescan [-i <hcix>] -m br [--timeout=<sec>]
    bluescan [-i <hcix>] -m le [--timeout=<sec>] [--le-scan-type=<type>]

Options:
    -h, --help               Display this help.
    -v, --version            Show the version.
    -i <hcix>                HCI device. [default: hci0]
    -m <mode>                Scan mode, br or le.
    --timeout=<sec>          Duration of scan. Only valid in le scan. [default: 10]
    --le-scan-type=<type>    Active or passive scan for le scan. [default: active]
```

## 解决 scanend Failed

在执行 `bluescan -m le` 时可能报 scanend Failed：

```txt
Failed to execute management command 'scanend' (code: 11, error: Rejected)
```

导致该问题可能的原因与对应的解决办法如下：

* hcix blocked

  此时检查 hcix 是否被 block，若 block 则解锁即可解决问题：

  ```txt
  # rfkill
  ID TYPE      DEVICE      SOFT      HARD
  0 bluetooth hci0   unblocked unblocked
  1 bluetooth hci1     blocked unblocked

  # rfkill unblock 1
  # rfkill
  ID TYPE      DEVICE      SOFT      HARD
  0 bluetooth hci0   unblocked unblocked
  1 bluetooth hci1   unblocked unblocked
  ```

* hcix 被占用

  ```sh
  hciconfig hcix reset
  hciconfig hcix up
  ```

  > 当 BR 扫描出其他问题时也可以通过重置 hcix 解决。

## 解决无法执行 pasvend 的问题

在执行 `bluescan -m le --le-scan-type=passive` 时可能报如下错误：

```txt
Failed to execute management command 'pasvend'
```

此时重启 Bluetooth service 可以解决：

```sh
systemctl restart bluetooth.service
```
