#!/usr/bin/env python
# encoding: utf-8
"""
fileUpdater.py

Created by Sam Cook on 2011-02-06.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os
from TH1py import *
from ROOT import TCanvas

def frameFactorer(n):
    """Finds suitable pairs of numbers for creating aXb grids, eg canvases"""
    a = b = c = int(abs(n)**0.5)
    while (a*b < n):
        # use 'c' to alternatly increment a and b
        if ((a - c) != (b - c)):
            b += 1
        else:
            a += 1
    else: 
        return a, b


def_TH1 = ('hist', 100, 0.0, 100.0)
# 3 instance attributes: a list of histograms, hist, a canvas & n_ch
class FileUpdater(file): 
    """The file updater produces and manages a chain of files
    with incrementing numerical suffixes, each file 
    is also plotted in n_data root histograms, the assumption being
    that each n_data corresponds to a channel"""
    file_number = 0 # class attribute
    canvas = None,
    
    def __init__(self, file_path = 'r_%03i.txt', mode="w", n_dat=4, header = '', TH1args=def_TH1, update_on=100):
        """if file_path contains '%' then that is formatted as the file_number
        multiple uses of '%' cause an error. If included as an argument
        the header is added to the beginning of the file. Arguments for initialising 
        the histogram should be included in the dictionary TH1F_kargs"""
        # set instance attributes
        self.n_ch = n_dat
        self.n_run = FileUpdater.file_number
        self.entries = 0
        self.update_on = update_on
        FileUpdater.file_number +=1
        if '%' in file_path: file_path = file_path % self.n_run
        
        # open the file
        file.__init__(self, file_path, mode)
        if header: file.write(self, header)
        
        # initilse the histograms
        self.hist = []
        for i in range(self.n_ch):
            hist_name = "run%i_ch%i" % (self.n_run, i)
            self.hist.append(TH1([], hist_name, *TH1args))
        
        FileUpdater.canvas = TCanvas("c%i" % self.n_run)
        FileUpdater.canvas.Divide(*frameFactorer(self.n_ch))
    
    def write(self, dataStr, sep=None):
        """write the dataStr to file then splits it using sep to plot"""
        dat = dataStr.split(sep)
        if len(dat) != self.n_ch: 
            raise IndexError("%s has %i entries, expecting %i" % (dat, len(dat), self.n_ch))
        dat = [string_stripper(i) for i in dat]
        file.write(self, dataStr) 
        for hist in self.hist:
            filler = dat.pop(0)
            try:
                hist.Fill(filler)
            except TypeError, e:
                print filler
                raise e
                for h in self.hist:
                    del h
                    del FileUpdater.canvas
        
        if (self.entries % self.update_on == 0):
            self.update()
    
    def update(self):
        """Updates the displayed histograms, best called every 
        few 100 events/ few seconds"""
        pad = 1
        for entry in self.hist:
            FileUpdater.canvas.cd(pad)
            entry.Draw() 
            pad += 1

        FileUpdater.canvas.Update()
    
    def close(self):
        """close the file and delete the histograms"""
        del FileUpdater.canvas
        del self.hist
        del self.n_ch
        file.close(self)
    
def string_stripper(s):
    """ 
    Convert a string into a float, removes all none digit
    or none decimal place characters. Raises a TypeError
    if more than one deimal place is discovered"""
    res = ''
    point_count = 0
    if (s[0] == '-') or (s[0] == '+'): res = s[0]
    for i in s:
        if i.isdigit():
            res += i 
        elif (i=='.'):
            res += '.'
        else: 
            pass
        
        s = s[1:] # 'delete' the first character
        if i == '.': point_count += 1
        if point_count > 1: raise TypeError("cannot have 2 decimal places")
    return 0.0 + float(res)
            

if __name__ == '__main__':
    from ROOT import gRandom
    from time import sleep
    n_tests = 1
    
    # generate a set of random data points to add
    dat = []
    for i in range(10):
        s = ''
        for j in range(4):
            s += "%04.2f  " % abs(gRandom.Gaus())
        dat.append(s)
    print "data generated, running tests"
    t = FileUpdater("test.txt")

    for i in range(n_tests):
        print "0"
        count = 0
        for d in dat:
            print"1"
            
            t.write(d)
            print"2"
            count += 1
            if count % 100 == 0: 
                print"update"
                t.update
        sleep(5)
    print "done"
    try:
        while(True):
            pass
    except Exception, e:    
        pass
    finally:
        t.close()