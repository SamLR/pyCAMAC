#!/usr/bin/env python
# encoding: utf-8
"""
TH1additions.py

This is a wrapper class for the root TH1 histogram
It will allow instantiation calls that pass a iterator
which will be displaed in a histogram with a 100 bins 
between min(iter) and max(iter)

Created by Sam Cook on 2011-02-06.
Copyright (c) 2011 All rights reserved.
"""

from ROOT import TH1F, gRandom

verbose = False

def tracer(f, *args, **kargs):
    if verbose:
        def new_func(*args, **kargs):
            print "entering", f.__name__
            f(*args, **kargs)
            print "exiting", f.__name__
        return new_func
    else:
        return f

class TH1(TH1F, object):
    """This is a wrapper class for the Root TH1F histogram, it is primerly 
    to allow creation of histograms initialised with a list or other iterable
    other functionality will be added later"""
    
    @tracer
    def __init__(self, data=[], *args):# title='hist', description='hist', nbins=100, xmin=0.0, xmax=100.0):
        """Creates a root TH1F of data (an iterable) with title, description, nbins, xmax and xmin.
        The number of bins defaults to 100, if the range values aren't set they are
        based from the data."""
        
        if data: 
            xmin = float(min(data))
            xmax = float(max(data))
            # args = (title, description, nbins, xmin, xmax)
            TH1F.__init__(self, *args)#title, description, nbins, xmin, xmax)
            self.addList(data)
        else:
            # args = (tite, description, nbins, xmin, xmax)
            TH1F.__init__(self, *args) #title, description, nbins, xmin, xmax)
    
    @tracer
    def addList(self, data):
        """adds data (an itererable) to the histogram"""
        try:            
            for entry in data:
                try:
                    self.Fill(entry)
                except TypeError:
                    raise TypeError ("%f is not a number, cannot fill histogram." % entry)
        except TypeError:
            raise TypeError ("%s is not an iterable; try wrapping it in a 'list()' call" % data)
    

if __name__ == '__main__':
    
    dat = []
    for i in range (100):
        dat.append(gRandom.Gaus())    
    hist = TH1(dat)
    print "__init__ works ok\n"
    
    dat = []
    for i in range (20):
        d = str(gRandom.Gaus()) + ", "
        a = float(d.strip()[:-1])
        dat.append(a)
    hist.addList(dat)
    print "addList works as expected\n"
    
    try:
        hist.addList(5)
    except TypeError:
        print "error checking succesful"
    
    hist.Fill(float("   5,   ".strip()[:-1]))
    
    from fileUpdater import string_stripper
    
    hist.Draw()
    
    hist2 = TH1()
    hist2.Fill(5)
    hist2.Fill(float("   5  ".strip()))
    hist2.Fill(string_stripper("    ,sFSD^ 5,"))
    hist2.Draw()
    
    while True:
        try:
            pass
        except Exception, e:
            del TH1
    
    print "done"
    

    

