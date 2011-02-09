""" 
replicates the header values for ECC as taken from superNemo_dump/ecc1365 files 
files defining values are: ecc.h, our_ecc.h, ecc_interface.c

made S. Cook 18-01-11
"""

from struct import pack, unpack, calcsize
from packet_desc import *

def _inc_request_no():
    """
    increments the request number
    """
    # global ecp_header
    ecp_header["requestNumber"][1] += 1
    if ecp_header["requestNumber"][1] >= 0xFFFF:
        # reset otherwise it breaks
        ecp_header["requestNumber"][1] = 0
        
# TODO remove set_llccontrol
def set_llccontrol(llcControl):
    global ecp_header
    ecp_header_defaults["llcControl"][1] = llcControl
    
def getheader():
    """
    Returns the ECC header as a single string
    """
    res = b''
    for key in ecp_header_fields:
        packStr, val = ecp_header[key]
        res += pack(packStr, val)
    _inc_request_no()
    return res
    
# some seem to be for set up:
# (eg: CMD_CLR = cccc = 0xB, cccz=0xA=cmd_init, ccci=0xC=cmd_inhibit)
def getCOR(cmd='cmd_camac_op', mod=1): 
    """
    Returns the ecc COR command, mod changes 
    the modifier value as given on p30 of the manual
    NB - this may not always return 'lo' and 'hi'
    this is as intended
    """
    res = b''
    for entry in ecp_COR_fields:
        pack_str, val = ecp_COR[entry]
        if (entry == 'cmd'):
            res += pack(pack_str, (ecp_COR_cmds.index(cmd) | 0x80))
            if cmd != 'cmd_camac_op': break
        elif (entry == 'modifier'):
            print mod, pack_str
            res += pack(pack_str, mod)
        else:
            res += pack(pack_str, val) 
    return res

def gettop(cmd='cmd_camac_op', mod=1):
    """
    returns the combined header and COR 
    """
    res = getheader() + getCOR(cmd, mod)
    return res
    
def printer(packStr, byteStr):
    """
    Essentially exists because unpack has issues with 'I'
    and print doesn't like byte strings
    """
    res = ''
    for char in packStr:
        current, byteStr = byteStr[:calcsize(char)], byteStr[calcsize(char):]
        res += "0x%x " % unpack(char, current)[0]
    return res
    
def dictify(keyList, byteStr):
    """
    Returns a dictionary of the byteStr
    """
    res = []
    for key in keyList:
        current, byteStr = byteStr[:calcsize(char)], byteStr[calcsize(char):]
        res += "0x%x " % unpack(char, current)[0]
    return res
    
if __name__ == '__main__':
    from struct import unpack

    print ("current top is:")
    print (printer(ecp_header_packStr + ecp_COR_packStr, gettop()))
    print ("check request number")
    print (printer(ecp_header_packStr + ecp_COR_packStr, gettop()))