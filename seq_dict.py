#!/usr/bin/env python
# encoding: utf-8
"""
seq_dict.py

Created by Sam Cook on 2011-02-09.
"""

# TODO put a more logical order, or any order (ironicly)
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
    
    def insert(self, index, key, value = 0, in_situ = True):
        """
        Inserts the key:value pair(s) at index
        if the key already exists then the 
        previous value is replaced in situ 
        """
        while index < 0:
            index = len(self) - index
            
        count = 0
        try:
            # if there are multiple k:v pairs
            for k in key:
                try: 
                    val = value[count]
                    count += 1
                    if count == len(value): count = 0
                except TypeError:
                    val = value
                    
                dict.__setitem__(self, k, val) 
                
                if k in self.order and in_situ: 
                    # if key exists already but we want 
                    # to maintain position: do nothing (default)
                    continue;
                elif k in self.order and not in_situ:
                    # if the key already exists but we want to
                    # move it to the new location remove it
                    self.order.remove (k)
                    
                # assuming we've not continued insert at index and 
                # increment index
                self.order.insert(index, k)    
                index += 1
        except TypeError: 
            # insert single item           
            self.order.insert(index, key)
            dict.__setitem__(self, key, value)
            
    def __iter__(self):
        for key in self.order:
            yield key
    
    def keys(self):
        return self.order
        
    def items(self):
        res = []
        for k in self.order: res.append(self[k])
        return res
            
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
        
    def append(self, keys, values):
        """
        Appends the pair(s) to the dictionary
        """
        self.insert(-1, keys, values)
        
    def copy(self):
        D = dict(zip(self.keys(), self.items()))
        return seq_dict(D, self.order)
    
    def __add__(self, other):
        res = self.copy()
        res.append(other.keys(), other.items()) 
        return res
        
class SeqDictError(TypeError, Exception):
    pass
    

if __name__ == '__main__':
    d = {'a':1, 'b':2, 'c':3}
    o = ['c', 'b', 'a']
    sd = seq_dict(d, o)
    sd['d'] = 9
    sd.insert(-1, 'f', 6)
    sd.insert(-1, ('e', 'g'), (9, 10))
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
        
    sd2 = seq_dict(dict(zip((1, 2, 3), "hel")), (3, 2, 1))
    sd3 = sd2.copy()
    print sd3
    print sd2
    a = sd + sd2
    print a['d']
    print a