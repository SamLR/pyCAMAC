#! /usr/bin/python

"""
reads in the data file and plots it in ROOT
"""

import ROOT

def plot_it(files_on, files_off, file_fmt, positions, intensities, union):
    res = {}
    cf_rates = {}
    for i in range(len(intensities)):
        entries = sum = 0
        on_file  = file_fmt % files_on [i]
        on_file  = open(on_file, "r")
        
        for line in on_file:
            if '-' in line: 
                continue
            else:
                sum += float(line)
                entries += 1
        on_file.close()
        ave_on = sum/entries
        
        sum = entries = 0
        off_file = file_fmt % files_off[i]
        off_file = open (off_file, "r")
        
        for line in off_file:
            if '-' in line: 
                continue
            else:
                sum += float(line)
                entries += 1
        off_file.close()
        
        ave_off = sum/entries
        rate = (ave_on - ave_off)/intensities[i]
        res[positions[i]] = rate
        if i in union.values(): cf_rates[positions[i]] = rate
        print "at", positions[i], "the rate is:", rate, "Hz"
    return res, cf_rates


def draw_it(hist):
    hist.GetXaxis().SetTitle("x [cm]")    
    hist.GetYaxis().SetTitle("y [cm]")
    hist.GetZaxis().SetTitle("Hits")
    hist.Draw('SURF2')


if __name__ == '__main__':
    # file info: format of name, position for that data, intensity, hite rate on number and off number
    file_fmt = 'data/hit_rates_%03i.txt'
    
    mg_pos  = ((-17,20), (-17,-16), (-17,0), (17,0), (17,20), (17,-16), (0,-16), (0,20), (0,0))  
    mg_int  = (0.636,    0.893,     0.967,   1.014,  0.939,   0.878,    0.908,   0.833,  0.863)
    mg_on   = (12,       14,        15,      16,     18,      19,       20,      21,     22) 
    mg_off  = (13,       226,       228,     230,    232,     234,      236,     238,    240) 
    
    cu_pos = ((0,25), (-17,25), (0,20), (0,0))  #(0,20),  
    cu_int = (0.560,  0.575,    0.772,  0.862)
    cu_on  = (23,     24,       25,     26)
    cu_off = (242,    244,      246,    246)
    
    late_pos = ((-17, 34), (0,0),  (-35,25))
    late_int = (0.1514,    0.1514, 0.1514)
    late_on  = (42,        49,     54)
    late_off = (47,        46,     52)
    
    # find the common measurement i.e. reference positions
    union_cu, union_mg, union_late = {}, {}, {}
    for i in mg_pos:
        if i in cu_pos: 
            union_cu[i] = cu_pos.index(i)
            union_mg[i] = mg_pos.index(i)
        if i in late_pos:
            union_late[i] = late_pos.index(i)
    
    # calaculate the intensity averaged rates and find the reference values
    print "mg union:", union_mg, "cu union:", union_cu, "late union:", union_late
    data_mg, mg_rates     = plot_it(mg_on, mg_off, file_fmt, mg_pos, mg_int, union_mg)        
    data_cu, cu_rates     = plot_it(cu_on, cu_off, file_fmt, cu_pos, cu_int, union_cu)
    data_late, late_rates = plot_it(late_on, late_off, file_fmt, late_pos, late_int, union_late)
    
    print data_late, late_rates
    # calculate the scaling at each ref position
    scale, scale_late = {}, {}
    for i in union_mg:        
        scale[i] = mg_rates[i]/cu_rates[i]
        if i in union_late:
            scale_late[i] = mg_rates[i]/late_rates[i]
        print "cu", cu_rates[i]
        print "mg", mg_rates[i]
        
    print "scale mg:cu", scale, "scale mg:late", scale_late
    
    # make scale the average
    sum = n = 0
    for i in scale:
        sum += scale[i]
        n += 1
    scale_val = sum/n
    
    sum = n = 0
    for i in scale_late:
        sum += scale_late[i]
        n += 1
    scale_late_val = sum/n
    
    # make it pretty and rooty!
    ROOT.gROOT.ProcessLine('.x prettyPalette.C')
    hist_mg   = ROOT.TH2F("hit_rate_mg", "beam_flux_mg",             20, -40, 25, 20, -25, 40)
    hist_cu   = ROOT.TH2F("hit_rate_cu", "beam_flux_cu",             20, -40, 25, 20, -25, 40)
    hist_late = ROOT.TH2F("hit_rate_late", "beam_flux_late",         20, -40, 25, 20, -25, 40)
    hist_all  = ROOT.TH2F("hit_rate_combined", "beam_flux_combined", 20, -40, 25, 20, -25, 40)
    
    # fill the histograms
    for i in data_mg: 
        hist_mg.Fill(i[0], i[1], data_mg[i])
        hist_all.Fill(i[0], i[1], data_mg[i])
    for i in data_cu: 
        hist_cu.Fill(i[0], i[1], data_cu[i])
        if i in scale: continue
        hist_all.Fill(i[0], i[1], data_cu[i]*scale_val)
    for i in data_late:
        hist_late.Fill(i[0], i[1], data_late[i])
        if i in scale_late : continue
        hist_all.Fill(i[0], i[1], data_late[i]*scale_late_val)
    
    can = ROOT.TCanvas("data", "data")
    can.Divide(3,1)
    can.cd(1)
    draw_it(hist_mg)
    can.cd(2)
    draw_it(hist_cu)
    can.cd(3)
    draw_it(hist_late)
        
    can2 = ROOT.TCanvas("combined_data", "combined_data")
    draw_it(hist_all)
    
    # stops everything closing straight away
    print "press any key then press 'enter' to quit"
    run = True
    while run:
        d = raw_input()
        if d:
            exit()
            
