#! /usr/bin/env python

import os, multiprocessing
from ROOT import TFile, TH1D
import ROOT
from root_numpy import root2array, array2hist, fill_hist
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

def BTagHists(year, mass):

    file_path = NTUPLEDIR+"MC_signal_{}_M{}.root".format(year,mass)
   
    outfile = TFile("testfile.root", "RECREATE")
    weights = {}
    histograms = {}
    for category in categories:
        selection = alias[category].format(WP=working_points[BTAGGING])
        weights[category] = root2array(file_path, treename='tree', branches=BRANCHES, selection=selection)
        histograms[category] =  TH1D(category, category, 40, 0., 6.)
        fill_hist(histograms[category], weights[category]['BTagAK4Weight_deepJet'])
        histograms[category].SetTitle(category+";BTagAK4Weight_deepJet;events")
        histograms[category].Write()
    outfile.Close()


if __name__ == "__main__":
    year = 2018
    mass = '4500'
    BTagHists(year, mass)
