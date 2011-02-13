# encoding: utf-8
"""
camac_cmds.py

Created by Sam Cook on 2011-01-24.
Copyright (c) 2011. All rights reserved.
"""

from ecp_header import * # this imports packet_desc

from socket import *
from select import *
from struct import *
from time import sleep


# recvPackStr = ecp_header.headerPackStr + 'H'*3
# lens = {''}

class CAMACError(Exception):
    # TODO look at adding status code ref'd error msgs?
    pass
        

def status(sock): 
    """
    returns the status as received from the socket, sock. 
    options: verbose - returns full packet
             packStr - alternate packing string (eg if header)
    """
    
    data = ''
    while not data:
        data = sock.recv(4096) 
        
    if len(data) == 24:
        # header only
        res = dictify(ecp_header, data)
        llcControl = res["llcControl"][1]
    elif len(data) == 30:
        # rcvd packed (header + nwords, data, qresp)
        res = dictify(ecp_rcvd_packet, data)
        llcControl = res["llcControl"][1]
    else:
        # most likley error but unpack it anyway
        res = ()
        while len(data) > 0:
            byte, data = data[:1], data[1:]
            res += unpack('B', byte)
            llcControl = res[2]
        
    ecp_header["llcControl"][1] = llcControl
    
    return res

def status_check(data):
    """
    Checks the status and qresp for the passed packed"""
    if data["status"][1] != 1:
        raise CAMACError("Status failure code: %i" % data["status"][1])
    elif data["qresp"][1]  != 0x8000:
        # TODO - check if this term also includes xresp
        raise CAMACError("Qresp failure %i" % data["qresp"][1])

def cccc(sock):
    """
    send CAMAC clear to socket, sock
    """
    msg = gettop(cmd = 'cmd_clear', mod = 0)
    sock.send(msg)
    return status(sock)

def cccz(sock):
    """
    send CAMAC init to socket, sock
    """
    msg = gettop(cmd = 'cmd_init', mod = 0)
    sock.send(msg)
    return status(sock)

def ccci(sock):
    """
    send CAMAC inhibit to socket, sock
    """
    msg = gettop(cmd = 'cmd_inhibit', mod=0)
    sock.send(msg)
    return status(sock)

def cssa(sock, n, f, a = None, data = None): # waitForLAM = False, timeout = 30):
    """
    n = slot no,
    f = camac function, 
    a is optional based on function and the subaddress of the module 
    d is optional based on function and the data to be passed
    waitForLAM sends the command with the COR command "attach to LAM"
    which will not be processed until a LAM has been seen on the module
    returns the received packet as a list: n_words, dat and status
    """
    # commands attached to lam _must_ be deferred
    # if waitForLAM:
    #        toparg = {"cmd":"cmd_attach_lam", "mod":n, "deferred":True} 
    #    else:
    toparg = {"cmd":'cmd_camac_op', "mod":1}
    msg = gettop(**toparg) + naf(n, f, a, data)
    sock.send(msg)
    data = status(sock)
    # if waitForLAM:
    #      if data["status"][1] != 1: raise CAMACError("Status error %i" % data["status"][1])
    #      # dark voodoo using select()
    #      inputs = [sock, ]
    #      running = True
    #      while running:
    #          inputready, outputready, erready = select(inputs, [], [], timeout)
    #          for s in inputready:
    #              data = status(s)
    #              print "in cssa", data
    #              llc = data["llcControl"][1] ^ 0x80
    #              msg = gettop(deferred=True, llcControl=llc, status=1)
    #              sock.send(msg) # send an ack
    return data
    
def stackem(sock, n_lam, n, f, a=None, data=None):
    count = len(f)
    msg = gettop("cmd_attach_lam", n_lam, count)
    for op in range(count):
        msg += naf(n[i], f[i], a[i], data[i])
    sock.sock(msg)
    print status(sock)
    return

def sendCOR(sock, cmd, mod):
    # TODO use this to simplify cccc etc
    msg = gettop(cmd = cmd, mod=mod)
    sock.send(msg)
    return status(sock)

