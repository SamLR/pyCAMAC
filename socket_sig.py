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
    
    # for send/receive 
    host = "192.168.0.2"
    port = 240
    buf = 1024
    addr = (host,port)
    
    # socket for sending to CAMAC
    sendSock = socket(AF_INET, SOCK_DGRAM)
    sendSock.settimeout(10)
    
    # message to send
    msg =  ecp_header.gettop() + naf.naf(8, 'testStatus')#, a = 0, data =2)
    print(msg)
    sendSock.sendto(msg, addr) 
    data = ''
    while (not data):
        data, addr2 = sendSock.recvfrom(buf)
        print(data)
    
    print(data)
    print(unpack("B"*24,data))
    
    # sample outputs naf = 16, 0, clearLAM, 
# (96, 96, 247, 0, 0, 0, 0, 7, 0, 0, 0, 1, 0, 0, 58, 184, 0, 0, 0, 1, 0, 3, 10, 0)
# (96, 96, 247, 0, 0, 0, 0, 7, 0, 0, 0, 1, 0, 0, 71, 184, 0, 0, 0, 1, 0, 3, 10, 0)
# (96, 96, 247, 0, 0, 0, 0, 7, 0, 0, 0, 1, 0, 0, 78, 184, 0, 0, 0, 1, 0, 3, 10, 0)
# (96, 96, 247, 0, 0, 0, 0, 7, 0, 0, 0, 1, 0, 0, 93, 184, 0, 0, 0, 1, 0, 3, 10, 0)

# naf = 24, testLAM, 0
# (96, 96, 247, 0, 0, 0, 0, 7, 0, 0, 0, 1, 0, 0, 122, 184, 0, 0, 0, 1, 0, 3, 10, 0)
# (96, 96, 247, 0, 0, 0, 0, 7, 0, 0, 0, 1, 0, 0, 144, 184, 0, 0, 0, 1, 0, 3, 10, 0)

#  naf = 16, readGrp1, 0
# (96, 96, 247, 0, 0, 0, 0, 7, 0, 0, 0, 1, 0, 0, 166, 184, 0, 0, 0, 1, 0, 3, 10, 0)
# (96, 96, 247, 0, 0, 0, 0, 7, 0, 0, 0, 1, 0, 0, 180, 184, 0, 0, 0, 1, 0, 3, 10, 0)