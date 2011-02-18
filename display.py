#! /usr/bin/python

"""
reads in the data file and plots it in ROOT
"""

import ROOT

if __name__ == '__main__':        
    file_numbers = (262,) #range(209)
    file_fmt = 'data/test_%03i.txt'
    
    # open the files and read them into a histogram
    hist = []
    for ch in range(4):
        h = ROOT.TH1F("ch%i" % ch, "Beam on 1nA pos: (0, 20)", 2**12, 0, 2**12 + 1)
        hist.append(h)
    
    for n in file_numbers:
        file = open(file_fmt % n, "r")
        for line in file:
            if '-' in line: continue
            
            dat = line.split()
            for ch in range(4):
                hist[ch].Fill(float(dat[ch]))
    
    canvas = ROOT.TCanvas("dat", "dat")
    canvas.Divide(2, 2)
    
    for pad in range (1, 5):
        canvas.cd(pad)
        hist[pad - 1].Draw()
        
    run = True
    while run:
        d = raw_input()
        if d:
            run = False