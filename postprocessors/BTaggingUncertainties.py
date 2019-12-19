#! /usr/bin/env python

import os, multiprocessing
from ROOT import TFile, TH1F
import ROOT
from root_numpy import root2array
import sys

from aliases import alias, working_points

from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument('-b', '--btagging', action='store', type=str, dest='btagging',default='medium', choices = ['tight', 'medium', 'loose'])
args = parser.parse_args()

YEARS       = ['2016', '2017', '2018']
BTAGGING    = args.btagging

mass_points = [600, 800, 1000, 1200, 1400, 1600, 1800, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 7000, 8000]
BRANCHES = ['BTagAK4Weight_deepJet', 'BTagAK4Weight_deepJet_up', 'BTagAK4Weight_deepJet_down']
categories = ['bb', 'bq', 'mumu']

NTUPLEDIR = "/afs/cern.ch/work/m/msommerh/public/Zprime_to_bb_Analysis/Skim/"

def BTagUncertainties(year, mass):

    file_path = NTUPLEDIR+"MC_signal_{}_M{}.root".format(year,mass)
    
    weights = {}
    for category in categories:
        selection = alias[category].format(WP=working_points[BTAGGING])
        weights[category] = root2array(file_path, treename='tree', branches=BRANCHES, selection=selection)

    histograms = {}
    for i, branch in enumerate(BRANCHES):
        histograms[branch] = TH1F(branch, branch, len(categories), 0, len(categories))
    
        for j, category in enumerate(categories):
            for weight in weights[category][branch]:
                histograms[branch].Fill(j, weight)

    #outfile = TFile("testfile.root", "RECREATE")
    #for branch in BRANCHES:
    #    histograms[branch].Write()
    #outfile.Close()

    uncertainties = {"up":{}, "down":{}}

    for i, category in enumerate(categories):
        center_value = histograms[BRANCHES[0]].GetBinContent(i+1)
        up_value     = histograms[BRANCHES[1]].GetBinContent(i+1)
        down_value   = histograms[BRANCHES[2]].GetBinContent(i+1)

        if center_value==0:
            uncertainties["up"][category]   = -100 
            uncertainties["down"][category] = -100
        else:   
            uncertainties["up"][category]   = (up_value-center_value)/center_value
            uncertainties["down"][category] = (center_value-down_value)/center_value

    return uncertainties

if __name__ == "__main__":
    uncertainties = {}
    with open('BTag_uncertainties.py', 'w') as fout:
        fout.write("BTag_uncertainties = {\n")
        for m in mass_points:   
            uncertainties[m] = {}
            for year in YEARS:
                uncertainties[m][year] = BTagUncertainties(year, m)
            #print
            #print "ZpBB_M{}:".format(m)
            #print
            #print "'BTag_uncertainties' : {"
            #print "\t'2016': { 'up':", uncertainties[m]['2016']["up"],","
            #print "\t\t'down':", uncertainties[m]['2016']["down"],"},"
            #print "\t'2017': { 'up':", uncertainties[m]['2017']["up"],","
            #print "\t\t'down':", uncertainties[m]['2017']["down"],"},"
            #print "\t'2018': { 'up':", uncertainties[m]['2018']["up"],","
            #print "\t\t'down':", uncertainties[m]['2018']["down"],"},"
            #print "\t}"
            #print
            
            fout.write("\t'ZpBB_M"+str(m)+"' : {\n")
            fout.write("\t\t'2016': { 'up':")
            fout.write(str(uncertainties[m]['2016']["up"]))
            fout.write( ",\n")
            fout.write("\t\t\t'down':")
            fout.write(str(uncertainties[m]['2016']["down"]))
            fout.write( "},\n")
            fout.write("\t\t'2017': { 'up':")
            fout.write(str(uncertainties[m]['2017']["up"]))
            fout.write( ",\n")
            fout.write("\t\t\t'down':")
            fout.write(str(uncertainties[m]['2017']["down"]))
            fout.write( "},\n")
            fout.write("\t\t'2018': { 'up':")
            fout.write(str(uncertainties[m]['2018']["up"]))
            fout.write(",\n")
            fout.write("\t\t\t'down':")
            fout.write(str(uncertainties[m]['2018']["down"]))
            fout.write("},\n")
            fout.write("\t\t},\n")
        fout.write("\t}\n")
    print "Saved uncertainties as BTag_uncertainties.py"
