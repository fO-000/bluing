# bluescan

A powerful Bluetooth scanner that supports scanning:

* BR devices
* LE devices
* GATT
* SDP
* Vulnerabilities (demo)

## Requirements

```sh
sudo apt install libglib2.0-dev libbluetooth-dev

# This tool is based on BlueZ, the official Linux Bluetooth stack.
# If you want to try the vulnerabilities scanning, see requirements in
# README.md of https://github.com/ojasookert/CVE-2017-0785
```

The Bluetooth adapters using following chips are recommended:

* Broadcom
* CSR

## Install

```sh
sudo pip3 install bluescan
```

## Usage

```txt
$ bluescan -h
Usage:
    bluescan (-h | --help)
    bluescan (-v | --version)
    bluescan [-i <hcix>] -m br [--inquiry-len=<n>] [--async]
    bluescan [-i <hcix>] -m le [--timeout=<sec>] [--le-scan-type=<type>] [--sort=<key>]
    bluescan [-i <hcix>] -m sdp BD_ADDR
    bluescan [-i <hcix>] -m gatt [--include-descriptor] --addr-type=<type> BD_ADDR
    bluescan [-i <hcix>] -m vuln --addr-type=br BD_ADDR

Arguments:
    BD_ADDR    Target Bluetooth device address

Options:
    -h, --help                  Display this help
    -v, --version               Show the version
    -i <hcix>                   HCI device for scan [default: hci0]
    -m <mode>                   Scan mode, support BR, LE, SDP, GATT and vuln
    --inquiry-len=<n>           Inquiry_Length parameter of HCI_Inquiry command [default: 8]
    --timeout=<sec>             Duration of LE scan [default: 10]
    --le-scan-type=<type>       Active or passive scan for LE scan [default: active]
    --sort=<key>                Sort the discovered devices by key, only support RSSI now [default: rssi]
    --async                     Asynchronous scan for BR scan
    --include-descriptor        Fetch descriptor information
    --addr-type=<type>          Public, random or BR
```

## Example

* Scan LE device

  ```txt
  $ sudo bluescan -m le
  [Warnning] Before doing active scan, make sure you spoof your BD_ADDR.
  LE active scanning on hci0...timeout 10 sec

  BD_ADDR:     4c:34:78:26:ad:71
  Addr type:   random
  Connectable: True
  RSSI:        -94 dB
  General Access Profile:
          Flags (0x01): 06
          Manufacturer (0xFF): 4c0010054b1c3debf9

  BD_ADDR:     28:11:a5:41:28:27
  Addr type:   public
  Connectable: True
  RSSI:        -91 dB
  General Access Profile:
          Flags (0x01): 19
          Complete 16b Services (0x03): 0000febe-0000-1000-8000-00805f9b34fb,0000fe26-0000-1000-8000-00805f9b34fb
          Manufacturer (0xFF): 010951100d8851abf2f196f2
          Tx Power (0x0A): f6

  ... ...
  ```

* Scan BR device

  ```txt
  $ sudo bluescan -m br
  BR scanning on hci0...timeout 10.24 sec

  [BR scan] discovered new device
  addr: EC:51:BC:ED:6E:DC
  name: OPPO R11
  class: 0x5A020C


  [BR scan] discovered new device
  addr: 9C:2E:A1:43:EB:5F
  name: 360syh
  class: 0x5A020C

  ... ...
  ```

* Scan (Discover) GATT

  ```txt
  $ sudo bluescan -m gatt --addr-type=random ??:??:??:??:??:??
  Number of services: 5


  Service declaration (3 characteristics)
      Handle: "attr handle" by using gatttool -b <BD_ADDR> --primary
      Type: (May be primary service 00002800-0000-1000-8000-00805f9b34fb)
      Value (Service UUID): 00001800-0000-1000-8000-00805f9b34fb (Generic Access)
      Permission: Read Only, No Authentication, No Authorization

      Characteristic declaration (0 descriptors)
          Handle: 0x0002
          Type: 00002803-0000-1000-8000-00805f9b34fb
          Value:
              Characteristic properties: READ WRITE  
              Characteristic value handle: 0x0003
              Characteristic UUID:  00002a00-0000-1000-8000-00805f9b34fb (Device Name)
          Permission: Read Only, No Authentication, No Authorization
      Characteristic value declaration
          Handle: 0x0003
          Type: 00002a00-0000-1000-8000-00805f9b34fb
          Value: b'???????'
          Permission: Higher layer profile or implementation specific
  
  ... ...
  ```

* Scan (Discover) SDP

  ```txt
  $ sudo bluescan -m sdp ??:??:??:??:??:??
  Service Record
  0x0000: ServiceRecordHandle (uint32)
      0x0001000a
  0x0001: ServiceClassIDList (sequence)
      uuid: 0x112f (Phonebook Access – PSE)
  0x0004: ProtocolDescriptorList (sequence)
      uuid: 0x0100 (L2CAP)
      uuid: 0x0003 (RFCOMM)
          channel: 0x13
      uuid: 0x0008 (OBEX)
  0x0005: BrowseGroupList (sequence)
      uuid: 0x1002 (PublicBrowseRoot)
  0x0009: BluetoothProfileDescriptorList (sequence)
      uuid: 0x1130 (Phonebook Access)
          <uint16 value="0x0101" />
  0x0100: unknown
      <text value="OBEX Phonebook Access Server " />
  0x0314: unknown
      <uint8 value="0x01" />
  
  ... ...
  ```

* Vulnerability (demo)

  ```txt
  $ sudo bluescan -m vuln --addr-type=br ??:??:??:??:??:??
  ... ...
  CVE-2017-0785
  ```
