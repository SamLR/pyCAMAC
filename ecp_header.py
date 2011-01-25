""" 
replicates the header values for ECC as taken from superNemo_dump/ecc1365 files 
files defining values are: ecc.h, our_ecc.h, ecc_interface.c

made S. Cook 18-01-11
"""

from os import getpid     # used to get the pid of this process
from struct import pack   # imports 'pack' to create byte strings

# convert the PID of this process into an 
# unsigned short int [2 bytes]
_ourpid = getpid()
_request_no = 1

# these are the structures of the headers 
headerPackStr = 'B'*6 + 'H'*4 + 'I' + 'H'*4
CORPackStr = 'B'*2 + 'H'*4

# format [header component, packStr, value]
# use a list NOT dictionary to maintain sequence, 
# TODO look at possible sequential dictionaries? 
ecp_header = [ # would be dictionary but order is important
    ['llcDestinationLsap', 'B', 0x60],
    ['llcSourceLsap', 'B', 0x60],
    ['llcControl', 'B', 0xF7],
    ['llcStatus', 'B', 0x00],
    ['pseudoLlc3Control', 'B',0x03],
    ['pseudoLlc3Status', 'B', 0x00],
    # Frametype doesn't seem to ever be changed [defined in manual]
    ['frameType', 'H', 0x0007],            
    # request no. should increment with calls to it possibly set as int not str?
    ['requestNumber', 'H', _request_no],
    ['crateNumber', 'H', 0x0001],
    ['hostId', 'H', 0xCCCC], # TODO change to FFFF
    # use os getpid[] function at top 
    # this may be tricky if ever run with multiple threads
    ['hostPid', 'I', _ourpid],                  
    # no idea what hostAccessId is: set in ecc_interface         
    ['hostAccessId', 'H', 0x0001],          
    ['flags', 'H', 0x8300],
    ['status', 'H', 0x0047],
    ]

ecp_COR = [ # holds a standard COR command for ecc
    ['modifier', 'B', 0x01],
    ['cmd', 'B', 0x81],
    ['op_lo', 'H', 0x0001],
    ['op_hi', 'H', 0x0000],
    ]


COR_func = ( # enumerate as a list - access using .index('func_name')
    'cmd_nop', 'cmd_camac_op', 'cmd_set_noint', 'cmd_set_wait',
    'cmd_book_module', 'cmd_unbook_module',
    'cmd_book_lam', 'cmd_unbook_lam', 'cmd_attach_lam',
    'cmd_init', 'cmd_clear', 'cmd_inhibit', 'cmd_test_inhibit',
    'cmd_enable_demand', 'cmd_demand_enabled', 'cmd_demand_present',
    'cmd_set_lam_mode', 'cmd_clear_lam', 'cmd_test_lam', 'cmd_inform_lam',
    'cmd_change_sec', 'cmd_read_booking', 'cmd_read_times',
    'cmd_read_stats', 'cmd_read_trace',
    'cmd_load_ecc_cmd', 'cmd_load_cor', 'cmd_read_sec',
    'cmd_store_host_block', 'cmd_store_sys_block',
    'cmd_chain_host_block', 'cmd_chain_sys_block',
    'cmd_module_promiscuous', 'cmd_lam_promiscuous',
    'cmd_alloc_response', 'cmd_enable_lam', 'cmd_clear_security',
    'cmd_attach_cor_lam'
    )

def _inc_request_no():
    """
    increments the request number
    """
    # global _request_no
    global ecp_header
    # _request_no += 2
    # ecp_header[7][2] = _request_no
    ecp_header[7][2] += 1
    
def getheader():
    """
    Returns the ECC header as a single string
    """
    res = b''
    for entry in ecp_header:
        # convert the value to a byte string according to it's packStr
        res += pack(entry[1], entry[2])
    _inc_request_no()
    return res
    
# some seem to be for set up:
# (eg: CMD_CLR = cccc = 0xB, cccz=0xA=cmd_init, ccci=0xC=cmd_inhibit)
def getCOR(cmd='cmd_camac_op'): 
    """
    returns the ecc COR command
    """
    res = b''
    for entry in ecp_COR:
        if (entry[0] == 'cmd'):
            res += pack('B',(COR_func.index(cmd) | 0x80))
        else:
            res += pack(entry[1], entry[2]) 
    return res

def gettop(cmd='cmd_camac_op'):
    """
    returns the combined header and COR 
    """
    res = getheader() + getCOR(cmd)
    return res
    
if __name__ == '__main__':
    print("current top is:")
    print(gettop())
    print("current header is:")
    print(getheader())
    print("current COR is:")
    print(getCOR())
    print("new top is")
    print(gettop())
    print("done")
    print(ecp_header[7][1])