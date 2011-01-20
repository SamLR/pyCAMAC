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
    
    # TODO: Dictionary of commands
    # TODO: string to hex for decoding return values (hexdump?)
    # TODO: test with ADC/TDC
    # TODO: start looking at patterns for cont receive. 
    # TODO: get hold of numPy etc in order to set up online monitoring 
    
    host = "192.168.0.2"
    port = 240
    buf = 1024
    addr = (host,port)
    
    # socket for sending to CAMAC
    sendSock = socket(AF_INET, SOCK_DGRAM)
    sendSock.settimeout(50)
    # in theory this message should send the test LAM command A(0)F(8)
    #  header(24B) + COR(6B) + naf (0fff ffnn nnna aaas)
    clearLAM = b"\x25\x12"
    writeReg = b"\x41\x12"
    data = b"\x01\x00\x00\x00"
    msg = ecp_header.gettop() + clearLAM
   
    sendSock.sendto(msg, addr) 
    # receiver    
    # wait for a return signal
    data = ''
    while (not data):
        data, addr = sendSock.recvfrom(buf)
        if data:
            print ("got back:")
            print (data)
            
    msg = ecp_header.getheader() + b"\x80\x01\x00\x00\x00\x00" + writeReg + data

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
    