# encoding: utf-8
"""
camac_cmds.py

Created by Sam Cook on 2011-01-24.
Copyright (c) 2011. All rights reserved.
"""

import ecp_header 
from naf import *

from socket import *
from struct import unpack, calcsize
from time import sleep

recvPackStr = ecp_header.headerPackStr + 'H'*3
lens = {''}

def status(sock, verbose=False, packStr=recvPackStr): 
    """returns the status as received from the socket, sock. 
    options: verbose - returns full packet
             packStr - alternate packing string (eg if header)
    """
    # TODO tidy this up, get packstrs for all 
    # returns
    data = ''
    while not data:
        data = sock.recv(4096) #1228
    s = []
    if not packStr:
        while len(data) > 0:
            s += unpack('B',data[:1])
            data = data[1:]
        res = s
    else:    
        for char in recvPackStr:
            # this is a hack because unpack seems to have issues with mixed 
            # format strings containing 'I', gods alone know why...
            size = calcsize(char)
            current, data = data[:size], data[size:]
            s.append(unpack(char, current)[0])
    
        fields = ecp_header.header_fields + ecp_header.rcvd_fields
        res = dict(zip(fields, s))
    # ack's are sequential 
    ecp_header.set_llccontrol(s[2])
    return res

def cccc(sock, verbose=False):
    """
    send CAMAC clear to socket, sock
    """
    msg = ecp_header.gettop(cmd = 'cmd_clear', mod = 0)
    sock.send(msg)
    return status(sock, verbose, packStr = None)

def cccz(sock, verbose=False):
    """
    send CAMAC init to socket, sock
    """
    msg = ecp_header.gettop(cmd = 'cmd_init', mod = 0)
    sock.send(msg)
    return status(sock, verbose, packStr = None)

def ccci(sock, verbose=False):
    """
    send CAMAC inhibit to socket, sock
    """
    msg = ecp_header.gettop(cmd = 'cmd_inhibit', mod=0)
    sock.send(msg)
    return status(sock, verbose, packStr = None)

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
    return status(sock, verbose, packStr = None)

# TODO check that rcvd[2] _is_ the status and is != 0 for good returns
def waitForLAM(sock, n, maxpolls = 100):
    """
    Polls the LAM at n then sleeps for 10us
    """
    msg = ecp_header.gettop(cmd='cmd_test_lam', mod=int(n))
    for i in range(maxpolls):
        rsync(sock)
        rcvd = sock.send(msg)
        if not (rcvd [-1]):
            sleep(0.01)
        else:
            print(rcvd)
            return rcvd[-1]
    else:
        raise Exception("Timeout waiting for LAM")
# 
# def waitForInt(sock, maxpolls = 100, ):
#     """docstring for waitForInt"""
#     pass

def rsync(sock, maxTries = 10):
    """resyncs the ecc + pc"""
    LLC_responce = 0x64 # from 'our_ecc.h'
    LLC_command = 0x60
    rsync_cmd_1 = b'\x60\x60\x67'
    rsync_cmd_2 = b'\x64\x64\xE7'
    attempts = 0
    cmd_2_sent = False
    llccontrol = 0xF7 # more magic!
    
    sock.send(rsync_cmd_1)
    while True:
        # s = status(sock, verbose=True)[1]# this should be destination LSAP
        s = sock.recv(4098)
        s = unpack("BBB",s[:3])[0]
        if s == LLC_responce:
            sock.send(rsync_cmd_2)
            cmd_2_sent = True
        elif (s == LLC_command and cmd_2_sent):
            ecp_header.set_llccontrol(llccontrol) 
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
    # filter for wire shark: 
    #(ip.src == 192.186.0.1 and ip.dst == 192.168.0.2) or (ip.src == 192.168.0.2 and ip.dst == 192.186.0.1)
    
    # this bit might work but it's hard to tell
    print("starting, sending clear, init and inhibit,")
    rsync(sendSock)
    print("completed rsync")
    for i in cccc(sendSock, verbose=True): print hex(i),
    print("\ncompleted c")
    for i in cccz(sendSock, verbose=True): print hex(i),
    print("\ncompleted z")
    for i in ccci(sendSock, verbose=True): print hex(i),
    print("\ncompleted i")

    ret = cssa(sock = sendSock, n = 23, f = "overWriteGrp1", a = 0, data = 0)
    for i in ret: print hex(i), 

    cssa(sock = sendSock, n = 23, f = "overWriteGrp1", a = 0, data=1)
    # print("look for LAM")
    # waitForLAM(sendSock, maxpolls=1000)
    # for i in range (5): 
    #        print(cssa(sock = sendSock, n = 23, f = "overWriteGrp1", a = 1, data=1))
    #        print(cssa(sock = sendSock, n = 23, f = "overWriteGrp1", a = 1, data=0))
    #        sleep(0.1)

    sendSock.close()
