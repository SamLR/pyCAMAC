# encoding: utf-8
"""
camac_cmds.py

Created by Sam Cook on 2011-01-24.
Copyright (c) 2011. All rights reserved.
"""

import ecp_header 
from naf import *

from socket import *
from struct import unpack
from time import sleepÌ

recvPackStr = ecp_header.headerPackStr + 'B'*3
ecpFramePackStr = ecp_header.headerPackStr + 'B'*1200

def status(sock, verbose=False, packStr=None): 
    """returns the status as received from the socket, sock. 
    options: verbose - returns full packed
             packStr - alternate packing string (eg if header)
    """
    data = ''
    while not data:
        data = sock.recv(4096) #1228
    
    s = (None,)
    if not packStr:
        while len(data) > 0:
            s += unpack('B',data[:1])
            data = data[1:]
    else:    
        s = unpack(packStr, data)
    res = s if verbose else (s[-3], s[-2], s[-1])
    return res

def cccc(sock, verbose=False):
    """
    send CAMAC clear to socket, sock
    """
    msg = ecp_header.gettop(cmd = 'cmd_clear')
    # sock.sendto(msg,addr)
    sock.send(msg)
    return status(sock, verbose)

def cccz(sock, verbose=False):
    """
    send CAMAC init to socket, sock
    """
    msg = ecp_header.gettop(cmd = 'cmd_init')
    # sock.sendto(msg,addr)
    sock.send(msg)
    return status(sock, verbose)

def ccci(sock, verbose=False):
    """
    send CAMAC inhibit to socket, sock
    """
    msg = ecp_header.gettop(cmd = 'cmd_inhibit')
    # sock.sendto(msg,addr)
    sock.send(msg)
    return status(sock, verbose)

def cssa(sock, n, f, a = - 1, data = -1, verbose = False):
    """
    wait until a LAM signal is received
    sends to socket sock
    n = slot no,
    f = camac function, 
    a is optional based on function and the subaddress of the module 
    d is optional based on function and the data to be passed
    returns the received packet as a list: n_words, dat and status
    """
    msg = ecp_header.gettop() + naf(n, f, a, data)
    sock.send(msg)
    data = ''
    return status(sock, verbose)

# TODO check that rcvd[2] _is_ the status and is != 0 for good returns
def waitForLAM(sock, maxpolls = 100):
    """
    Polls the LAM then sleeps for 10us
    """
    for i in range(maxpolls):
        rsync(sock)
        rcvd = cssa(sock, 24, 'testLAM')
        if not (rcvd [-1]):
            sleep(0.01)
        else:
            print(rcvd)
            return rcvd[-1]
    else:
        raise Exception("Timeout waiting for LAM")

def rsync(sock, maxTries = 10):
    """resyncs the ecc + pc"""
    LLC_responce = 0x64 # from 'our_ecc.h'
    LLC_command = 0x60
    rsync_cmd_1 = b"\x60\x60\x67"
    rsync_cmd_2 = b'\x64\x64\xE7'
    attempts = 0
    cmd_2_sent = False
    
    sock.send(rsync_cmd_1)
    while True:
        s = status(sock, verbose=True)[1]# this should be destination LSAP
        if s == LLC_responce:
            sock.send(rsync_cmd_2)
            cmd_2_sent = True
        elif (s == LLC_command and cmd_2_sent):
            return 1
        elif attempts == maxTries:
            print("rsync failure, too many attempts")
            return 0
        else:
            attempts += 0


if __name__ == '__main__':
    # socket for sending to CAMAC: network using UDP
    sendSock = socket(AF_INET, SOCK_DGRAM)
    # this is the signal timeout, ie how long to keep sending
    # without receiving 
    sendSock.settimeout(10)
    
    # addresses for send/receive 
    sendAddr = ('192.168.0.2', 240) # (host, port) both defined in our_ecc
    rcvAddr = ('', 59329)
    
    sendSock.bind(rcvAddr) # where to receive data
    sendSock.connect(sendAddr) # where to send from
    
    # this bit might work but it's hard to tell
    print("starting, sending clear, init and inhibit,")
    rsync(sendSock)
    #print(cccc(sendSock, verbose=True))
    #print(cccz(sendSock, verbose=True))
    #print(ccci(sendSock, verbose=True))

    print("look for LAM")
    waitForLAM(sendSock, maxpolls=1000) 
    print(cssa(sock = sendSock, n = 9, f = "readGrp1", a = 0))

    sendSock.close()
