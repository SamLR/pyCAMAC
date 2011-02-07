
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

def camac_reader(file, maxEvents = 5000):
    # set up CAMAC here
    #      create socket X
    #      CAMAC_init() X
    #      file for writing -> use something that implements 'write'
    #           overload so that an object can be passed that will display + write
    print("initialising the CAMAC crate")
    sock = sock_init()
    camac_init(sock)
    # while loop
    #      waitLAM
    #      read ADC
    #      eventcount++
    #      exit/cont
    n_error = 0
    for i in range(maxEvents):
        try:
            camac_control.waitForLAM(sock)      
        except Exception, e:
            print("LAM timeout")
            n_error += 1
        data = read_mod(sock, module_location, n_subaddresses)
        file.write(data)

def camac_init(sock):
    # rsync -> cccc -> cccz -> ccci
    camac_control.rsync(sock)
    camac_control.cccc(sock)
    camac_control.cccz(sock)
    camac_control.ccci(sock)

def read_mod(sock, n, sub_addr_max, grp1=True):
    """reads the CAMAC module at position, n,
    subaddresses 0 to (sub_addr_max - 1)
    assumes reading grp1, if false reads grp2"""
    res = []
    func = "readGrp1" if grp1 else "readGrp2"
    for addr in range(sub_addr_max):
        # TODO figure out which bit of the return status is the data
        # cssa returns [u16 nwords, u16 data, u16 status or qresp], want the data bit
        res.append(camac_control.cssa(pos, func, addr)[1])
    return res

def sock_init(host = '192.168.0.2', sendPort = 240, recvPort = 59329):
    """Initialises the socket for communication to the crate"""
    sendAddr = (host, sendPort)
    recvAddr = ('', recvPort)
    sock = socket.socket(socket.AF  _INET, socket.SOCK_DGRAM)
    sock.connect(sendAddr)
    sock.bind(recvAddr)
    return sock

if __name__ == '__main__':
    f = open 
    main(f)

