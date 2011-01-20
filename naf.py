"""
A simple set of functions for talking to CAMAC
"""

from struct import pack

def naf(n, a, f):
    """
    Converts n, a, f to a 2byte string that is suitable
    to be sent to CAMAC in the format: 0fff ffnn nnna aaas
    """
    
    return pack('H',(f << 10 | n << 5 | a << 1 | 0))
    
