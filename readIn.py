
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
adc = {"n":21, "a":(0,1,2,3)}
int_reg = {"n":22, "a":(0)}
out_reg = {"n":23, "subaddr":(1)}

def camac_reader(out_file, maxEvents = 5000):
   
    print("initialising the CAMAC crate")
    sock = sock_init()
    try:
        camac_init(sock)
        n_error = 0
        cssa(sock, f="enable", **int_reg) #enable the LAM
        reset_trigger(sock, **out_reg)
        print("trigger reset")
        for i in range(maxEvents):
            try:
                waitForLAM(sock, **int_reg)
                # this won't run if wait times out
                data = read_mod(sock, **adc)
            except timeout:
                n_error += 1
                print "LAM timeout"
                continue
            except CAMACError, e:
                n_error += 1
                print e
                # TODO logging?
            finally:
                # make sure that the veto hasn't jammed
                reset_trigger(sock, **out_reg)
                # clear_mod(sock, **adc)
                
            out_file.write(str(data))
        
        print "done with %i errors" % n_error
    finally:
        out_file.close()
        sock.close()

def camac_init(sock):
    # rsync -> cccc -> cccz -> ccci
     rsync(sock)
     cccc(sock)
     cccz(sock)
     ccci(sock)
     print "CAMAC init complete"

def read_mod(sock, n, a, grp1=True, str_fmt="%4i  "):
    """
    reads the CAMAC module at position, n,
    subaddresses 0 to (sub_addr_max - 1)
    assumes reading grp1, if false reads grp2
    """
    res = ''
    func = "readGrp1" if grp1 else "readGrp2"
    func2 = "clearGrp1" if grp1 else "clearGrp2"
    for a in a:
        res += str_fmt % (cssa(sock, n, func, a)["data"][1])
    cssa(sock, n, func2, a)
    return res + '\n'

def waitForLAM(sock, n, a, maxpolls=1000, subaddr=None):
    """
    polls the module for LAM, returns if there is a LAM
    otherwise throws a timeout error"""
    cssa(sock, n, f="clearLAM", a=a)
    for i in range(maxpolls):
        status = cssa(sock, n, f="testLAM", a=a)
        try:
            status_check(status)
        except CAMACError: 
            sleep(0.001) # sleep for 1us
            continue
        return
    else:
        raise timeout("timed out waiting for LAM")

def clear_mod(sock, n, a, grp1=True):
    """
    clears LAM and any data saved in the module"""
    func = "clearGrp1" if grp1 else "clearGrp2"
    # while clear group clears all addrs it still needs one...
    status = cssa(sock, n=n, a=a[0], f=func) 
    # status_check(status)
    status =  cssa(sock, n=n, a=a[0], f="clearLAM") 
    # status_check(status)

def reset_trigger(sock, n, subaddr, grp1=True, a=0):
    """
    Sets the register, in slot n, at addr to 
    value, subaddr, then sets it to 0. Unless grp1 is unset
    this assumes that addr exists in group1
    """
    func = "overWriteGrp1" if grp1 else "overWriteGrp2"
    status = cssa(sock, n, func, a=a, data=subaddr)
    status_check(status)
    # now clear the address
    status = cssa(sock, n, func, a=a, data=0)
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
    n_files = 5
    try:
        for i in range (n_files):
            print "setting up file"
                # values for creating the histogram (ROOT style, title dealt w/ by fileupdater)
            th1 = ('hist', 100, 0.0, 100.0)
            # f = FileUpdater('../data/test%i.txt', 'w', 50, header='music_data' th1)
            f = FileUpdater('data/test_%03i.txt', mode="w", n_dat=4, header = '', TH1args=th1, update_on=100)
            print "starting run"
            camac_reader(f, maxEvents=20000)
    finally:
        f.close()
        