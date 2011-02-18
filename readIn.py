
#!/usr/bin/env python
# encoding: utf-8
"""
readIn.py

Created by Sam Cook on 2011-02-01.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os

from camac_control import *
from time import sleep
from socket import *
from fileUpdater import *   
from time import localtime, strftime

verbose = False

adc     = {"n":21, "a":(8, 9, 10, 11)}
# clk     = {"n":20, "a":(0,)}
scalor  = {"n":20, "a":(1,)}
int_reg = {"n":22, "a":(0,)}
out_reg = {"n":23, "a":(0,), "subaddr":(1,)}
set_reg = {"n":23, "a":(0,), "subaddr":(2,)}

gate_width = 1

def camac_reader(out_file, maxEvents = 5000):
    percent = int(round(maxEvents*0.1))
    sock = sock_init()
    
    n_error = 0
    n_timeouts = 0
    try:
        camac_init(sock)
        if verbose: print("CAMAC initialised")
        
        camac(sock, f="enable", **int_reg) #enable the LAM
        if verbose: print("int reg LAM enabled")
        
        reset_trigger(sock, **out_reg)
        if verbose: print("trigger reset")
        
        print 'starting run'
        for i in range(maxEvents):
            if i%percent == 0: print i
            try:
                if verbose: print 'waiting for LAM'
                waitForLAM(sock, maxpolls=5000, **int_reg)
                if verbose: print 'LAM found'
                
                camac(sock, f="disable", **int_reg)
                if verbose: print 'disabled int reg'
                
                data = read_mod(sock, **adc)
                if verbose: print 'ADC read'
                
                out_file.write(str(data))
                if verbose: print 'written file'
                
            except timeout: # caused by LAM
                if verbose: print '>>>> timeout error'
                n_timeouts += 1
                continue
                
            except CAMACError, e: # status & qresp errors
                n_error += 1
                print e
                # reset everything  
                
                try:
                    sleep(0.001) # allow the crate to stabise then restart it
                    clear_mod(sock, **adc) 
                    clear_mod(sock, **int_reg)
                    reset_trigger(sock, **out_reg)
                    if verbose: print 'adc and int reg cleared, trigger reset'
                except CAMACError, e:
                    camac_init(sock)
                    print "Crate re-initialised"
                    n_error += 1
                    print e
                
            finally:
                # make sure that the veto hasn't jammed
                reset_trigger(sock, **out_reg)
                if verbose: print 'Reset trigger'
                
                camac(sock, f="enable", **int_reg)
                if verbose: print 'Enabled LAM'
                
        print "Finished with %i errors and %i timeouts" % (n_error, n_timeouts)
    finally:
        print "errors:", n_error, "timeouts:", n_timeouts
        sock.close()

def pedestal(out_file, maxEvents = 5000):
    percent = int(round(maxEvents*0.1))
    print("initialising the CAMAC crate")
    sock = sock_init()
    try:
        camac_init(sock)
        n_error = 0
        n_timeouts = 0
        camac(sock, f="enable", **int_reg) #enable the LAM
        reset_trigger(sock, **out_reg)
        print("trigger reset")
        for i in range(maxEvents):
            if i%percent == 0: print i
            try:
                set_out_reg(sock, **set_reg)
                waitForLAM(sock, **int_reg)
                data = read_mod(sock, **adc)
                out_file.write(str(data))
            except timeout:
                n_timeouts += 1
                print "LAM timeout"
                continue
            except CAMACError, e:
                n_error += 1
                print e.message
            finally:
                # make sure that the veto hasn't jammed
                reset_trigger(sock, **out_reg)
        print "done with %i errors & %i timeouts" % (n_error, n_timeouts)
    finally:
        sock.close()
        print "REMEMBER: change back ADC gate line and gg set line"

def hit_rate(out_file, maxTries = 60):
        print("initialising the CAMAC crate")
        sock = sock_init()
        try:
            camac_init(sock)
            n_error = 0
            n_timeout = 0
            sum = 0
            camac(sock, f="enable", **int_reg) #enable the LAM
            reset_trigger(sock, **out_reg)
            print("trigger reset")
            for i in range(maxTries):
                try:
                    clear_mod(sock, **scalor)
                    set_out_reg(sock, **set_reg)
                    sleep(1)
                    # waitForLAM(sock, maxpolls=1000, **scalor)
                    data = read_mod(sock, **scalor)
                    sum += int(data)
                    # print "rate = %iHz" % (data)
                    out_file.write(str(data))
                except timeout:
                    n_timeout += 1
                    print "LAM timeout"
                    continue
                except CAMACError, e:
                    n_error += 1
                    print e.message
                finally:
                    # make sure that the veto hasn't jammed
                    reset_trigger(sock, **out_reg)
            print "average rate: %.3fHz" % (sum/maxTries)
            print "done with %i errors %i timeouts" % (n_error, n_timeout)
        finally:
            sock.close()
            print "REMEMBER: change back ADC gate line and gg set line"

def camac(sock, n, f, a=0, subaddr=None, data=None, single=False):
    """
    Sends a camac command
    if single is true the function is sent to addr 0 only
    either data _or_ subaddr will be used, if both given
    subaddr will be ignored
    it is assumed that a, subaddr, and data will be indexable
    even in single mode
    """
    data = data if (data != None) else (subaddr if (subaddr != None) else (None, ))
    if (single): 
        return cssa(sock, n=n, a=0, f=f, data=data[0])
    else:
        for i in range(len(a)):
            return cssa(sock, n=n, a=a[i], f=f, data=data[i])

def camac_init(sock):
    # rsync -> cccc -> cccz -> ccci
     rsync(sock)
     cccc(sock)
     cccz(sock)
     ccci(sock)

def read_mod(sock, n, a, grp1=True, str_fmt="%4i  "):
    """
    reads the CAMAC module at position, n,
    subaddresses 0 to (sub_addr_max - 1)
    assumes reading grp1, if false reads grp2
    """
    res = ''
    func = "readGrp1" if grp1 else "readGrp2"
    func2 = "clearGrp1" if grp1 else "clearGrp2"
    blanks = 0
    for addr in a:
        status = camac(sock, n, func, (addr,))
        if status["qresp"][1] != 0x8000:
            # try reading the module again
            status = camac(sock, n, func, (addr,))
            if status["qresp"][1] != 0x8000:
                raise CAMACError("problem reading %i" % status["qresp"][1])
        if (status["data"][1] == 1) or (status["data"][1] == 0): blanks += 1
        res += str( status["data"][1] ) + ' '
    camac(sock, n, func2, single=True)
    return res

def waitForLAM(sock, n, a, maxpolls=1000, subaddr=None):
    """
    polls the module for LAM, returns if there is a LAM
    otherwise throws a timeout error"""
    status = camac(sock, n, f="clearLAM", single=True)
    status_check(status, 'wait for Lam clearLAM')
    for i in range(maxpolls):
        status = camac(sock, n, f="testLAM", a=a)
        try:
            status_check(status, 'wait for LAM: testLAM')
        except CAMACError: 
            sleep(0.001) # sleep for 1us
            continue
        camac(sock, n, f="clearGrp1", single=True)
        return
    else:
        raise timeout("timed out waiting for LAM")

def clear_mod(sock, n, a, grp1=True):
    """
    clears LAM and any data saved in the module"""
    func = "clearGrp1" if grp1 else "clearGrp2"
    # while clear group clears all addrs it still needs one...
    status = camac(sock, n=n, a=(0,), f=func) 
    # status_check(status, 'clear mod: clear grp')
    status =  camac(sock, n=n, a=(0,), f="clearLAM") 
    # status_check(status, 'clear mod: clear LAM')

def reset_trigger(sock, n, subaddr, grp1=True, a=0):
    """
    Sets the register, in slot n, at addr to 
    value, subaddr, then sets it to 0. Unless grp1 is unset
    this assumes that addr exists in group1
    """
    func = "overWriteGrp1" if grp1 else "overWriteGrp2"
    status = camac(sock, n=n, f=func, a=a, data=subaddr)
    status_check(status, 'trigger reset: write 1')
    # now clear the address
    status = camac(sock, n=n, f=func, a=a, data=(0,))
    status_check(status, 'trigger reset: write 2')
    
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


def set_out_reg(sock, n, subaddr, grp1=True, a=0):
    func = "overWriteGrp1" if grp1 else "overWriteGrp2"
    status = camac(sock, n=n, a=a, f=func, data=subaddr)
    status_check(status, 'set out reg, write 1')
    status = camac(sock, n=n, a=a, f=func, data=(0,))
    status_check(status, 'set out reg, write 2')

def stall(record=False):
    """
    Waits for user input to continue. Will exit the program on 'Q'
    if record is set this will return any integer entered by the user
    if a non-digit character is entered it will return None"""
    run = True
    while run:
        d = raw_input()
        if (d == 'Q') or (d == 'q'):
            exit() 
        elif d and record:
            for i in d:
                if not i.isdigit(): return None
            return int(d)
        elif d:
            return
        else:
            continue

if __name__ == '__main__':
    n_files = 1
    timefmt = "%d-%m-%y %H:%M:%S"
    maxEvents = 100000
    for i in range (n_files):
        print '='*40
        print "Please connect the GREY veto line then press any key and 'enter'"
        print "Please measure the beam intensity"
        print '='*40
        stall()
        
        th1_hit = ('hist', 100, 2.0, 4000)
        hit_file = 'data/hit_rates_%03i.txt' 
        head = strftime(timefmt, localtime())
        f_hit = FileUpdater(hit_file, n_dat=1, header = head, TH1args=th1_hit,  update_on=1)
        try:
            hit_rate(f_hit, maxTries=40)
        finally:
            foot = strftime(timefmt, localtime())
            f_hit.closeFooter(foot)
        
        print '='*40
        print "Please connect the GREEN veto line then press any key and 'enter'"
        print 'max entries set to %i is this correct?' % maxEvents
        print 'if not please enter how many events to take' 
        print "press 'Q' to quit"
        print '\n\n\n', '='*40
        d = stall(True)
        maxEvents = d if d else maxEvents

        th1_dat = ('hist', 100, 2.0, 2**12)
        data_file = 'data/test_%03i.txt' #pedestal_%03i.txt'
        head = strftime(timefmt, localtime())
        f_adc = FileUpdater(data_file, n_dat=4, header = head, TH1args=th1_dat, update_on=200)
        try:
            camac_reader(f_adc, maxEvents=500)
            # pedestal(f_adc, maxEvents=1000)
        finally:
            foot = strftime(timefmt, localtime())
            f_adc.closeFooter(foot)

        print '='*40
        print "Please connect the GREY veto line then press any key and 'enter'"
        print "Please measure the beam intensity"
        print '='*40
        stall()

        hit_file = 'data/hit_rates_%03i.txt' 
        head = strftime(timefmt, localtime())
        f_hit2 = FileUpdater(hit_file, n_dat=1, header = head, TH1args=th1_hit,  update_on=1)
        try:
            hit_rate(f_hit2, maxTries=20)
        finally:
            foot = strftime(timefmt, localtime())
            f_hit2.closeFooter(foot)


            # End of for loop