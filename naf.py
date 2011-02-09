"""
A simple function for sending single commands to CAMAC
"""

from struct import pack


    
if __name__ == '__main__':
    from struct import unpack
    s = unpack("HH", naf(20,"overWriteGrp1",0,1))
    print(hex(s[0]), hex(s[1])) 
    print(hex(unpack("H", naf(1,"clrGrp2", 0))[0])) # should be 0x2c20
    print(hex(unpack("H", naf(1,"clrGrp2", 5))[0])) # should be 0x2c2a
    # the following are not supported in python2.6
    # print(hex(unpack("HHH", naf(1,"overWriteGrp2", 6, 88))[0]), end = ' ') # should be 0x442c
    # print(hex(unpack("HHH", naf(1,"overWriteGrp2", 6, 88))[1]), end = ' ') # should be 0x0058
    # print(hex(unpack("HHH", naf(1,"overWriteGrp2", 6, 88))[2]), end = ' ') # should be 0x0000