# def waitForLAM(sock, n, addr=None, maxpolls = 100):
#     """
#     Polls the LAM at n then sleeps for 10us
#     """
#     # this actually looks for activity in the register
#     # TODO try with LAM again..
#     msg = gettop(cmd = 'cmd_clear_lam', mod = 22)
#     sock.send (msg)
#     data = status(sock)
#     for i in range(maxpolls):
#         msg = gettop(cmd = 'cmd_test_lam', mod = 22)
#         sock.send (msg)
#         
#         data = status(sock)
#         if data["status"][1] != 1:
#             raise CAMACError("status: %i" % data["status"][1])
#         if "qresp" in data:
#             return data["qresp"]
#     else:
#         raise timeout("Timeout waiting for interupt")


def waitForLAM(sock, n, addr=None, maxpolls = 100):
    """
    Polls the LAM at n then sleeps for 10us
    """
    # this actually looks for activity in the register
    # TODO try with LAM again..
    msg = gettop() + naf(n, f="clearLAM", a = 1)
    sock.send (msg)
    data = status(sock)
    old_data = data#{"status":9, "qresp":0}
    for i in range(maxpolls):
        msg = gettop() + naf(n=n, f="testLAM")#cmd = 'cmd_test_lam', mod = n)
        sock.send (msg)
        
        data = status(sock)
        # status_check(data)
        if data["status"] != old_data["status"]:
            print data
        if ("qresp" in data) and (data["qresp"] != old_data["qresp"]):
            print data
        old_data = data
        # if data["data"][1] != 0:
        #             print data["data"][1]
        #             return 
        #         continue
        # if data["status"][1] != 1:
        #     raise CAMACError("status: %i" % data["status"][1])
        # if "qresp" in data:
        #     
        #     return data["qresp"]
        
    else:
        raise timeout("Timeout waiting for interupt")

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
        s = sock.recv(4098)
        s = unpack("BBB",s[:3])[0]
        if s == LLC_responce:
            sock.send(rsync_cmd_2)
            cmd_2_sent = True
        elif (s == LLC_command and cmd_2_sent):
            ecp_header["llcControl"][1] = llccontrol
            return
        elif attempts == maxTries:
            raise timeout("timed running rsynch")
        else:
            attempts += 0

# dictionary format "command name":(command code, [subaddress needed?], [data needed?])
camacFunction = { 
    "readGrp1":          (0,  "subaddr"),
    "readGrp2":          (1,  "subaddr"),
    "readClrGrp1":       (2,  "subaddr"),
    "readClrGrp2":       (3,  "subaddr"),
    "testLAM":           (8,  ),
    "clearGrp1":         (9,  "subaddr"),
    "clearLAM":          (10, ),
    "clearGrp2":         (11, "subaddr"),
    "overWriteGrp1":     (16, "subaddr", "data"),
    "overWriteGrp2":     (17, "subaddr", "data"),
    "maskOverWriteGrp1": (18, "subaddr", "data"), 
    "maskOverWriteGrp2": (19, "subaddr", "data"),
    "disable":           (24, ),
    "increment":         (25, "subaddr"),
    "enable":            (26, ),
    "testStatus":        (27, ),
    }

def naf(n, f, a = None, data = None ):
    # data to write
    """
    Converts n, a, f to a 2byte string that is suitable
    to be sent to CAMAC in the format: 0fff ffnn nnna aaas
    """
    # get the function info required (number and whether an address etc are needed) 
    funcCode = (f, ) if str(f).isdigit() else camacFunction[f] 
    if (("subaddr" in funcCode) and (a == None)):
        raise Exception("function requires a subaddress")
    elif (("data" in funcCode) and (data == None)):
        raise Exception("function requires a data")
        
    a = a if a else 0
    data = pack('H', data) if (data >= 0) else b''
    # print funcCode[0], n, a
    res = funcCode[0] <<10 | n <<5 | a << 1 | 0 
    res = pack('H', res)
    return res + data

