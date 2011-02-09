"""
packet_desc.py

This file contains the field lists, and default values of ecc packets

Created by Sam Cook on 2011-02-09.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

from os import getpid

def _genpackstr(dic, lst):
    """Generates pack strings from the dictionaries"""
    res = ''
    for entry in lst:
        res += dic[entry][0]
    return res

_ourpid = getpid()
_request_number = 0x0000

# these two dictionaries should be read in the order defined by 
# their respective _fields lists
# the format they follow is Key:["packstring", initial value]
ecp_header = {}
ecp_COR = {}

ecp_header_packStr = ''
ecp_COR_packStr = ''
ecp_rcvd_packStr = 'HHH'

ecp_header_fields = ('llcDestinationLsap', 'llcSourceLsap',
    'llcControl', 'llcStatus', 'pseudoLlc3Control',
    'pseudoLlc3Status', 'frameType', 'requestNumber',
    'crateNumber', 'hostId', 'hostPid', 'hostAccessId',
    'flags', 'status',)

ecp_rcvd_fields = ('nwords', 'data', 'qresp')

ecp_COR_fields = ('modifier', 'cmd', 'lo', 'hi')

_ecp_header_defaults = ( # would be dictionary but order is important
    ['B', 0x60], # LSAP dest
    ['B', 0x60], # LSAP src
    ['B', 0xF7], # llc control - changes for every send/recv pair
    ['B', 0x00], # llc status
    ['B', 0x03], # llc3 ctrl
    ['B', 0x00], # llc3 status
    ['H', 0x0007], # frame type - 0x07 = UI_frame            
    ['H', _request_number], # request No should increment
    ['H', 0x0001], # crate No
    ['H', 0xFFFF], # host id
    ['I', _ourpid], # pid                  
    ['H', 0x0001], # host access id          
    ['H', 0x8300], # flags : IxLF 3 * xxxx; I = immediate or defered command, L/F = last/first segment x = don't care
    ['H', 0x0047], # status 
    )
    
ecp_header = dict(zip(ecp_header_fields, _ecp_header_defaults))
    
_ecp_COR_defaults = (
    ['B', 0x01], # COR modifier: essentially the argument for COR command ref p30 manual
    ['B', 0x01], # COR command - some std CAMAC commands some others see COR_cmds & manual
    ['H', 0x0001], # Lo & hi used if sending multiple instructions
    ['H', 0x0000], 
    )

ecp_COR = dict(zip(ecp_COR_fields, _ecp_COR_defaults))

ecp_COR_cmds = ( # enumerate as a list - access using .index('func_name')      # enum range
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
    'cmd_attach_cor_lam'                                                   # 37 
    )

ecp_header_packStr = _genpackstr(ecp_header, ecp_header_fields)
ecp_COR_packStr = _genpackstr(ecp_COR, ecp_COR_fields)

if __name__ == '__main__':
    print ecp_COR_packStr
    print ecp_header_packStr
    print _ourpid


