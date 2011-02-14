""" 
replicates the header values for ECC as taken from superNemo_dump/ecc1365 files 
files defining values are: ecc.h, our_ecc.h, ecc_interface.c

made S. Cook 18-01-11
"""

from struct import pack, unpack, calcsize
from packet_desc import *
from seq_dict import *

def _inc_request_no():
    """
    increments the request number
    """
    # global ecp_header
    ecp_header["requestNumber"][1] += 1
    if ecp_header["requestNumber"][1] >= 0xFFFF:
        # reset otherwise it breaks
        ecp_header["requestNumber"][1] = 0

    
def getheader(deferred=False, llcControl=None, status=None, flags=None):
    """
    Returns the ECC header as a single string
    """
    res = b''
    for key in ecp_header:
        if (key == "flags") and flags:
            res += pack(ecp_header[key][0], flags) # normally flags set to 0x8300
        elif (key == "llcControl") and llcControl:
            res += pack(ecp_header[key][0], llcControl)
        elif (key == "status") and status:
            res += pack(ecp_header[key][0], status)
        res += pack(*ecp_header[key])
    _inc_request_no()
    return res

def getCOR(cmd='cmd_camac_op', mod=1, ops=0): 
    """
    Returns the ecc COR command, mod changes 
    the modifier value as given on p30 of the manual
    NB - this may not always return 'lo' and 'hi'
    this is as intended
    """
    res = b''
    for key in ecp_COR:
        pack_str, val = ecp_COR[key]
        if (key == 'cmd'):
            res += pack(pack_str, (ecp_COR_cmds.index(cmd) | 0x80))
            if not((cmd == 'cmd_camac_op') or (cmd == 'cmd_attach_lam')):
                break
        elif (key == 'modifier'):
            res += pack(pack_str, mod)
        elif (key == 'lo'):
            val = ops if ops else val
            res += pack(pack_str, val)
        else:
            res += pack(pack_str, val) 
    return res

def gettop(cmd='cmd_camac_op', mod=1, flags=None, llcControl=None, status=None, ops=None):
    """
    returns the combined header and COR 
    """
    res = getheader(flags, llcControl, status) + getCOR(cmd, mod, ops)
    return res

def printer(sdict, byteStr):
    """
    Essentially exists because unpack has issues with 'I'
    and print doesn't like byte strings
    """
    res = []
    for key in sdict:
        char = sdict[key][0]
        current, byteStr = byteStr[:calcsize(char)], byteStr[calcsize(char):]
        res += "0x%x " % unpack(char, current)[0]
    return res
    
def dictify(sdict, byteStr):
    """
    Returns a dictionary of the byteStr
    """
    res = seq_dict()
    for key in sdict:
        packStr = sdict[key][0]
        size = calcsize(packStr)
        current, byteStr = byteStr[:size], byteStr[size:]
        res[key] = (packStr, unpack(packStr, current)[0] )
    return res
    
if __name__ == '__main__':
    from struct import unpack

    print ("current top is:")
    print (printer(ecp_header + ecp_COR, gettop()))
    print ("check request number")
    print (printer(ecp_header + ecp_COR, gettop()))
    print ("check dictify")
    print "status = %s 0x%x" %( dictify(ecp_header + ecp_COR, gettop())['status'])