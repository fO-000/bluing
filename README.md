# bluescan

A Bluetooth scanner, support both BR and LE (device, GATT, SDP)!

## Requirements

```sh
apt install libglib2.0-dev
```

## Install

```sh
pip3 install bluescan
```

## Usage

```txt
# bluescan -h
Usage:
    bluescan (-h | --help)
    bluescan (-v | --version)
    bluescan [-i <hcix>] -m br [--inquiry-len=<n>] [--async]
    bluescan [-i <hcix>] -m le [--timeout=<sec>] [--le-scan-type=<type>] [--sort=<key>]
    bluescan [-i <hcix>] -m sdp BD_ADDR
    bluescan [-i <hcix>] -m gatt --addr-type=<type> BD_ADDR

Arguments:
    BD_ADDR    Target Bluetooth device address

Options:
    -h, --help               Display this help
    -v, --version            Show the version
    -i <hcix>                HCI device for scan [default: hci0]
    -m <mode>                Scan mode, support BR, LE, SDP and GATT
    --inquiry-len=<n>        Inquiry_Length parameter of HCI_Inquiry command [default: 8]
    --timeout=<sec>          Duration of LE scan [default: 10]
    --le-scan-type=<type>    Active or passive scan for LE scan [default: active]
    --sort=<key>             Sort the discovered devices by key, only support RSSI now [default: rssi]
    --async                  Asynchronous scan for BR scan
    --addr-type=<type>       Public or random
```

## Example

* Scan LE device

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

  ... ...
  ```

* Scan (Discover) GATT

  ```txt
  # bluescan -m gatt --addr-type=random 57:c6:75:e5:dc:e4
  Number of services: 9

  Service declaration attribute
      Handle: "attr handle" by using gatttool -b <BD_ADDR> --primary
      type: (May be primary service 00002800-0000-1000-8000-00805f9b34fb)
      Value (Service UUID): 9fa480e0-4967-4542-9390-d343dc5d04ae (Unknown service) 
  Number of characteristics: 1

      Characteristic declaration attribute
          handle:
          type:
          value:
              Properties: WRITE NOTIFY EXTENDED PROPERTIES  
              Characteristic value attribute handle: 0x0011
              Characteristic value attribute UUID:  af0badb1-5b99-43cd-917a-a77bc549e3cc (Unknown characteristic)
  
  ... ...
  ```

* Scan (Discover) SDP

  ```txt
  # bluescan -m sdp 9C:2E:A1:43:EB:5F
  Name: Headset Gateway
  Protocol RFCOMM
  Port 2
  Service Class: ['1112', '1203']
  Profiles: [('1108', 258)]
  Description: None
  Provider: None
  Service-id None

  Name: Handsfree Gateway
  Protocol RFCOMM
  Port 3
  Service Class: ['111F', '1203']
  Profiles: [('111E', 262)]
  Description: None
  Provider: None
  Service-id None
  
  ... ...
  ```