def main_test():
    sock = socket(AF_INET, SOCK_DGRAM)
   
    sock.settimeout(5)
    
    sendAddr = ('192.168.0.2', 240) # (host, port) both defined in our_ecc
    rcvAddr = ('', 59329)
    
    sock.bind(rcvAddr) # where to receive data
    sock.connect(sendAddr) # where to send from
    
    
    # this bit might work but it's hard to tell
    print("starting, sending clear, init and inhibit,")
    rsync(sock)
    print("completed rsync")
    for i in cccc(sock): pass# print hex(i),
    print("\ncompleted c")
    for i in cccz(sock): pass #print hex(i),
    print("\ncompleted z")
    for i in ccci(sock): pass#print hex(i),
    print("\ncompleted i")
    
    cssa(sock, n = 21, f = "clearGrp1", a = 0)
    cssa(sock = sock, n = 23, f = "overWriteGrp1", a = 0, data=1) 
    cssa(sock = sock, n = 23, f = "overWriteGrp1", a = 0, data=0) 
    print "try and read"
    old_q = 32768 
    n_run = 0
    n_loops = 0
    while n_run < 5:
        q = cssa(sock, n = 21, f = "testLAM")["qresp"][1]
        if q == 0x8000: 
            
            # sleep(0.15) 
            for i in range(4):
                d = cssa(sock, n = 21, f = "readGrp1", a = i)
                print d["data"]

            n_run += 1
            cssa(sock, n = 21, f = "clearGrp1", a=8)
            cssa(sock, n = 21, f = "clearLAM")
            print "="*10
            cssa(sock = sock, n = 23, f = "overWriteGrp1", a = 0, data=1) 
            cssa(sock = sock, n = 23, f = "overWriteGrp1", a = 0, data=0)
        n_loops += 1
        if n_loops == 50:
            cssa(sock = sock, n = 23, f = "overWriteGrp1", a = 0, data=1) 
            cssa(sock = sock, n = 23, f = "overWriteGrp1", a = 0, data=0)
        

        # cssa(sock, n = 21, f = "readGrp1", a = 8,) # waitForLAM=True)
    
    # dat = 0
    # n_errors = 0
    # while dat == 0:
    #     try:
    #         dat = sock.recv(4098)
    #     except timeout:
    #         n_errors += 1
    #         sleep(1)
    #         if n_errors == 100:
    #             print n_errors
    #             sock.close()
    #             return
    # print dat
    # # clear the ADC
    # cssa(sock, n = 21, f = "clearGrp1", a = 0)
    # cssa(sock = sock, n = 23, f = "overWriteGrp1", a = 0, data=1) # hold the trigger reset
    # run = True
    # count = 0
    # print "out reg flashed"
    # cssa(sock = sock, n = 23, f = "overWriteGrp1", a = 0, data=0)
    # while run:
    #     count += 1
    #     adc_dat = []
    #     print("look for LAM")
    #     sendCOR(sock, cmd="cmd_clear_lam", mod=22)
    #     waitForLAM(sock, n=22, maxpolls=1000000)
    #     print("found")
    #     for i in range (8, 12):
    #         
    #         dat = cssa(sock, n = 21, f = "readGrp1", a = i, waitForLAM=True)["data"]
    #         cssa(sock, n = 21, f = "clearGrp1", a = i)
    #         adc_dat.append(dat)
    #         if dat: 
    #             cssa(sock = sock, n = 23, f = "overWriteGrp1", a = 0, data=1)
    #             cssa(sock = sock, n = 23, f = "overWriteGrp1", a = 0, data=0)
    #             run = False
    #     if count % 100 == 0: print "here again"
    #     # run=False
    # print("done in %i" % count)
    # # print adc_dat
    
    sock.close()


def adc_test():
    # this uses the ADC's test feature
    sock = socket(AF_INET, SOCK_DGRAM)
    
    sock.settimeout(1)
    
    sendAddr = ('192.168.0.2', 240) # (host, port) both defined in our_ecc
    rcvAddr = ('', 59329)
    
    sock.bind(rcvAddr) # where to receive data
    sock.connect(sendAddr) # where to send from
    
    print "rsync", 
    rsync(sock)
    print "inhibi", 
    sendCOR(sock, "cmd_inhibit", mod=1)
    print "F(25)",
    cssa(sock, n= 21, f=25, a=0)
    print "wait..",
    sleep(0.002)
    print "read ADC:"
    for i in range(11):
        dat = cssa(sock, n = 21, f="readClrGrp1", a=i)
        if "qresp" in dat: print i, dat["qresp"][1], dat["data"][1]
    sock.close()
    print "done"


if __name__ == '__main__':
    # filter for wire shark: 
    #(ip.src == 192.186.0.1 and ip.dst == 192.168.0.2) or (ip.src == 192.168.0.2 and ip.dst == 192.186.0.1)
    # adc_test()

    main_test()
