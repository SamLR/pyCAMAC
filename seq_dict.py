#!/usr/bin/env python
# encoding: utf-8
"""
seq_dict.py

Created by Sam Cook on 2011-02-09.
"""

class seq_dict(dict):
    """
    A sequential dictionary who's order is user specified
    """
    
    def __init__(self, kargs = {}, order = None):
        """
        Creates a dictionary that is ordered according to order, 
        if no order is given then sorted(keys) is used
        """
        self.order = list(order) if order else sorted(kargs.keys())
        dict.__init__(self, **kargs)
    
    def __setitem__(self, key, value):
        """
        Items added using [key] are appened to the order
        """
        self.order.append(key)
        dict.__setitem__(self, key, value)
    
    def insert(self, index, key, value = 0):
        """
        Inserts the key:value pair(s) at index
        """
        try:
            # if there are multiple k:v pairs
            for k in key:
                try:
                    val = value[index]
                except TypeError:
                    val = value
                    
                self.order.insert(index, k)
                dict.__setitem__(self, k, val)
                index += 1
        except TypeError:            
            self.order.insert(index, key)
            dict.__setitem__(self, key, value)
            
    def __iter__(self):
        for key in self.order:
            yield self[key]
    
    def keys(self):
        return self.order
            
    def __repr__(self):
        res = '{'
        for k in self.keys():
            res += "%s:%s, " % (repr(k), repr(self[k]))
        return res + '}'
    
    def setorder(self, order):
        """
        Manual setting of the order
        """
        if set(order) != set(self.order): 
            raise SeqDictError("The argument has incorrect keys")
        self.order = order
        
class SeqDictError(TypeError, Exception):
    pass
    

if __name__ == '__main__':
    d = {'a':1, 'b':2, 'c':3}
    o = ['c', 'b', 'a']
    sd = seq_dict(d, o)
    sd['d'] = 9
    sd.insert(-1, 'f', 6)
    sd.insert(0, ('hi','lo'))
    print sd.order
    print sd
    try:
        sd.setorder(('a', 'b'))
    except SeqDictError:
        pass
    sd.setorder(sorted(sd.order))
    print sd.order
    print sd
    
    for i in sd:
        print i