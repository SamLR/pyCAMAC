""" 
replicates the header values for ECC as taken from superNemo_dump/ecc1365 files 
files defining values are: ecc.h, our_ecc.h, ecc_interface.c

made S. Cook 18-01-11
"""

from os import getpid     # used to get the pid of this process
from struct import pack   # imports 'pack' to create byte strings

# convert the PID of this process into an 
# unsigned short int [2 bytes]
_ourpid = pack('I', getpid())


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
    
def getheader():
    """
    Returns the ECC header as a single string
    """
    res = b''
    for entry in ecp_header:
        res += entry[1]
    print (res)
    return res