#!/usr/bin/env python
# encoding: utf-8
"""
camac_cmds.py

Created by Sam Cook on 2011-01-24.
Copyright (c) 2011. All rights reserved.
"""

from socket import socket
from ecp_header import *
from naf import *
from struct import unpack
from time import sleep

recvPackStr = ecp_header.headerPackStr + 'B'*3

def recv(sock, addr, verbose=False, returnAddr=False, packStr=recvPackStr):
    """returns the status as received from the socket, sock at addr. 
    options: verbose - returns full packed
             returnAddr - returns the return address
             packStr - alternate packing string (eg if header)
    """
    data = ''
    while not data:
        data, rtn_addr = sock.recvfrom(1024)
        
    s = unpack(packStr, data)
    res = s if verbose else (s[-3], s[-2], s[-1])
    res = (res + rtn_addr) if returnAddr else res
    return res

def cccc(sock, addr):
    """
    send CAMAC clear to socket, sock, at address addr
    """
    msg = ecp_header.gettop(cmd = 'cmd_clr')
    sock.sendto(msg, addr)
    return recv(sock, addr)

def cccz(sock, addr):
    """
    send CAMAC init to socket, sock, at address addr
    """
    msg = ecp_header.gettop(cmd = 'cmd_init')
    sock.sendto(msg, addr)
    return recv(sock, addr)

def cccc(sock, addr):
    """
    send CAMAC inhibit to socket, sock, at address addr
    """
    msg = ecp_header.gettop(cmd = 'cmd_inhibit')
    sock.sendto(msg, addr)
    return recv(sock, addr)

def cssa(sock, addr, n, f, a = -1, data = -1, timeout = 1, verbose = False):
    """
    wait until a LAM signal is received
    sends to socket sock at address addr
    n = slot no,
    f = camac function, 
    a is optional based on function and the subaddress of the module 
    d is optional based on function and the data to be passed
    returns the received packet as a list: n_words, dat and status
    """
    msg = ecp_header.gettop() + naf(n, f, a = -1, data = -1)
    sock.sendto(msg, addr)
    sock.settimeout(timeout)
    data = ''
    return recv(sock, addr, verbose)

# TODO maybe move this to a higher level?
# TODO move all of sock stuff into naf or lower level?
# TODO TEST THIS 
# TODO check that rcvd[2] _is_ the status and is != 0 for good returns
def waitForLAM(sock, addr, maxpolls = 1000):
    """
    Polls the LAM then sleeps for 10us
    """
    for i in range(maxpolls):
        rcvd = cssa(sock, addr, 24, 0, 'testLAM')
        if not (rcvd [2]):
            break
            sleep(0.01)
        else:
            raise Exception("Timeout waiting for LAM")
            return rcvd[2]

if __name__ == '__main__':
    # for send/receive 
    host = "192.168.0.2"
    port = 240
    buf = 1024
    addr = (host,port)

    # socket for sending to CAMAC
    sendSock = socket(AF_INET, SOCK_DGRAM)
    # this is the signal timeout, ie how long to keep sending
    # without receiving 
    sendSock.settimeout(10)
    
    cccc(sock, addr)
    cccz(sock, addr)
    ccci(sock, addr)