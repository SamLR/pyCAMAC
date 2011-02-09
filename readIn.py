
#!/usr/bin/env python
# encoding: utf-8
"""
readIn.py

Created by Sam Cook on 2011-02-01.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import camac_control
import socket

n_subaddresses = 4
module_location = 8
adc = {"n":21, "addr":(0,1,2,3)}
int_reg = {"n":22, "addr":(0)}
out_reg = {"n":23, "subaddr":(1G)}

# TODO undo wrapitis that is endemic throughout this
# restructure in a more sensible way (see notes)

def camac_reader(file, maxEvents = 5000):
    # set up CAMAC here
    #      create socket X
    #      CAMAC_init() X
    #      file for writing -> use something that implements 'write'
    #           overload so that an object can be passed that will display + write
    print("initialising the CAMAC crate")
    sock = sock_init()
    
    print ("here I am")
    camac_init(sock)
    # while loop
    #       waitLAM -> change to look for interupt reg?
    #       read ADC
    #       send trig reset to output reg
    #       eventcount++
    #       exit/cont
    n_error = 0
    reset_trigger(sock, **out_reg)
    for i in range(maxEvents):
        try:
            camac_control.waitForLAM(sock, **int_reg)      
        except socket.timeout:
            print("LAM timeout")
            n_error += 1
        data = read_mod(sock, **adc)
        reset_trigger(sock, **out_reg)
        file.write(str(data))


def camac_init(sock):
    # rsync -> cccc -> cccz -> ccci
     camac_control.rsync(sock)
     camac_control.cccc(sock)
     camac_control.cccz(sock)
     camac_control.ccci(sock)
     print "CAMAC init complete"

def read_mod(sock, n, addr, grp1=True):
    """
    reads the CAMAC module at position, n,
    subaddresses 0 to (sub_addr_max - 1)
    assumes reading grp1, if false reads grp2
    """
    res = []
    func = "readGrp1" if grp1 else "readGrp2"
    for a in addr:
        # TODO figure out which bit of the return status is the data
        # cssa returns [u16 nwords, u16 data, u16 status or qresp], want the data bit
        res.append(camac_control.cssa(sock, n, func, a)["data"])
    return res

def reset_trigger(sock, n, subaddr, grp1=True, addr=0):
    """
    Sets the register, in slot n, at addr to 
    value, subaddr, then sets it to 0. Unless grp1 is unset
    this assumes that addr exists in group1
    """
    # TODO add 'CAMACError'
    func = "overWriteGrp1" if grp1 else "overWriteGrp2"
    status = camac_control.cssa(sock, n, func, a=addr, data=subaddr)["status"]
    if status != 1: raise Exception ("no qresp")
    # now clear the address
    status = camac_control.cssa(sock, n, func, a=addr, data=0)["status"]
    if status != 1: raise Exception("no qresp")
    
def sock_init(host = '192.168.0.2', sendPort = 240, recvPort = 59329):
    """
    Initialises the socket for communication to the crate
    """
    sendAddr = (host, sendPort)
    recvAddr = ('', recvPort)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(recvAddr)
    sock.connect(sendAddr)
    return sock

if __name__ == '__main__':
    f = open('test.txt', 'w')
    camac_reader(f, maxEvents=5)

