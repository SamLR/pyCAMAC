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

# these are the structures of the headers 
headerPackStr = 'B'*6 + 'H'*4 + 'I' + 'H'*3 # this would include 'I' for the pid, but unpack doesn't like mixing 'I's
CORPackStr = 'B'*2 + 'H'*4
rcvd_fields = ('nwords', 'data', 'qresp')
# TODO sort out sequential dictionary
# TODO set up so that you can refer to received fields by name
# eg recvd.llcSourceLSAP rather than offsets


header_fields = ('llcDestinationLsap', 'llcSourceLsap',
    'llcControl', 'llcStatus', 'pseudoLlc3Control',
    'pseudoLlc3Status', 'frameType', 'requestNumber',
    'crateNumber', 'hostId', 'hostPid', 'hostAccessId',
    'flags', 'status',)

ecp_header_defaults = ( # would be dictionary but order is important
    ['B', 0x60],
    ['B', 0x60],
    ['B', 0xF7], # this changes, 
    ['B', 0x00],
    ['B', 0x03],
    ['B', 0x00],
    # Frametype doesn't seem to ever be changed [defined in manual]
    ['H', 0x0007],            
    # request no. should increment with calls to it possibly set as int not str?
    ['H', 0x0001],
    ['H', 0x0001],
    ['H', 0xFFFF], # 0xCCCC <- useful for cf against C version of call
    # use os getpid[] function at top 
    # this may be tricky if ever run with multiple threads
    ['I', _ourpid],                  
    # no idea what hostAccessId is: set in ecc_interface         
    ['H', 0x0001],          
    ['H', 0x8300],
    ['H', 0x0047],
    )

# makes defaults more legible allows this to be treated as a dict but kept in order
ecp_header_defaults = dict(zip(header_fields, ecp_header_defaults))
    
ecp_COR = [ # COR control, based on manual for CAMAC controlls only (naf, i, z & c)
    ['modifier', 'B',0x01], # this changes for certain COR commands
    ['cmd','B', 0x01], # 0x01 for main camac control only, changes otherwise
    ['lo', 'H', 0x0001], # Lo & hi used if sending multiple instructions
    ['hi','H', 0x0000], 
    ] 

COR_func = ( # enumerate as a list - access using .index('func_name')      # enum range
    'cmd_nop', 'cmd_camac_op', 'cmd_set_noint', 'cmd_set_wait',            # 0  : 3
    'cmd_book_module', 'cmd_unbook_module',                                # 4  : 5
    'cmd_book_lam', 'cmd_unbook_lam', 'cmd_attach_lam',                    # 6  : 8
    'cmd_init', 'cmd_clear', 'cmd_inhibit', 'cmd_test_inhibit',            # 9  : 12
    'cmd_enable_demand', 'cmd_demand_enabled', 'cmd_demand_present',       # 13 : 15
    'cmd_set_lam_mode', 'cmd_clear_lam', 'cmd_test_lam', 'cmd_inform_lam', # 16 : 19
    'cmd_change_sec', 'cmd_read_booking', 'cmd_read_times',                # 20 : 22 
    'cmd_read_stats', 'cmd_read_trace',                                    # 23 : 24
    'cmd_load_ecc_cmd', 'cmd_load_cor', 'cmd_read_sec',                    # 25 : 27
    'cmd_store_host_block', 'cmd_store_sys_block',                         # 28 : 39
    'cmd_chain_host_block', 'cmd_chain_sys_block',                         # 30 : 31
    'cmd_module_promiscuous', 'cmd_lam_promiscuous',                       # 32 : 33
    'cmd_alloc_response', 'cmd_enable_lam', 'cmd_clear_security',          # 34 : 36 
    'cmd_attach_cor_lam'                                                   # 37 :
    )

def _inc_request_no():
    """
    increments the request number
    """
    global ecp_header_defaults
    ecp_header_defaults["requestNumber"][1] += 1
    if ecp_header_defaults["requestNumber"][1] >= 0xFFFF:
        # reset otherwise it breaks
        ecp_header_defaults["requestNumber"][1] = 0

def set_llccontrol(llcControl):
    global ecp_header
    ecp_header_defaults["llcControl"][1] = llcControl
    
def getheader():
    """
    Returns the ECC header as a single string
    """
    res = b''
    for key in header_fields:
        # convert the value to a byte string according to it's packStr
        byte_type, val = ecp_header_defaults[key]
        res += pack(byte_type, val)
    _inc_request_no()
    return res
    
# some seem to be for set up:
# (eg: CMD_CLR = cccc = 0xB, cccz=0xA=cmd_init, ccci=0xC=cmd_inhibit)
def getCOR(cmd='cmd_camac_op', mod=None): 
    """
    Returns the ecc COR command, mod changes 
    the modifier value as given on p30 of the manual
    """
    res = b''
    for entry in ecp_COR:
        if (entry[0] == 'cmd'):
            res += pack('B',(COR_func.index(cmd) | 0x80))
            if cmd != 'cmd_camac_op': break
            # all other commands terminate at end of COR, i.e. here
            # 'lo'/'hi' are for CAMAC controls
        elif (entry[0] == 'modifier' and mod != None):
            # explicitly check for the default or mod = '0' would be ignored
            res += pack('B', mod)
        else:
            res += pack(entry[1], entry[2]) 
    return res

def gettop(cmd='cmd_camac_op', mod=None):
    """
    returns the combined header and COR 
    """
    res = getheader() + getCOR(cmd, mod)
    return res
    
if __name__ == '__main__':
    print "I'm sorry, but I can't allow you to do that."
    # print("current top is:")
    #     print(unpack(headerPackStr + CORPackStr, gettop()))
    #    print("current header is:")    # 
        # print(getheader())
        # print("current COR is:")
        # print(getCOR())
        # print("new top is")
        # print(gettop())
        # print("done")
        # print(ecp_header[7][1])