
#!/usr/bin/env python
# encoding: utf-8
"""
readIn.py

Created by Sam Cook on 2011-02-01.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os

from socket import *
from camac_control import *
from fileUpdater import *

n_subaddresses = 4
module_location = 8
adc = {"n":21, "addr":(0,1,2,3)}
int_reg = {"n":22, "addr":(0)}
out_reg = {"n":23, "subaddr":(1)}

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
    camac_init(sock)
    # while loop
    #       waitLAM -> change to look for interupt reg?
    #       read ADC
    #       send trig reset to output reg
    #       eventcount++
    #       exit/cont
    n_error = 0
    reset_trigger(sock, **out_reg)
    print("trigger reset")
    for i in range(maxEvents):
        try:
            waitForLAM(sock, **adc)
            # this won't run if wait times out
            data = read_mod(sock, **adc)
        except timeout:
            n_error += 1
            continue
        except CAMACError, e:
            n_error += 1
            print e
            # TODO logging?
        finally:
            # make sure that the veto hasn't jammed
            reset_trigger(sock, **out_reg)
            clear_mod(sock, **adc)

        file.write(str(data))
        
    print "done with %i errors" % n_error


def camac_init(sock):
    # rsync -> cccc -> cccz -> ccci
     rsync(sock)
     cccc(sock)
     cccz(sock)
     ccci(sock)
     print "CAMAC init complete"

def read_mod(sock, n, addr, grp1=True, str_fmt="%4i  "):
    """
    reads the CAMAC module at position, n,
    subaddresses 0 to (sub_addr_max - 1)
    assumes reading grp1, if false reads grp2
    """
    res = ''
    func = "readGrp1" if grp1 else "readGrp2"
    for a in addr:
        res += str_fmt % (cssa(sock, n, func, a)["data"][1])
    return res

def waitForLAM(sock, n, addr, maxpolls=100, subaddr=None):
    """
    polls the module for LAM, returns if there is a LAM
    otherwise throws a timeout error"""
    n_timeouts = 0
    for i in range(maxpolls):
        status = cssa(sock, n, f="testLAM")
        try:
            status_check(status)
        except CAMACError:  
            n_timeouts += 1
            continue
        return
    else:
        raise timeout("timed out waiting for LAM n_timeouts: %i" % n_timeouts)

def clear_mod(sock, n, addr, grp1=True):
    """
    clears LAM and any data saved in the module"""
    func = "clearGrp1" if grp1 else "clearGrp2"
    # while clear group clears all addrs it still needs one...
    status = cssa(sock, n=n, a=addr[0], f=func) 
    # status_check(status)
    status =  cssa(sock, n=n, a=addr[0], f="clearLAM") 
    # status_check(status)

def reset_trigger(sock, n, subaddr, grp1=True, addr=0):
    """
    Sets the register, in slot n, at addr to 
    value, subaddr, then sets it to 0. Unless grp1 is unset
    this assumes that addr exists in group1
    """
    func = "overWriteGrp1" if grp1 else "overWriteGrp2"
    status = cssa(sock, n, func, a=addr, data=subaddr)
    status_check(status)
    # now clear the address
    status = cssa(sock, n, func, a=addr, data=0)
    status_check(status)
    
def sock_init(host = '192.168.0.2', sendPort = 240, recvPort = 59329):
    """
    Initialises the socket for communication to the crate
    """
    sendAddr = (host, sendPort)
    recvAddr = ('', recvPort)
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(recvAddr)
    sock.connect(sendAddr)
    return sock


if __name__ == '__main__':
    print "setting up file"
    f = FileUpdater('test.txt', 'w', update_on=50)
    print "starting run"
    camac_reader(f, maxEvents=200)
    while True:
        pass
