# encoding: utf-8
"""
socket_sig.py

Created by Sam Cook on 2011-01-18.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import ecp_header
import naf
from socket import *
from struct import pack, unpack


if __name__ == '__main__':
    
    # TODO: string to hex for decoding return values (hexdump?)
    # TODO: test with ADC/TDC
    # TODO: start looking at patterns for cont receive. 
    
    host = "192.168.0.2"
    port = 240
    buf = 1024
    addr = (host,port)
    
    # socket for sending to CAMAC
    sendSock = socket(AF_INET, SOCK_DGRAM)
    sendSock.settimeout(20)
    # in theory this message should send the test LAM command A(0)F(8)
    #  header(24B) + COR(6B) + naf (0fff ffnn nnna aaas)
    clearLAM = b"\x25\x12"
    writeReg = b"\x41\x12"
    data = b"\x01\x00\x00\x00"
    # msg = ecp_header.gettop() + clearLAM
    # msg = ecp_header.getheader() + b'\x08\x01\x00\x00\x00\x00' + clearLAM
    # msg = naf.naf(16, 'readGrp1', a = 0)
    # msg = ecp_header.gettop() + naf.naf(16, 'clearLAM', a = 0)

    msg =  ecp_header.gettop() + naf.naf(16, 'clearLAM', a = 0)

    sendSock.sendto(msg, addr) 
    # receiver    
    # wait for a return signal
    data = ''
    while (not data):
        data, addr = sendSock.recvfrom(buf)
        if data:
            print ("got back:")
            print (data)
    
    

    msg = ecp_header.getheader() + b"\x80\x01\x00\x00\x00\x00" + naf.naf(16, 'readGrp1', a = 0)

    sendSock.sendto(msg, addr) 
    # receiver    
    # wait for a return signal
    data = ''
    while (not data):
        data, addr = sendSock.recvfrom(buf)
        if data:
            print ("got back:")
            print (data)

            print("done")
    