""" 
replicates the header values for ECC as taken from superNemo_dump/ecc1365 files 
files defining values are: ecc.h, our_ecc.h, ecc_interface.c

made S. Cook 18-01-11
"""

from os import getpid     # used to get the pid of this process
from struct import pack   # imports 'pack' to create byte strings
# TODO: add COR variable

# convert the PID of this process into an 
# unsigned short int [2 bytes]
_ourpid = pack('I', getpid())

# format [header component, value]
# use a list NOT dictionary to maintain sequence, look at possible sequential dictionaries? 
ecp_header = [ # would be dictionary but order is important
    ['llcDestinationLsap', b'\x60'],
    ['llcSourceLsap', b'\x60'],
    ['llcControl', b'\x77'],
    ['llcStatus', b'\x01'],
    ['pseudoLlc3Control', b'\x03'],
    ['pseudoLlc3Status', b'\x00'],
    ['frameType', b'\x00\x07'],            # this doesn't seem to ever be changed [defined in manual]
    ['requestNumber', b'\x00\x00'],        # this should increment with calls to it possibly set as int not str?
    ['crateNumber', b'\x00\x01'],
    ['hostId', b'\xFF\xFF'],
    ['hostPid', _ourpid],                  # use os getpid[] function
    ['hostAccessId', b'\x00\x01'],          # no idea what this is set in ecc_interface         
    ['flags', b'\x00\x00'],
    ['status', b'\x00\x47'],
    ]

ecp_COR = [ # holds a standard COR command for ecc
    ['modifier', b'\x08'],
    ['cmd', b'\x01'],
    ['op_lo', b'\x00\x00'],
    ['op_hi', b'\x00\x00'],
    ]
    
def getheader():
    """
    Returns the ECC header as a single string
    """
    res = b''
    for entry in ecp_header:
        res += entry[1]
    return res
    
# TODO: add dictionary options of COR commands
# TODO: find out what these COR values are actually for!
def getCOR(): 
    """
    returns the ecc COR command
    """
    res = b''
    for entry in ecp_COR:
        res += entry[1]
    return res

def gettop():
    """
    returns the combined header and COR 
    """
    res = getheader() + getCOR()
    print(res)
    return res
    
if __name__ == '__main__':
    # TODO: change this to only print hex (hexdump?)
    print("current top is:")
    print(gettop())
    print("current header is:")
    print(getheader())
    print("current COR is:")
    print(getCOR())
    print("done")