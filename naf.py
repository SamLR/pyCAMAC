"""
A simple function for sending single commands to CAMAC
"""

from struct import pack

# dictionary format "command name":(command code, [subaddress needed?], [data needed?])
camacFunction = { 
    "readGrp1": (0, "subaddr"),
    "readGrp2": (1, "subaddr"),
    "readClrGrp1": (2, "subaddr"),
    "readClrGrp2": (3, "subaddr"),
    "testLAM": (8,),
    "clrGrp1": (9, "subaddr"),
    "clearLAM": (10,),
    "clrGrp2": (11, "subaddr"),
    "overWriteGrp1": (16, "subaddr", "data"),
    "overWriteGrp2": (17, "subaddr", "data"),
    "maskOverWriteGrp1": (18, "subaddr", "data"), 
    "maskOverWriteGrp2": (19, "subaddr", "data"),
    "disable": (24,),
    "increment": (25, "subaddr"),
    "enable": (26,),
    "testStatus": (27,),
    }
    

def naf(n, f, a = -1, data = -1 ):
    # data to write
    """
    Converts n, a, f to a 2byte string that is suitable
    to be sent to CAMAC in the format: 0fff ffnn nnna aaas
    """
    # get the function info required (number and whether an address etc are needed)
    funcCode = camacFunction[f]
    if (("subaddr" in funcCode) and (a == -1)):
        raise Exception("function requires a subaddress")
    elif (("data" in funcCode) and (data == -1)):
        raise Exception("function requires a data")
        
    a = a if (a >= 0) else 0
    data = pack('I', data) if (data >= 0) else b''
    f = funcCode[0]
    
    res =  pack('H',(f << 10 | n << 5 | a << 1 | 0)) + data
    return res
    
if __name__ == '__main__':
    from struct import unpack
    print(hex(unpack("H", naf(1,"clearLAM"))[0]))   # should be 0x2820
    print(hex(unpack("H", naf(1,"clrGrp2", 0))[0])) # should be 0x2c20
    print(hex(unpack("H", naf(1,"clrGrp2", 5))[0])) # should be 0x2c2a
    # the following are not supported in python2.6
    # print(hex(unpack("HHH", naf(1,"overWriteGrp2", 6, 88))[0]), end = ' ') # should be 0x442c
    # print(hex(unpack("HHH", naf(1,"overWriteGrp2", 6, 88))[1]), end = ' ') # should be 0x0058
    # print(hex(unpack("HHH", naf(1,"overWriteGrp2", 6, 88))[2]), end = ' ') # should be 0x0000
