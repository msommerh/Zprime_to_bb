#! /usr/bin/env python

print "starting package import"

import os, sys, getopt, multiprocessing
import copy, math, pickle
from array import array
from ROOT import gROOT, gSystem, gStyle, gRandom
from ROOT import TMath, TFile, TChain, TTree, TCut, TH1F, TH2F, TF1, THStack, TGraph, TGraphErrors, TGaxis
from ROOT import TStyle, TCanvas, TPad, TLegend, TLatex, TText

# Import PDF library
from ROOT import RooFit, RooRealVar, RooDataHist, RooDataSet, RooAbsData, RooAbsReal, RooAbsPdf, RooPlot, RooBinning, RooCategory, RooSimultaneous, RooArgList, RooArgSet, RooWorkspace, RooMsgService
from ROOT import RooFormulaVar, RooGenericPdf, RooGaussian, RooExponential, RooPolynomial, RooChebychev, RooBreitWigner, RooCBShape, RooExtendPdf, RooAddPdf

from rooUtils import *

import optparse

print "packages imported"

usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage)
parser.add_option("-t", "--test_run", action="store_true", default=False, dest="test")
parser.add_option("-M", "--isMC", action="store_true", default=False, dest="isMC")
parser.add_option('-y', '--year', action='store', type='string', dest='year',default='2016')
parser.add_option("-c", "--category", action="store", type="string", dest="category", default="")
parser.add_option("-b", "--btagging", action="store", type="string", dest="btagging", default="tight")
(options, args) = parser.parse_args()
gROOT.SetBatch(True) #suppress immediate graphic output
if options.test: print "performing test run on small QCD MC sample"

########## SETTINGS ##########

CARDDIR     = "datacards/"
YEAR        = options.year
ISMC        = options.isMC
BTAGGING    = options.btagging

if YEAR not in ['2016', '2017', '2018', 'run2']:
    print "unknown year:",YEAR
    sys.exit()

if BTAGGING not in ['tight', 'medium', 'loose']:
    print "unknown btagging requirement:", BTAGGING
    sys.exit()

CARDDIR = CARDDIR+BTAGGING+"/"

categories = ['bb', 'bq']

massPoints = [1000, 1200, 1400, 1600, 1800, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 7000, 8000]

########## ######## ##########

def datacards(category):

    for i, m in enumerate(massPoints):
        generate_datacard(YEAR, category, m, BTAGGING, CARDDIR+"%s_%s_M%d%s%s.txt" % (category, YEAR, m, "_MC" if ISMC else "" , "_test" if options.test else ""))


def generate_datacard(year, category, masspoint, btagging, outname):
    card  = "imax 1\n"
    card += "jmax 1\n"
    card += "kmax *\n"
    card += "-----------------------------------------------------------------------------------\n"
    card += "shapes            sig  *    signal_workspace/skimmed/{btagging}/MC_signal_{year}_{category}.root     Zprime_{year}:ZpBB_M{masspoint}\n".format(year=year, category=category, masspoint=masspoint, btagging=btagging)
    card += "shapes            bkg  *    bkg_workspace/skimmed/{btagging}/{data_type}_{year}_{category}.root    Zprime_{year}:Bkg_{category}\n".format(data_type="MC_QCD_TTbar" if ISMC else "data", year=year, category=category, btagging=btagging)
    card += "shapes            data_obs  *    bkg_workspace/skimmed/{btagging}/{data_type}_{year}_{category}.root    Zprime_{year}:data_obs\n".format(data_type="MC_QCD_TTbar" if ISMC else "data", year=year, category=category, btagging=btagging)
    card += "-----------------------------------------------------------------------------------\n"
    card += "bin               {}\n".format(category)
    card += "observation       -1\n"
    card += "-----------------------------------------------------------------------------------\n"
    card += "bin               {:20}{:20}\n".format(category, category)
    card += "process           {:20}{:20}\n".format("sig", "bkg") 
    card += "process           {:20}{:20}\n".format("0", "1")
    card += "rate              {:20}{:20}\n".format("1", "1") 
    card += "-----------------------------------------------------------------------------------\n"
    cardfile = open(outname, 'w')
    cardfile.write(card)
    cardfile.close()
    print "Datacards for mass", masspoint, "in category", category, "saved in", outname


if __name__ == "__main__":
    if options.category!='':
        datacards(options.category)
    else:
        jobs=[]
        for c in categories:
            p = multiprocessing.Process(target=datacards, args=(c,))
            jobs.append(p)
            p.start()
