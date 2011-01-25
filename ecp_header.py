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
_request_no = 0
_request_no_s = pack('H',0)

# these are the structures of the headers 
headerPackStr = 'B'*6 + 'H'*4 + 'I' + 'H'*4
CORPackStr = 'B'*2 + 'H'*4

# format [header component, value]
# use a list NOT dictionary to maintain sequence, look at possible sequential dictionaries? 
ecp_header = [ # would be dictionary but order is important
    ['llcDestinationLsap', b'\x60'],
    ['llcSourceLsap', b'\x60'],
    ['llcControl', b'\x77'],
    ['llcStatus', b'\x01'],
    ['pseudoLlc3Control', b'\x03'],
    ['pseudoLlc3Status', b'\x00'],
    # Frametype doesn't seem to ever be changed [defined in manual]
    ['frameType', b'\x00\x07'],            
    # request no. should increment with calls to it possibly set as int not str?
    ['requestNumber', pack('H',_request_no)],
    ['crateNumber', b'\x00\x01'],
    ['hostId', b'\xFF\xFF'],
    # use os getpid[] function at top 
    # this may be tricky if ever run with multiple threads
    ['hostPid', _ourpid],                  
    # no idea what hostAccessId is: set in ecc_interface         
    ['hostAccessId', b'\x00\x01'],          
    ['flags', b'\x00\x00'],
    ['status', b'\x00\x47'],
    ]

ecp_COR = [ # holds a standard COR command for ecc
    ['modifier', b'\x08'],
    ['cmd', b'\x01'],
    ['op_lo', b'\x00\x00'],
    ['op_hi', b'\x00\x00'],
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
    global _request_no
    global ecp_header
    _request_no += 2
    ecp_header[7][1] = pack('H',_request_no)
    
def getheader():
    """
    Returns the ECC header as a single string
    """
    res = b''
    for entry in ecp_header:
        res += entry[1]
    _inc_request_no()
    return res
    
# TODO: find out what these COR values are actually for!
# some seem to be for set up:
# (eg: CMD_CLR = cccc = 0xB, cccz=0xA=cmd_init, ccci=0xC=cmd_inhibit)
def getCOR(cmd='cmd_camac_op'): 
    """
    returns the ecc COR command
    """
    res = b''
    for entry in ecp_COR:
        if entry[0] == 'cmd':
            entry[1] = pack('B', ecp_COR.index(cmd))
        res += entry[1]
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