#!/usr/bin/env python
# encoding: utf-8
"""
fileUpdater.py

Created by Sam Cook on 2011-02-06.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import TH1py
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


# 3 instance attributes: a list of histograms, hist, a canvas & n_ch
class FileUpdater(file): 
    """The file updater produces and manages a chain of files
    with incrementing numerical suffixes, each file 
    is also plotted in n_data root histograms, the assumption being
    that each n_data corresponds to a channel"""
    file_number = 0 # class attribute
    
    def __init__(self, file_path = 'r_%03i.txt', n_dat=4, header = '', **TH1F_kargs):
        """if file_path contains '%' then that is formatted as the file_number
        multiple uses of '%' cause an error. If included as an argument
        the header is added to the beginning of the file. Arguments for initialising 
        the histogram should be included in the dictionary TH1F_kargs"""
        self.n_ch = n_dat
        self.n_run = FileUpdater.file_number
        if '%' in file_path: file_path = file_path % self.n_run
        file.__init__(self, file_path, "w")
        if header: file.write(self, header)
        
        self.hist = []
        for i in range(self.n_ch):
            hist_name = "run%i_ch%i" % (self.n_run, i)
            self.hist.append(TH1py.TH1(title=hist_name, **TH1F_kargs))
        
        self.canvas = TCanvas("c%i" % self.n_run)
        self.canvas.Divide(*frameFactorer(self.n_ch))
        FileUpdater.file_number += 1
    
    def writeDat(self, dataStr, sep=None):
        """write the dataStr to file then splits it using sep to plot"""
        dat = dataStr.split(sep)
        if len(dat) != self.n_ch: 
            raise IndexError("%s has %i entries, expecting %i" % (dat, len(dat), self.n_ch))
        for entry in dat: 
            if not entry.isdigit():
                raise TypeError("%s is not a number." % entry)
        file.write(self, dataStr) 
        for hist in self.hist:
            hist.Fill(dat.pop(0))
    
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
        del self.canvas
        del self.hist
        del self.n_ch
        file.close(self)
    

if __name__ == '__main__':
    from ROOT import gRandom
    from time import sleep
    n_tests = 10
    
    # generate a set of random data points to add
    dat = []
    for i in range(1000):
        s = ''
        for j in range(4):
            s += "%04.2f  " % abs(gRandom.Gaus())
        dat.append(s)
    
    print "data generated, running tests"
    for i in range(n_tests):
        t = FileUpdater()
        count = 0
        for d in dat:
            t.writeDat(d)
            count += 1
            if count % 100 == 0: t.update
        sleep(5)
        t.close()