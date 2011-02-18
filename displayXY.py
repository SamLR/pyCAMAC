#! /usr/bin/python

"""
reads in the data file and plots it in ROOT
"""

import ROOT

if __name__ == '__main__':        
    file_numbers = (2,3,4)
    file_fmt = 'test_dat/test_%03i.txt'
    
    # open the files and read them into a histogram
    hist = []
    for ch in range(1, 4):
        h = ROOT.TH2F("ch1&ch%i" % ch, "pedestal_data", 2000, 0, 2000, 2000, 0, 2000)
        hist.append(h)
    
    for n in file_numbers:
        file = open(file_fmt % n, "r")
        for line in file:
            dat = line.split()
            for ch in range(1, 4):
                hist[ch - 1].Fill(float(dat[0]), float(dat[ch]))
    
    canvas = ROOT.TCanvas("dat", "dat")
    canvas.Divide(2, 2)
    
    for pad in range (1, 4):
        canvas.cd(pad)
        hist[pad - 1].Draw()
        
    run = True
    while run:
        d = raw_input()
        if d:
            run = False