# encoding: utf-8
"""
socket_sig.py

Created by Sam Cook on 2011-01-18.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import ecp_header
from socket import *
from struct import pack


if __name__ == '__main__':
    
    host = "192.168.0.2"
    port = 240
    buf = 1024
    addr = (host,port)
    
    # socket for sending to CAMAC
    sendSock = socket(AF_INET, SOCK_DGRAM)
    sendSock.settimeout(50)
    # in theory this message should send the test LAM command A(0)F(8)
    # pack this instead
    msg = ecp_header.getheader() + b"\x81\x00\x01\xFF\x23\x01\x00\x00"
    # header is always 24 bytes, the message is variable but normally 4 bytes for a single naf()
    packstr = "I"*24 + "I"*8
    msg = pack(packstr, msg)
    sendSock.sendto(msg, addr) 
    # receiver    
    # wait for a return signal
    data = ''
    while (not data):
        data, addr = sendSock.recvfrom(buf)
        if data:
            print (data)
            
    print("done")
    