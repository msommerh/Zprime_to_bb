#! /usr/bin/env python

import os, sys, getopt, multiprocessing
import copy, math, pickle
from array import array
from ROOT import gROOT, gSystem, gStyle, gRandom
from ROOT import TMath, TFile, TChain, TTree, TCut, TH1F, TH2F, THStack, TF1, TGraph, TGaxis
from ROOT import TStyle, TCanvas, TPad, TLegend, TLatex, TText

# Import PDF library and PDF diagonalizer
#gSystem.Load("PDFs/HWWLVJRooPdfs_cxx.so")
#gSystem.Load("PDFs/PdfDiagonalizer_cc.so")

from ROOT import RooFit, RooRealVar, RooDataHist, RooDataSet, RooAbsData, RooAbsReal, RooAbsPdf, RooPlot, RooBinning, RooCategory, RooSimultaneous, RooArgList, RooArgSet, RooWorkspace, RooMsgService
from ROOT import RooFormulaVar, RooGenericPdf, RooGaussian, RooExponential, RooPolynomial, RooChebychev, RooBreitWigner, RooCBShape, RooExtendPdf, RooAddPdf, RooProdPdf, RooNumConvPdf, RooFFTConvPdf
#from ROOT import PdfDiagonalizer, RooAlphaExp, RooErfExpPdf, Roo2ExpPdf, RooAlpha42ExpPdf, RooExpNPdf, RooAlpha4ExpNPdf, RooExpTailPdf, RooAlpha4ExpTailPdf, RooAlpha, #RooDoubleCrystalBall #RooPowerLaw
from ROOT import TMatrixDSym, TMatrixDSymEigen, RooAddition, RooCustomizer, RooFitResult


from rooUtils import *
#from selections import selection
#from xsections import xsection
#from samples import sample

#import optparse
#usage = "usage: %prog [options]"
#parser = optparse.OptionParser(usage)
#parser.add_option("-a", "--all", action="store_true", default=False, dest="all")
#parser.add_option("-b", "--bash", action="store_true", default=False, dest="bash")
#parser.add_option("-c", "--channel", action="store", type="string", dest="channel", default="")
#parser.add_option("-d", "--different", action="store_true", default=False, dest="different")
#parser.add_option("-e", "--extrapolate", action="store_true", default=False, dest="extrapolate")
#parser.add_option("-p", "--parallelize", action="store_true", default=False, dest="parallelize")
#parser.add_option("-s", "--scan", action="store_true", default=False, dest="scan")
#parser.add_option("-x", "--dijet", action="store_true", default=False, dest="dijet")
#parser.add_option("-v", "--verbose", action="store_true", default=False, dest="verbose")
#(options, args) = parser.parse_args()
#if options.bash: gROOT.SetBatch(True)

########## SETTINGS ##########

# Silent RooFit
RooMsgService.instance().setGlobalKillBelow(RooFit.FATAL)

#gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)
gStyle.SetPadTopMargin(0.06)
gStyle.SetPadRightMargin(0.05)
gStyle.SetErrorX(0.)

#ALTERNATIVE = options.different
#EXTRAPOLATE = options.extrapolate
#SCAN        = options.scan
#DIJET       = options.dijet
ALTERNATIVE = False
EXTRAPOLATE = False
SCAN        = False
DIJET       = False
VERBOSE     = False

NTUPLEDIR   = "/scratch/zucchett/Ntuple/VH/"
#PLOTDIR     = "plotsAlpha/" if not EXTRAPOLATE else "plotsAlphaExt/"
PLOTDIR     = "plots/"
CARDDIR     = "datacards/"
WORKDIR     = "workspace/"
RATIO       = 4
LUMI        = 35867
BLIND       = False if not EXTRAPOLATE else False
REGENERATE  = False
PREFIX      = "CMS2016_"
#VERBOSE     = options.verbose
#PARALLELIZE = options.parallelize

channelList = ['nnb', 'nnbb', 'enb', 'enbb', 'mnb', 'mnbb', 'eeb', 'mmb', 'eebb', 'mmbb']
signalList = ['XWH', 'XZH', 'XVH']

genPoints = [600, 800, 1000, 1200, 1400, 1600, 1800, 2000, 2500, 3000, 3500, 4000, 4500]
massPoints = [x for x in range(800, 4500+1, 100)] #if not HVTMODEL else genPoints

LOWMIN = 30.
LOWMAX = 65. if not EXTRAPOLATE else 50. #65.
LOWINT = 85.
SIGMIN = 105. if not EXTRAPOLATE else 50. #65.
SIGMAX = 135. if not EXTRAPOLATE else 65. #105.

HIGMIN = 135.
HIGMAX = 250.

XBINMIN= 750.
XBINMAX= 4750.
XBINS  = 80

XTBINMIN = 750.
XTBINMAX= 4750.
XTBINS  = 80

# inclusive top SF
topSF = {
    'nnb'   : [1.017, 0.045, 0.029],
    'nnbb'  : [1.050, 0.097, 0.029],
    'enb'   : [0.911, 0.017, 0.029],
    'enbb'  : [0.940, 0.038, 0.029],
    'mnb'   : [0.891, 0.015, 0.029],
    'mnbb'  : [0.848, 0.032, 0.029],
    'emb'   : [0.940, 0.061, 0.040],
    'embb'  : [1.029, 0.169, 0.040],
    'eeb'   : [0.940, 0.061, 0.040],
    'eebb'  : [1.029, 0.169, 0.040],
    'mmb'   : [0.940, 0.061, 0.040],
    'mmbb'  : [1.029, 0.169, 0.040],
}

vvSF = [1.000, 0.229]

functions = {
    "nnb"  : {"Vjet" : "POL5", "VjetAlt" : "EXPGAUS", "Top" : "GAUS3", "VV" : "EXPGAUS3",  "Shape" : "EXPN", "ShapeAlt" : "EXPTAIL"},
    "nnbb" : {"Vjet" : "POL5", "VjetAlt" : "EXPGAUS", "Top" : "GAUS2", "VV" : "EXPGAUS3",  "Shape" : "EXPN", "ShapeAlt" : "EXPTAIL"},
    "enb"  : {"Vjet" : "POL4", "VjetAlt" : "EXPGAUS", "Top" : "GAUS3", "VV" : "EXPGAUS2",  "Shape" : "EXPN", "ShapeAlt" : "EXPTAIL"},
    "enbb" : {"Vjet" : "POL4", "VjetAlt" : "EXPGAUS", "Top" : "GAUS3", "VV" : "EXPGAUS2",  "Shape" : "EXPN", "ShapeAlt" : "EXPTAIL"},
    "mnb"  : {"Vjet" : "POL4", "VjetAlt" : "EXPGAUS", "Top" : "GAUS3", "VV" : "EXPGAUS2",  "Shape" : "EXPN", "ShapeAlt" : "EXPTAIL"},
    "mnbb" : {"Vjet" : "POL4", "VjetAlt" : "EXPGAUS", "Top" : "GAUS3", "VV" : "EXPGAUS2",  "Shape" : "EXPN", "ShapeAlt" : "EXPTAIL"},
    "eeb"  : {"Vjet" : "POL3", "VjetAlt" : "EXPGAUS", "Top" : "GAUS2",  "VV" : "EXPGAUS3",  "Shape" : "EXPN", "ShapeAlt" : "EXPTAIL"},
    "eebb" : {"Vjet" : "POL3", "VjetAlt" : "EXP",     "Top" : "GAUS2",  "VV" : "EXPGAUS3",  "Shape" : "EXPN", "ShapeAlt" : "EXPTAIL"},
    "mmb"  : {"Vjet" : "POL3", "VjetAlt" : "EXPGAUS", "Top" : "GAUS2",  "VV" : "EXPGAUS3",  "Shape" : "EXPN", "ShapeAlt" : "EXPTAIL"},
    "mmbb" : {"Vjet" : "POL3", "VjetAlt" : "EXP",     "Top" : "GAUS2",  "VV" : "EXPGAUS3",  "Shape" : "EXPN", "ShapeAlt" : "EXPTAIL"},
}



########## ######## ##########


#def alpha(channel):
#    if channel.startswith('X'):
#        stype = channel[:3] if channel.startswith('X') else 'XVH'
#        category = channel[3:] if channel.startswith('X') else channel
#    else:
#        stype, category = 'XVH', channel
#        channel = stype+category
#    nElec = channel.count('e')
#    nMuon = channel.count('m')
#    nLept = nElec + nMuon
#    nBtag = channel.count('b')
#
#    print "--- Channel", channel, "---"
#    print "  number of electrons:", nElec, " muons:", nMuon, " b-tags:", nBtag
#    print "  signal name:", stype
#
#    if ALTERNATIVE: print "  using ALTERNATIVE fit functions"
#    if EXTRAPOLATE: print "  using VALIDATION mode"
#    if DIJET:       print "  using BUMP HUNT background estimation"
#    print "-"*11*2
#
#    #*******************************************************#
#    #                                                       #
#    #              Variables and selections                 #
#    #                                                       #
#    #*******************************************************#
#
#    # Define all the variables from the trees that will be used in the cuts and fits
#    # this steps actually perform a "projection" of the entire tree on the variables in thei ranges, so be careful once setting the limits
#
#    X_mass = RooRealVar(  "VH_mass",    "m_{VH}",       XBINMIN, XBINMAX, "GeV")
#    J_mass = RooRealVar(  "H_mass",   "jet mass",        LOWMIN, HIGMAX, "GeV")
#    V_mass = RooRealVar(  "V_mass", "V jet mass",           -9.,  1.e6, "GeV")
#    CSV1    = RooRealVar( "H_csv1",           "",         -999.,     2.     )
#    CSV2    = RooRealVar( "H_csv2",           "",         -999.,     2.     )
#    H_ntag  = RooRealVar( "H_ntag",           "",           -9.,     9.     )
#    H_dbt   = RooRealVar( "H_dbt",            "",           -2.,     2.     )
#    H_tau21 = RooRealVar( "H_tau21",          "",           -9.,     2.     )
#    V_tau21 = RooRealVar( "V_tau21",          "",           -9.,     2.     )
#    V_dbt   = RooRealVar( "V_dbt",            "",           -2.,     2.     )
#    MaxBTag = RooRealVar( "MaxBTag",          "",          -10.,     2.     )
#    MinDPhi = RooRealVar( "MinDPhi",          "",           -1.,    99.     )
#    DEta    = RooRealVar( "DEta",             "",           -1.,    99.     )
#    nTaus   = RooRealVar( "nTaus",            "",           -1.,    99.     )
#    Vpt     = RooRealVar( "V.Pt()",           "",           -1.,   1.e6     )
#    CosThetaStar = RooRealVar( "CosThetaStar","",          -99.,    99.     )
#    CosTheta1 = RooRealVar( "CosTheta1",      "",          -99.,    99.     )
#    nTaus   = RooRealVar( "nTaus",            "",           -1.,    99.     )
#    TopVeto = RooRealVar( "isTveto",          "",            0.,     2.     )
#    isZtoNN = RooRealVar( "isZtoNN",          "",            0.,     2.     )
#    isWtoEN = RooRealVar( "isWtoEN",          "",            0.,     2.     )
#    isWtoMN = RooRealVar( "isWtoMN",          "",            0.,     2.     )
#    isZtoEE = RooRealVar( "isZtoEE",          "",            0.,     2.     )
#    isZtoMM = RooRealVar( "isZtoMM",          "",            0.,     2.     )
#    isVtoQQ = RooRealVar( "isVtoQQ",          "",            0.,     2.     )
#    weight  = RooRealVar( "eventWeightLumi",  "",         -1.e9,   1.e9     )
#
#    if nLept==0: X_mass.SetTitle("m^{T}_{VH}")
#
#    # Define the RooArgSet which will include all the variables defined before
#    # there is a maximum of 9 variables in the declaration, so the others need to be added with 'add'
#    variables = RooArgSet(X_mass, J_mass, V_mass, CSV1, CSV2, H_ntag, H_dbt, H_tau21, V_tau21)
#    variables.add(RooArgSet(DEta, MaxBTag, MinDPhi, nTaus, CosThetaStar, CosTheta1, Vpt))
#    variables.add(RooArgSet(TopVeto, isZtoNN, isWtoEN, isWtoMN, isZtoEE, isZtoMM, isVtoQQ, weight))
#
#    # define binning
#    Jbins = int(J_mass.getMax() - J_mass.getMin())
#    Xbins = int(X_mass.getMax() - X_mass.getMin())
##    if nLept==0: Xbins /= 2
#
#    # set reasonable ranges for J_mass and X_mass
#    # these are used in the fit in order to avoid ROOFIT to look in regions very far away from where we are fitting
#    # (honestly, it is not clear to me why it is necessary, but without them the fit often explodes)
#    X_mass.setRange("X_reasonable_range", X_mass.getMin(), X_mass.getMax())
#    J_mass.setRange("h_reasonable_range", J_mass.getMin(), J_mass.getMax())
#    J_mass.setRange("h_extended_reasonable_range", 0, J_mass.getMax())
#
#    # Define the ranges in fatJetMass - these will be used to define SB and SR
#    J_mass.setRange("LSBrange", LOWMIN, LOWMAX)
#    J_mass.setRange("HSBrange", HIGMIN, HIGMAX)
#    J_mass.setRange("VRrange",  LOWMAX, SIGMIN)
#    J_mass.setRange("SRrange",  SIGMIN, SIGMAX)
#
#    # Set binning for plots
#    J_mass.setBins(Jbins)
#    X_mass.setBins(Xbins/10)
#
#    # Set RooArgSets once for all, see https://root.cern.ch/phpBB3/viewtopic.php?t=11758
#    jetMassArg = RooArgSet(J_mass)
#
#    baseCut = selection[category] #getCut(channel)
#
#    # Cuts
#    SRcut  = baseCut + " && %s>%d && %s<%d" % (J_mass.GetName(), SIGMIN, J_mass.GetName(), SIGMAX)
#    LSBcut = baseCut + " && %s>%d && %s<%d" % (J_mass.GetName(), LOWMIN, J_mass.GetName(), LOWMAX)
#    HSBcut = baseCut + " && %s>%d && %s<%d" % (J_mass.GetName(), HIGMIN, J_mass.GetName(), HIGMAX)
#    SBcut  = baseCut + " && ((%s>%d && %s<%d) || (%s>%d && %s<%d))" % (J_mass.GetName(), LOWMIN, J_mass.GetName(), LOWMAX, J_mass.GetName(), HIGMIN, J_mass.GetName(), HIGMAX)
#    VRcut  = baseCut + " && %s>%d && %s<%d" % (J_mass.GetName(), LOWMAX, J_mass.GetName(), SIGMIN)
#
#    print "  SR cut\t:", SRcut
#    print "  LSB cut\t:", LSBcut
#    print "  HSB cut\t:", HSBcut
#    print "  SB cut\t:", SBcut
#    print "-"*11*2
#
#    # Binning
#    binsJmass = RooBinning(Jbins/5, J_mass.getMin(), J_mass.getMax())
#    #binsJmass.addUniform(Jbins/5, J_mass.getMin(), J_mass.getMax())
#    J_mass.setBinning(binsJmass, "PLOT")
#
#    binsXmass = RooBinning(Xbins/100, X_mass.getMin(), X_mass.getMax())
#    #binsXmass.addUniform(Xbins, X_mass.getMin(), X_mass.getMax())
#    X_mass.setBinning(binsXmass, "PLOT")
#
#    #*******************************************************#
#    #                                                       #
#    #                      Input files                      #
#    #                                                       #
#    #*******************************************************#
#
#    # Import the files using TChains (separately for the bkg "classes" that we want to describe: here DY and VV+ST+TT)
#    treeData = TChain("tree")
#    treeVjet = TChain("tree")
#    treeTop  = TChain("tree")
#    treeVV   = TChain("tree")
#
#    # Read data
#    pd = []
#    if nMuon: pd += [x for x in sample['data_obs']['files'] if 'SingleMuon' in x or 'MET' in x]
#    elif nElec: pd += [x for x in sample['data_obs']['files'] if 'SingleElectron' in x or 'MET' in x]
#    elif nLept==0: pd += [x for x in sample['data_obs']['files'] if 'MET' in x]
#    elif len(pd)==0: raw_input("Warning: Primary Dataset not recognized, continue?")
#    print "  Primary dataset:", pd
#    print "-"*11*2
#    print "  Read rootfiles and import trees"
#    for i, s in enumerate(pd): treeData.Add(NTUPLEDIR + s + ".root")
#
#    # Read V+jets backgrounds
#    for i, s in enumerate(["WJetsToLNu_HT", "DYJetsToNuNu_HT", "DYJetsToLL_HT"]):
#        for j, ss in enumerate(sample[s]['files']): treeVjet.Add(NTUPLEDIR + ss + ".root")
#
#    # Read Top backgrounds
#    for i, s in enumerate(["ST", "TTbarSL"]):
#        for j, ss in enumerate(sample[s]['files']): treeTop.Add(NTUPLEDIR + ss + ".root")
#
#    # Read VV backgrounds
#    for i, s in enumerate(["VV"]):
#        for j, ss in enumerate(sample[s]['files']): treeVV.Add(NTUPLEDIR + ss + ".root")
#
#    print "  Create datasets:",
#    print "Data",
#    # create a dataset to host data in sideband (using this dataset we are automatically blind in the SR!)
#    setDataSB = RooDataSet("setDataSB", "setDataSB", variables, RooFit.Cut(SBcut), RooFit.WeightVar(weight), RooFit.Import(treeData))
#    setDataLSB = RooDataSet("setDataLSB", "setDataLSB", variables, RooFit.Import(setDataSB), RooFit.Cut(LSBcut), RooFit.WeightVar(weight))
#    setDataHSB = RooDataSet("setDataHSB", "setDataHSB", variables, RooFit.Import(setDataSB), RooFit.Cut(HSBcut), RooFit.WeightVar(weight))
#
#    # Observed data (WARNING, BLIND!)
#    setDataSR = RooDataSet("setDataSR", "setDataSR", variables, RooFit.Cut(SRcut), RooFit.WeightVar(weight), RooFit.Import(treeData))
#    setDataVR = RooDataSet("setDataVR", "setDataVR", variables, RooFit.Cut(VRcut), RooFit.WeightVar(weight), RooFit.Import(treeData)) # Observed in the VV mass, just for plotting purposes
#
#    setDataSRSB = RooDataSet("setDataSRSB", "setDataSRSB", variables, RooFit.Cut("("+SRcut+") || ("+SBcut+")"), RooFit.WeightVar(weight), RooFit.Import(treeData))
#    setDataSRSBVR = RooDataSet("setDataSRSBVR", "setDataSRSBVR", variables, RooFit.Cut("("+SRcut+") || ("+SBcut+") || ("+VRcut+")"), RooFit.WeightVar(weight), RooFit.Import(treeData))
#
#    # same for the bkg datasets from MC, where we just apply the base selections (not blind)
#    print "Vjet",
#    setVjet = RooDataSet("setVjet", "setVjet", variables, RooFit.Cut(baseCut), RooFit.WeightVar(weight), RooFit.Import(treeVjet))
#    setVjetSB = RooDataSet("setVjetSB", "setVjetSB", variables, RooFit.Import(setVjet), RooFit.Cut(SBcut), RooFit.WeightVar(weight))
#    setVjetSR = RooDataSet("setVjetSR", "setVjetSR", variables, RooFit.Import(setVjet), RooFit.Cut(SRcut), RooFit.WeightVar(weight))
#    print "Top",
#    setTop = RooDataSet("setTop", "setTop", variables, RooFit.Cut(baseCut), RooFit.WeightVar(weight), RooFit.Import(treeTop))
#    setTopSB = RooDataSet("setTopSB", "setTopSB", variables, RooFit.Import(setTop), RooFit.Cut(SBcut), RooFit.WeightVar(weight))
#    setTopSR = RooDataSet("setTopSR", "setTopSR", variables, RooFit.Import(setTop), RooFit.Cut(SRcut), RooFit.WeightVar(weight))
#    print "VV."
#    setVV = RooDataSet("setVV", "setVV", variables, RooFit.Cut(baseCut), RooFit.WeightVar(weight), RooFit.Import(treeVV))
#    setVVSB = RooDataSet("setVVSB", "setVVSB", variables, RooFit.Import(setVV), RooFit.Cut(SBcut), RooFit.WeightVar(weight))
#    setVVSR = RooDataSet("setVVSR", "setVVSR", variables, RooFit.Import(setVV), RooFit.Cut(SRcut), RooFit.WeightVar(weight))
#
#    print "  Data events SB: %.2f" % setDataSB.sumEntries()
#    print "  V+jets entries: %.2f" % setVjetSB.sumEntries()
#    print "  Top,ST entries: %.2f" % setTopSB.sumEntries()
#    print "  VV, VH entries: %.2f" % setVVSB.sumEntries()
#
#    nVjet = RooRealVar("nVjet", "Vjet normalization", setVjet.sumEntries(), 0., 1.e6)
#    nVjet2 = RooRealVar("nVjet2", "Vjet2 normalization", setVjet.sumEntries(), 0., 1.e6)
#    nTop  = RooRealVar("nTop", "Top normalization",  setTop.sumEntries(),  0., 1.e6)
#    nVV   = RooRealVar("nVV",  "VV normalization",   setVV.sumEntries(),   0., 1.e6)
#
#    # Apply Top SF
#    nTop.setVal(nTop.getVal()*topSF[category][0])
#    nTop.setError(nTop.getVal()*topSF[category][1])
#
#    nTop2 = RooRealVar("nTop2", "Top2 normalization",  nTop.getVal(),  0., 1.e6)
#    nTop2.setError(nTop.getError())
#
#    # Define entries
#    entryVjet = RooRealVar("entryVjets",  "V+jets normalization", setVjet.sumEntries(), 0., 1.e6)
#    entryTop = RooRealVar("entryTop",  "Top normalization", setTop.sumEntries(), 0., 1.e6)
#    entryVV = RooRealVar("entryVV",  "VV normalization", setVV.sumEntries(), 0., 1.e6)
#    entryVjetSB = RooRealVar("entryVjetsSB",  "V+jets normalization", setVjet.sumEntries(SBcut), 0., 1.e6)
#    entryTopSB = RooRealVar("entryTopSB",  "Top normalization", setTop.sumEntries(SBcut), 0., 1.e6)
#    entryVVSB = RooRealVar("entryVVSB",  "VV normalization", setVV.sumEntries(SBcut), 0., 1.e6)
#
#    entrySB = RooRealVar("entrySB",  "Data SB normalization", setDataSB.sumEntries(SBcut), 0., 1.e6)
#    entrySB.setError(math.sqrt(entrySB.getVal()))
#
#    entryLSB = RooRealVar("entryLSB",  "Data LSB normalization", setDataSB.sumEntries(LSBcut), 0., 1.e6)
#    entryLSB.setError(math.sqrt(entryLSB.getVal()))
#
#    entryHSB = RooRealVar("entryHSB",  "Data HSB normalization", setDataSB.sumEntries(HSBcut), 0., 1.e6)
#    entryHSB.setError(math.sqrt(entryHSB.getVal()))
#
#    ###################################################################################
#    #        _   _                                                                    #
#    #       | \ | |                          | (_)         | | (_)                    #
#    #       |  \| | ___  _ __ _ __ ___   __ _| |_ ___  __ _| |_ _  ___  _ __          #
#    #       | . ` |/ _ \| '__| '_ ` _ \ / _` | | / __|/ _` | __| |/ _ \| '_ \         #
#    #       | |\  | (_) | |  | | | | | | (_| | | \__ \ (_| | |_| | (_) | | | |        #
#    #       |_| \_|\___/|_|  |_| |_| |_|\__,_|_|_|___/\__,_|\__|_|\___/|_| |_|        #
#    #                                                                                 #
#    ###################################################################################
#    # fancy ASCII art thanks to, I guess, Jose
#
#    # start by creating the fit models to get the normalization:
#    # * MAIN and SECONDARY bkg are taken from MC by fitting the whole J_mass range
#    # * The two PDFs are added together using the relative normalizations of the two bkg from MC
#    # * DATA is then fit in the sidebands only using the combined bkg PDF
#    # * The results of the fit are then estrapolated in the SR and the integral is evaluated.
#    # * This defines the bkg normalization in the SR
#
#    #*******************************************************#
#    #                                                       #
#    #                 V+jets normalization                  #
#    #                                                       #
#    #*******************************************************#
#
#    # Variables for V+jets
#    constVjet   = RooRealVar("constVjet",   "slope of the exp",      -0.020, -1.,   0.)
#    offsetVjet  = RooRealVar("offsetVjet",  "offset of the erf",     30.,   -50., 400.)
#    widthVjet   = RooRealVar("widthVjet",   "width of the erf",     50.,    10., 200.) #0, 400
#    expVjet     = RooExponential("expVjet", "exp for Vjet modeling", J_mass, constVjet)
#    a0Vjet = RooRealVar("a0Vjet", "par 0 for poly", -1.25, -5, 0)
#    a1Vjet = RooRealVar("a1Vjet", "par 1 for poly", 0.25,  0, 5)
#    a2Vjet = RooRealVar("a2Vjet", "par 2 for poly", 0.04, -1, 1)
#    a3Vjet = RooRealVar("a3Vjet", "par 3 for poly", -0.04, -1, 1)
#    a4Vjet = RooRealVar("a4Vjet", "par 3 for poly", 0.04, -100, 100)
#    polVjet = RooChebychev("polVjet", "polynomial", J_mass, RooArgList(a0Vjet, a1Vjet, a2Vjet))
#    p0Vjet = RooRealVar("p0Vjet", "par 0 for power", -12., -40, 0)
#    p1Vjet = RooRealVar("p1Vjet", "par 1 for power", 500., 10, 1000)
#    powVjet = RooGenericPdf("powVjet", "power law", "pow(@0 + @2, @1)", RooArgList(J_mass, p0Vjet, p1Vjet))
#    meanVjet    = RooRealVar("meanVjet",     "mean of the gaussian", 100., 0., 200.)
#    sigmaVjet   = RooRealVar("sigmaVjet",    "sigma of the gaussian", 50., 20., 200.)
#    fracVjet    = RooRealVar("fracVjet",    "fraction of gaussian wrt exp", 0.1, 0.,  1.)
#    gausVjet    = RooGaussian("gausVjet",    "gaus for W jet mass", J_mass, meanVjet, sigmaVjet)
#
##    if channel=="XZHnnb":
##        offsetVjet  = RooRealVar("offsetVjet",  "offset of the erf",     200.,   0., 1000.)
##    if channel=="XZHnnbb":
##        offsetVjet  = RooRealVar("offsetVjet",  "offset of the erf",     350.,   200., 500.)
###    if channel == "XWHenb" or channel == "XZHeeb":
###        offsetVjet.setVal(120.)
###        offsetVjet.setConstant(True)
##    if channel == "XWHenbb":
##        a0Vjet = RooRealVar("a0Vjet", "width of the erf", -1.5, -5, 0)
##        a1Vjet = RooRealVar("a1Vjet", "width of the erf", 0.6,  0., 10)
##        a2Vjet = RooRealVar("a2Vjet", "width of the erf", -0.12, -1, -0.0001)
##    if channel == "XWHmnbb":
##        a0Vjet = RooRealVar("a0Vjet", "width of the erf", -1.5, -5, 0)
##        a1Vjet = RooRealVar("a1Vjet", "width of the erf", 0.7,  0., 10)
##        a2Vjet = RooRealVar("a2Vjet", "width of the erf", -0.12, -1, -0.0001)
##    if channel == "XWHenb":
##        offsetVjet  = RooRealVar("offsetVjet",  "offset of the erf",    120.,  80., 155.)
##    if channel == "XWHenbb" or channel == "XZHmmb":
##        offsetVjet  = RooRealVar("offsetVjet",  "offset of the erf",     67.,   50., 100.)
##    if channel == "XWHmnb":
##        offsetVjet  = RooRealVar("offsetVjet",  "offset of the erf",    30.,   -50., 600.)
##    if channel == "XZHeeb":
##        offsetVjet.setMin(-400)
##        offsetVjet.setVal(0.)
##        offsetVjet.setMax(1000)
##        widthVjet.setVal(1.)
#
#    # Define V+jets model
#    if functions[category]["Vjet"] == "ERFEXP": VjetMass = RooErfExpPdf("VjetMass", functions[category]["Vjet"], J_mass, constVjet, offsetVjet, widthVjet)
#    elif functions[category]["Vjet"] == "EXP": VjetMass = RooExponential("VjetMass", functions[category]["Vjet"], J_mass, constVjet)
#    elif functions[category]["Vjet"] == "GAUS": VjetMass = RooGaussian("VjetMass", functions[category]["Vjet"], J_mass, offsetVjet, widthVjet)
#    elif functions[category]["Vjet"] == "POL2": VjetMass = RooChebychev("VjetMass", functions[category]["Vjet"], J_mass, RooArgList(a0Vjet, a1Vjet))
#    elif functions[category]["Vjet"] == "POL3": VjetMass = RooChebychev("VjetMass", functions[category]["Vjet"], J_mass, RooArgList(a0Vjet, a1Vjet, a2Vjet))
#    elif functions[category]["Vjet"] == "POL4": VjetMass = RooChebychev("VjetMass", functions[category]["Vjet"], J_mass, RooArgList(a0Vjet, a1Vjet, a2Vjet, a3Vjet))
#    elif functions[category]["Vjet"] == "POL5": VjetMass = RooChebychev("VjetMass", functions[category]["Vjet"], J_mass, RooArgList(a0Vjet, a1Vjet, a2Vjet, a3Vjet, a4Vjet))
#    elif functions[category]["Vjet"] == "POW": VjetMass = RooGenericPdf("VjetMass", functions[category]["Vjet"], "pow(@0 + @2, @1)", RooArgList(J_mass, p0Vjet, p1Vjet))
#    elif functions[category]["Vjet"] == "EXPGAUS": VjetMass = RooAddPdf("VjetMass", functions[category]["Vjet"], RooArgList(expVjet, gausVjet), RooArgList(fracVjet))
#    elif functions[category]["Vjet"] == "POLGAUS": VjetMass = RooAddPdf("VjetMass", functions[category]["Vjet"], RooArgList(polVjet, gausVjet), RooArgList(fracVjet))
#    elif functions[category]["Vjet"] == "POWGAUS": VjetMass = RooAddPdf("VjetMass", functions[category]["Vjet"], RooArgList(powVjet, gausVjet), RooArgList(fracVjet))
#    else:
#        print "  ERROR! Pdf", functions[category]["Vjet"], "is not implemented for Vjets"
#        exit()
#
#    if functions[category]["VjetAlt"] == "POL2": VjetMass2 = RooChebychev("VjetMass2", functions[category]["VjetAlt"], J_mass, RooArgList(a0Vjet, a1Vjet))
#    elif functions[category]["VjetAlt"] == "POL3": VjetMass2 = RooChebychev("VjetMass2", functions[category]["VjetAlt"], J_mass, RooArgList(a0Vjet, a1Vjet, a2Vjet))
#    elif functions[category]["VjetAlt"] == "POL4": VjetMass2 = RooChebychev("VjetMass2", functions[category]["VjetAlt"], J_mass, RooArgList(a0Vjet, a1Vjet, a2Vjet, a3Vjet))
#    elif functions[category]["VjetAlt"] == "POL5": VjetMass2 = RooChebychev("VjetMass2", functions[category]["VjetAlt"], J_mass, RooArgList(a0Vjet, a1Vjet, a2Vjet, a3Vjet, a4Vjet))
#    elif functions[category]["VjetAlt"] == "POW": VjetMass2 = RooGenericPdf("VjetMass2", functions[category]["VjetAlt"], "pow(@0 + @2, @1)", RooArgList(J_mass, p0Vjet, p1Vjet))
#    elif functions[category]["VjetAlt"] == "EXP": VjetMass2 = RooExponential("VjetMass2", functions[category]["VjetAlt"], J_mass, constVjet)
#    elif functions[category]["VjetAlt"] == "ERFEXP": VjetMass2 = RooErfExpPdf("VjetMass2", functions[category]["VjetAlt"], J_mass, constVjet, offsetVjet, widthVjet)
#    elif functions[category]["VjetAlt"] == "EXPGAUS": VjetMass2 = RooAddPdf("VjetMass2",   functions[category]["VjetAlt"], RooArgList(expVjet, gausVjet), RooArgList(fracVjet))
#    else:
#        print "  ERROR! Pdf", functions[category]["VjetAlt"], "is not implemented for Vjets"
#        exit()
#
#    # fit to main bkg in MC (whole range)
#    frVjet = VjetMass.fitTo(setVjet, RooFit.SumW2Error(True), RooFit.Range("h_reasonable_range"), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Save(1), RooFit.PrintLevel(-1))
#    frVjet2 = VjetMass2.fitTo(setVjet, RooFit.SumW2Error(True), RooFit.Range("h_reasonable_range"), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Save(1), RooFit.PrintLevel(-1))
#    if VERBOSE: print "********** Fit result [JET MASS Vjets] *", category, "*"*40, "\n", frVjet.Print(), "\n", "*"*80
#    drawPlot("VjetMass", category, J_mass, VjetMass, setVjet, [frVjet], -1, None, "", VjetMass2 if ALTERNATIVE else None)
#
#    #likelihoodScan(VjetMass, setVjet, [constVjet, offsetVjet, widthVjet])
#
#
#    #*******************************************************#
#    #                                                       #
#    #                 Top, ST normalization                 #
#    #                                                       #
#    #*******************************************************#
#
#    # Variables for Top
#    # Error Function * Exponential to model the bulk
#    constTop  = RooRealVar("constTop",  "slope of the exp", -0.045,   -0.1,   0.)
#    offsetTop = RooRealVar("offsetTop", "offset of the erf", 100.0,   80., 250.)
#    widthTop  = RooRealVar("widthTop",  "width of the erf",  50.0,    1., 100.)
#    gausTop   = RooGaussian("baseTop",  "gaus for Top jet mass", J_mass, offsetTop, widthTop)
#    erfrTop   = RooErfExpPdf("baseTop", "error function for Top jet mass", J_mass, constTop, offsetTop, widthTop)
#    # gaussian for the W mass peak
#    meanW     = RooRealVar("meanW",     "mean of the gaussian",           80.2, 70., 90.)
#    sigmaW    = RooRealVar("sigmaW",    "sigma of the gaussian",          80.2*0.10,  6., 15.)
#    fracW     = RooRealVar("fracW",     "fraction of gaussian wrt erfexp", 0.12, 0.001,  0.3)
#    gausW     = RooGaussian("gausW",    "gaus for W jet mass", J_mass, meanW, sigmaW)
#    # gaussian for the Top mass peak
#    meanT     = RooRealVar("meanT",     "mean of the gaussian",           171., 160., 180.)
#    sigmaT    = RooRealVar("sigmaT",    "sigma of the gaussian",           12.,   5.,  20.)
#    fracT     = RooRealVar("fracT",     "fraction of gaussian wrt erfexp",  0.1,  0.,   0.4)
#    gausT     = RooGaussian("gausT",    "gaus for T jet mass", J_mass, meanT, sigmaT)
#
#    if not nLept==1:
#        meanW.setConstant(True)
#        sigmaW.setConstant(True)
#        meanT.setConstant(True)
#        sigmaT.setConstant(True)
##    if channel=="XZHeeb" or channel=="XZHeebb" or channel=="XZHmmb" or channel=="XZHmmbb":
##        offsetTop = RooRealVar("offsetTop", "offset of the erf", 200.0,   -50., 450.)
##        widthTop  = RooRealVar("widthTop",  "width of the erf",  100.0,    1., 1000.)
#
#    # Define Top model
#    if functions[category]["Top"] == "ERFEXPGAUS2": TopMass = RooAddPdf("TopMass",   functions[category]["Top"], RooArgList(gausW, gausT, erfrTop), RooArgList(fracW, fracT))
#    elif functions[category]["Top"] == "ERFEXPGAUS": TopMass = RooAddPdf("TopMass",   functions[category]["Top"], RooArgList(gausT, erfrTop), RooArgList(fracT))
#    elif functions[category]["Top"] == "GAUS3": TopMass  = RooAddPdf("TopMass",   functions[category]["Top"], RooArgList(gausW, gausT, gausTop), RooArgList(fracW, fracT))
#    elif functions[category]["Top"] == "GAUS2": TopMass  = RooAddPdf("TopMass",   functions[category]["Top"], RooArgList(gausT, gausTop), RooArgList(fracT))
#    elif functions[category]["Top"] == "GAUS": TopMass  = RooGaussian("TopMass", functions[category]["Top"], J_mass, offsetTop, widthTop)
#    else:
#        print "  ERROR! Pdf", functions[category]["Top"], "is not implemented for Top"
#        exit()
#
#    # fit to secondary bkg in MC (whole range)
#    frTop = TopMass.fitTo(setTop, RooFit.SumW2Error(True), RooFit.Range("h_reasonable_range"), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Save(1), RooFit.PrintLevel(-1))
#    if VERBOSE: print "********** Fit result [JET MASS TOP] ***", category, "*"*40, "\n", frTop.Print(), "\n", "*"*80
#    drawPlot("TopMass", category, J_mass, TopMass, setTop, [frTop])
#
#    #likelihoodScan(TopMass, setTop, [offsetTop, widthTop])
#
#
#    #*******************************************************#
#    #                                                       #
#    #                 VV, VH normalization                  #
#    #                                                       #
#    #*******************************************************#
#
#    # Variables for VV
#    # Error function and exponential to model the bulk
#    constVV  = RooRealVar("constVV",  "slope of the exp",  -0.030, -0.1,   0.)
#    offsetVV = RooRealVar("offsetVV", "offset of the erf", 90.,     1., 300.)
#    widthVV  = RooRealVar("widthVV",  "width of the erf",  50.,     1., 100.)
#    erfrVV   = RooErfExpPdf("baseVV", "error function for VV jet mass", J_mass, constVV, offsetVV, widthVV)
#    expoVV   = RooExponential("baseVV", "error function for VV jet mass", J_mass, constVV)
#    # gaussian for the W mass peak
#    meanVW    = RooRealVar("meanVW",   "mean of the gaussian",           80.2,    60., 100.)
#    sigmaVW   = RooRealVar("sigmaVW",  "sigma of the gaussian",          80.2*0.10,     6.,  30.)
#    fracVW    = RooRealVar("fracVW",   "fraction of gaussian wrt erfexp", 3.2e-1, 0.,   1.)
#    gausVW   = RooGaussian("gausVW",   "gaus for W jet mass", J_mass, meanVW, sigmaVW)
#    # gaussian for the Z mass peak
#    meanVZ    = RooRealVar("meanVZ",   "mean of the gaussian",           91.2,    60., 100.)
#    sigmaVZ   = RooRealVar("sigmaVZ",  "sigma of the gaussian",          91.2*0.10,     6.,  30.)
#    fracVZ    = RooRealVar("fracVZ",   "fraction of gaussian wrt erfexp", 3.2e-1, 0.,   1.)
#    gausVZ   = RooGaussian("gausVZ",   "gaus for Z jet mass", J_mass, meanVZ, sigmaVZ)
#    # gaussian for the H mass peak
#    meanVH    = RooRealVar("meanVH",   "mean of the gaussian",           125.,   100., 150.)
#    sigmaVH   = RooRealVar("sigmaVH",  "sigma of the gaussian",          125.*0.10,     5.,  50.)
#    fracVH    = RooRealVar("fracVH",   "fraction of gaussian wrt erfexp",  1.5e-2, 0.,   1.)
#    gausVH    = RooGaussian("gausVH",  "gaus for H jet mass", J_mass, meanVH, sigmaVH)
#
#    meanVW.setConstant(True)
#    sigmaVW.setConstant(True)
#    meanVZ.setConstant(True)
#    sigmaVZ.setConstant(True)
#    meanVH.setConstant(True)
#    sigmaVH.setConstant(True)
#
#    #if channel=="XWHenbb":
#    #    fracVV.setVal(5.5672e-01)
#    #    fracVV.setConstant(True)
#
#    # Define VV model
#    if functions[category]["VV"] == "ERFEXPGAUS": VVMass  = RooAddPdf("VVMass",   functions[category]["VV"], RooArgList(gausVW, erfrVV), RooArgList(fracVW))
#    elif functions[category]["VV"] == "ERFEXPGAUS2": VVMass  = RooAddPdf("VVMass",   functions[category]["VV"], RooArgList(gausVH, gausVW, erfrVV), RooArgList(fracVH, fracVW))
#    elif functions[category]["VV"] == "EXPGAUS": VVMass  = RooAddPdf("VVMass",   functions[category]["VV"], RooArgList(gausVW, expoVV), RooArgList(fracVW))
#    elif functions[category]["VV"] == "EXPGAUS2": VVMass  = RooAddPdf("VVMass",   functions[category]["VV"], RooArgList(gausVH, gausVW, expoVV), RooArgList(fracVH, fracVW))
#    elif functions[category]["VV"] == "EXPGAUS3": VVMass  = RooAddPdf("VVMass",   functions[category]["VV"], RooArgList(gausVH, gausVZ, gausVW, expoVV), RooArgList(fracVH, fracVZ, fracVW))
#    elif functions[category]["VV"] == "GAUS2": VVMass  = RooAddPdf("VVMass",   functions[category]["VV"], RooArgList(gausVH, gausVW), RooArgList(fracVH))
#    elif functions[category]["VV"] == "GAUS3": VVMass  = RooAddPdf("VVMass",   functions[category]["VV"], RooArgList(gausVH, gausVZ, gausVW), RooArgList(fracVH, fracVZ))
#    else:
#        print "  ERROR! Pdf", functions[category]["VV"], "is not implemented for VV"
#        exit()
#
#    # fit to secondary bkg in MC (whole range)
#    frVV = VVMass.fitTo(setVV, RooFit.SumW2Error(True), RooFit.Range("h_reasonable_range"), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Save(1), RooFit.PrintLevel(-1))
#    if VERBOSE: print "********** Fit result [JET MASS VV] ****", category, "*"*40, "\n", frVV.Print(), "\n", "*"*80
#    drawPlot("VVMass", category, J_mass, VVMass, setVV, [frVV])
#
#
#    #*******************************************************#
#    #                                                       #
#    #                 All bkg normalization                 #
#    #                                                       #
#    #*******************************************************#
#
##    constVjet.setConstant(True)
##    offsetVjet.setConstant(True)
##    widthVjet.setConstant(True)
##    a0Vjet.setConstant(True)
#    if nLept==2 and nBtag==2: a1Vjet.setConstant(True)
#    if nLept==0 or nLept==2 or nBtag==2: a2Vjet.setConstant(True)
#    a3Vjet.setConstant(True)
#    a4Vjet.setConstant(True)
##    p0Vjet.setConstant(True)
#    meanVjet.setConstant(True)
#    sigmaVjet.setConstant(True)
#    fracVjet.setConstant(True)
#
#    constTop.setConstant(True)
#    offsetTop.setConstant(True)
#    widthTop.setConstant(True)
#    meanW.setConstant(True)
#    sigmaW.setConstant(True)
#    fracW.setConstant(True)
#    meanT.setConstant(True)
#    sigmaT.setConstant(True)
#    fracT.setConstant(True)
#
#    constVV.setConstant(True)
#    offsetVV.setConstant(True)
#    widthVV.setConstant(True)
#    meanVW.setConstant(True)
#    sigmaVW.setConstant(True)
#    fracVW.setConstant(True)
#    meanVZ.setConstant(True)
#    sigmaVZ.setConstant(True)
#    fracVZ.setConstant(True)
#    meanVH.setConstant(True)
#    sigmaVH.setConstant(True)
#    fracVH.setConstant(True)
#
#    nVV.setConstant(True)
#    #nTop.setConstant(True)
#    #nTop2.setConstant(True)
#    #if not nLept==1:
#    nTop.setConstant(True)
#    nTop2.setConstant(True)
#    nVjet.setConstant(False)
#    nVjet2.setConstant(False)
#
##    if nLept==1:
##        constTop.setConstant(False)
##        #offsetTop.setConstant(False)
##        #widthTop.setConstant(False)
##        nTop.setConstant(False)
#
#    # Final background model by adding the main+secondary pdfs (using 'coef': ratio of the secondary/main, from MC)
#    #VjetMass_ext = RooExtendPdf("VjetMass_ext", "extended p.d.f", VjetMass, nVjet)
#    #VjetMass2_ext = RooExtendPdf("VjetMass2_ext", "extended p.d.f", VjetMass2, nVjet2)
#    #TopMass_ext  = RooExtendPdf("TopMass_ext",  "extended p.d.f", TopMass,  nTop)
#    #VVMass_ext   = RooExtendPdf("VVMass_ext",   "extended p.d.f", VVMass,   nVV)
#
#    BkgMass = RooAddPdf("BkgMass", "BkgMass", RooArgList(VVMass, TopMass, VjetMass), RooArgList(nVV, nTop, nVjet))
#    BkgMass2 = RooAddPdf("BkgMass2", "BkgMass2", RooArgList(VVMass, TopMass, VjetMass2), RooArgList(nVV, nTop2, nVjet2))
#    # These obscure commands screw up the integral normalization
#    #BkgMass.fixAddCoefRange("h_reasonable_range")
#    #BkgMass2.fixAddCoefRange("h_reasonable_range")
#    #BkgMass.fixAddCoefRange("h_extended_reasonable_range")
#    #BkgMass2.fixAddCoefRange("h_extended_reasonable_range")
#
#    #if channel=="XWHmnbb":
#    #    constVjet.setConstant(True)
#
#    # Extended fit model to data in SB
#    nTopPreFit = nTop.getVal()
#
#    frMass = BkgMass.fitTo(setDataSB, RooFit.SumW2Error(False), RooFit.Extended(True), RooFit.Range("LSBrange,HSBrange"), RooFit.Strategy(2), RooFit.Minimizer("Minuit"), RooFit.Save(1), RooFit.PrintLevel(-1)) #, RooFit.NumCPU(10)
#    if VERBOSE: print "********** Fit result [JET MASS DATA] **", category, "*"*40, "\n", frMass.Print(), "\n", "*"*80
#    if VERBOSE: frMass.correlationMatrix().Print()
#
#    nTopPostFit = nTop.getVal()
#
#    frMass2 = BkgMass2.fitTo(setDataSB, RooFit.SumW2Error(False), RooFit.Extended(True), RooFit.Range("LSBrange,HSBrange"), RooFit.Strategy(2), RooFit.Minimizer("Minuit"), RooFit.Save(1), RooFit.PrintLevel(-1))
#    if VERBOSE: print "********** Fit result [JET MASS DATA 2] **", category, "*"*40, "\n", frMass2.Print(), "\n", "*"*80
#
#    #if SCAN:
#    #    likelihoodScan(VjetMass, setVjet, [constVjet, offsetVjet, widthVjet])
#
#    # Fix normalization and parameters of V+jets after the fit to data
#    nVjet.setConstant(True)
#    nVjet2.setConstant(True)
#    nTop.setConstant(True)
#    nTop2.setConstant(True)
#
#    constVjet.setConstant(True)
#    offsetVjet.setConstant(True)
#    widthVjet.setConstant(True)
#    a0Vjet.setConstant(True)
#    a1Vjet.setConstant(True)
#    a2Vjet.setConstant(True)
#    a3Vjet.setConstant(True)
#    a4Vjet.setConstant(True)
#    p0Vjet.setConstant(True)
#
#    # integrals for global normalization
#    # do not integrate the composte model: results have no sense
#
#    # integral for normalization in the SB
#    iSBVjet = VjetMass.createIntegral(jetMassArg, RooFit.NormSet(jetMassArg), RooFit.Range("LSBrange,HSBrange"))
#    iSBVjet2 = VjetMass2.createIntegral(jetMassArg, RooFit.NormSet(jetMassArg), RooFit.Range("LSBrange,HSBrange"))
#    iSBTop = TopMass.createIntegral(jetMassArg, RooFit.NormSet(jetMassArg), RooFit.Range("LSBrange,HSBrange"))
#    iSBVV = VVMass.createIntegral(jetMassArg, RooFit.NormSet(jetMassArg), RooFit.Range("LSBrange,HSBrange"))
#
#    # integral for normalization in the SR
#    iSRVjet = VjetMass.createIntegral(jetMassArg, RooFit.NormSet(jetMassArg), RooFit.Range("SRrange"))
#    iSRVjet2 = VjetMass2.createIntegral(jetMassArg, RooFit.NormSet(jetMassArg), RooFit.Range("SRrange"))
#    iSRTop = TopMass.createIntegral(jetMassArg, RooFit.NormSet(jetMassArg), RooFit.Range("SRrange"))
#    iSRVV = VVMass.createIntegral(jetMassArg, RooFit.NormSet(jetMassArg), RooFit.Range("SRrange"))
#
#    # integral for normalization in the VR
#    iVRVjet = VjetMass.createIntegral(jetMassArg, RooFit.NormSet(jetMassArg), RooFit.Range("VRrange"))
#    iVRTop = TopMass.createIntegral(jetMassArg, RooFit.NormSet(jetMassArg), RooFit.Range("VRrange"))
#    iVRVV = VVMass.createIntegral(jetMassArg, RooFit.NormSet(jetMassArg), RooFit.Range("VRrange"))
#
#    # formual vars
#    SByield = RooFormulaVar("SByield", "normalization in SB", "@0*@1 + @2*@3 + @4*@5", RooArgList(iSBVjet, nVjet, iSBVV, nVV, iSBTop, nTop))
#    SByield2 = RooFormulaVar("SByield2", "normalization in SB", "@0*@1 + @2*@3 + @4*@5", RooArgList(iSBVjet2, nVjet2, iSBVV, nVV, iSBTop, nTop))
#    VRyield = RooFormulaVar("VRyield", "normalization in VR", "@0*@1 + @2*@3 + @4*@5", RooArgList(iVRVjet, nVjet, iVRVV, nVV, iVRTop, nTop))
#    SRyield = RooFormulaVar("SRyield", "normalization in SR", "@0*@1 + @2*@3 + @4*@5", RooArgList(iSRVjet, nVjet, iSRVV, nVV, iSRTop, nTop))
#    SRyield2 = RooFormulaVar("SRyield2", "normalization in SR", "@0*@1 + @2*@3 + @4*@5", RooArgList(iSRVjet2, nVjet2, iSRVV, nVV, iSRTop, nTop))
#    MainSRyield = RooFormulaVar("MainSRyield", "extrapolation to SR", "@0*@1", RooArgList(iSRVjet, nVjet))
#    MainSRyield2 = RooFormulaVar("MainSRyield2", "extrapolation to SR", "@0*@1", RooArgList(iSRVjet2, nVjet2))
#    TopSRyield = RooFormulaVar("TopSRyield", "extrapolation to SR", "@0*@1", RooArgList(iSRTop, nTop))
#    VVSRyield = RooFormulaVar("VVSRyield", "extrapolation to SR", "@0*@1", RooArgList(iSRVV, nVV))
#    # alternative method for main bakground estimation
#    SByieldRatio = RooFormulaVar("SByieldRatio", "extrapolation to SB","@0-@1*@3-@2*@4", RooArgList(entrySB, nVV, nTop, iSBVV, iSBTop))
#    SRyieldRatio = RooFormulaVar("SRyieldRatio", "extrapolation to SR","@0*@1/@2", RooArgList(SByieldRatio, iSRVjet, iSBVjet))
#    BkgYieldRatio            = SRyieldRatio.getVal()
#    BkgYieldRatio_error      = SRyieldRatio.getPropagatedError(frVjet)
#    BkgMassYield  = RooRealVar("BkgMassYield", "Background Yield in the Extended range", SByield.getVal(), 0., 1.e6)
#
#    # fractions
#    fMainSB = RooRealVar("fMainSB", "Fraction of Vjet events in SB", iSBVjet.getVal()*nVjet.getVal()/SByield.getVal(), 0., 1.)
#    fTopSB = RooRealVar("fTopSB", "Fraction of Top events in SB", iSBTop.getVal()*nTop.getVal()/SByield.getVal(), 0., 1.)
#    fVVSB = RooRealVar("fVVSB", "Fraction of VV events in SB", iSBVV.getVal()*nVV.getVal()/SByield.getVal(), 0., 1.)
#
#    fMainSR = RooRealVar("fMainSR", "Fraction of Vjet events in SR", iSRVjet.getVal()*nVjet.getVal()/SRyield.getVal(), 0., 1.)
#    fTopSR = RooRealVar("fTopSR", "Fraction of Top events in SR", iSRTop.getVal()*nTop.getVal()/SRyield.getVal(), 0., 1.)
#    fVVSR = RooRealVar("fVVSR", "Fraction of VV events in SR", iSRVV.getVal()*nVV.getVal()/SRyield.getVal(), 0., 1.)
#
#    # final normalization values
#    BkgYield            = SRyield.getVal()
#    BkgYield2           = SRyield2.getVal()
#    BkgYield_syst       = math.sqrt(SRyield.getPropagatedError(frVV)**2 + SRyield.getPropagatedError(frTop)**2)
#    BkgYield_stat       = math.sqrt(SRyield.getPropagatedError(frMass)**2)
#    BkgYield_alte       = abs(BkgYield - BkgYield2)
#    nBkgSR              = RooRealVar("nBkgSR", "expected yield in SR", BkgYield, 0., 1.e6)
#    nBkgSR.setError(math.sqrt( BkgYield_stat**2 + BkgYield_syst**2 + BkgYield_alte**2 + (BkgYield*fTopSR.getVal()*topSF[category][1])**2 + (BkgYield*fVVSR.getVal()*0.20)**2 ))
#
#    # backgrounds, separately
#    MainYield           = MainSRyield.getVal()
#    MainYieldErr        = MainSRyield.getPropagatedError(frMass)
#    MainYield2          = MainSRyield2.getVal()
#    MainYield2Err       = MainSRyield2.getPropagatedError(frMass2)
#    MainYieldAlt        = abs(MainYield2-MainYield)
#    TopYield            = TopSRyield.getVal()
#    TopYieldErr         = TopSRyield.getPropagatedError(frTop)
#    TopYieldSys         = math.sqrt(TopYieldErr**2 + (TopYield*topSF[category][1])**2 + (TopYield*topSF[category][2])**2)
#    VVYield             = VVSRyield.getVal()
#    VVYieldErr          = VVSRyield.getPropagatedError(frVV)
#    VVYieldSys          = math.sqrt(VVYieldErr**2 + (VVYield*vvSF[1])**2)
#    TotalYield          = MainYield + TopYield + VVYield
#    TotalYieldErr       = math.sqrt(MainYieldErr**2 + MainYieldAlt**2 + TopYieldErr**2 + VVYieldErr**2)
#    TotalYieldSys       = math.sqrt(MainYieldErr**2 + MainYieldAlt**2 + TopYieldSys**2 + VVYieldSys**2)
#    RatioSRSB           = SRyield.getVal()/SByield.getVal()
#
#    print "--- Channel", channel, "SR", "---"
#    print "#", channel, " bkg composition : V+jets %.3f (%.1f%%),   Top %.3f (%.1f%%),   VV %.3f (%.1f%%)" % (MainYield, fMainSR.getVal()*100, TopYield, fTopSR.getVal()*100, VVYield, fVVSR.getVal()*100)
#    print "#", channel, " main background:", MainYield, "+-", MainYieldErr, ", alternate:", BkgYieldRatio, "+-", BkgYieldRatio_error, "(fit) +-", math.sqrt(SByieldRatio.getVal()), "(stat)"
#    #print "#", channel, " top  background:", "\t%.3f -> %f, %f, %f" % (nTopPostFit/nTopPreFit, nTop.getVal(), nTopPreFit, nTopPostFit)
#    print "@", channel, "$%.0f \pm %.0f \pm %.0f$ & $%.0f \pm %.0f$ & $%.0f \pm %.0f$ & $%.0f \pm %.0f$ & $%.0f$ \\\\" % (MainYield, MainYieldErr, MainYieldAlt, TopYield, TopYieldSys, VVYield, VVYieldSys, TotalYield, TotalYieldSys, setDataSR.sumEntries() if not BLIND else -1 )
#    print "-"*11*2
#    
#    drawPlot("JetMass", category, J_mass, BkgMass, setDataSB if BLIND else setDataSRSB, [frMass], SByield.getVal(), None, "", BkgMass2)
#    drawPlot("JetMass_"+category, category, J_mass, BkgMass, setDataSB if BLIND else setDataSRSB, [frMass], SByield.getVal(), None, "", BkgMass2, SByield2.getVal())
#
#    #print setDataSB.sumEntries(), SByield.getVal()
#    #exit()
#    # ====== CONTROL VALUE ======
#
#
#    #############################################################################
#    #                           _____ _                                         #
#    #                          / ____| |                                        #
#    #                         | (___ | |__   __ _ _ __   ___                    #
#    #                          \___ \| '_ \ / _` | '_ \ / _ \                   #
#    #                          ____) | | | | (_| | |_) |  __/                   #
#    #                         |_____/|_| |_|\__,_| .__/ \___|                   #
#    #                                            | |                            #
#    #                                            |_|                            #
#    #############################################################################
#    # again, fancy ASCII art thanks to, I guess, Jose
#
#    # now move to the X_mass variable to fit the shapes in DATA and MC to get the final shape
#    # * only the MAIN bkg is used so far. the others could be added if necessary
#    # * using a erf*exp to model the slopes in X_mass
#    # * SIMULTANEOUS fit to MC_SR MC_SB and DATA_SB
#    # * the ratio of the PDFs from MC is the alpha = MC_SR/MC_SB
#    # * the DATA_SB PDF is then multiplied by alpha to obtain the expected DATA_SR (bkg only) PDF
#    # * with the simultaneous fit the full correlation matrix is correcly taken into account (we are fitting simultaneously the same variable in MC in two regions...)
#
#    # define the two categories (not ranges) to be used in the fit
#    reg = RooCategory("reg", "reg")
#    reg.defineType("mcSR")
#    reg.defineType("mcSB")
#
#    ### DEFINE ALL THE PARAMETERS (BOTH FOR STANDARD AND ALTERATIVE FNC)
#    par = {}
#    model = {}
#
#    # EXP const
#    for n in ["slopeMainSB", "slopeVjetSB", "slopeVjetSR", "slopeTopSB", "slopeTopSR", "slopeVVSB", "slopeVVSR"]: par[n] = RooRealVar(n, "slope of the exp",   -3.e-3,   -1., -1.e-6)
#    # EXP2
#    for n in ["const1MainSB", "const1VjetSB", "const1VjetSR", "const1TopSB", "const1TopSR", "const1VVSB", "const1VVSR"]: par[n] = RooRealVar(n, "slope of the exp 1", -5.e-3,   -1.,     0.)
#    for n in ["const2MainSB", "const2VjetSB", "const2VjetSR", "const2TopSB", "const2TopSR", "const2VVSB", "const2VVSR"]: par[n] = RooRealVar(n, "slope of the exp 2", -8.e-3,   -1.,     0.)
#    for n in ["fracMainSB", "fracVjetSB", "fracVjetSR", "fracTopSB", "fracTopSR", "fracVVSB", "fracVVSR"]: par[n] = RooRealVar(n, "fraction",            5.e-2,    0.,     10.)
#    # EXPN
#    for n in ["numMainSB", "numVjetSB", "numVjetSR", "numTopSB", "numTopSR", "numVVSB", "numVVSR"]: par[n] = RooRealVar(n, "term ~x of the expN",  -3.e-3,   -1.e-2, +1.e-4)
#    for n in ["denMainSB", "denVjetSB", "denVjetSR", "denTopSB", "denTopSR", "denVVSB", "denVVSR"]: par[n] = RooRealVar(n, "term ~1/x of the expN",  3.e+3,   -2.e+4, +1.e+5)
#    # EXPTAIL
#    for n in ["c0MainSB", "c0VjetSB", "c0VjetSR", "c0TopSB", "c0TopSR", "c0VVSB", "c0VVSR"]: par[n] = RooRealVar(n, "term ~x^0 of the pol1", 400., 40., 1.e4) #10., 0.1, 1.e4)
#    for n in ["c1MainSB", "c1VjetSB", "c1VjetSR", "c1TopSB", "c1TopSR", "c1VVSB", "c1VVSR"]: par[n] = RooRealVar(n, "term ~x^1 of the pol1", 0.10, 0,  0.50)
#    # ERFEXP offset and width
#    for n in ["constMainSB", "constVjetSB", "constVjetSR", "constTopSB", "constTopSR", "constVVSB", "constVVSR"]: par[n] = RooRealVar(n, "slope of the exp",   -3e-3,   -1., -1.e-6)
#    for n in ["offsetMainSB", "offsetVjetSB", "offsetVjetSR", "offsetTopSB", "offsetTopSR", "offsetVVSB", "offsetVVSR"]: par[n] = RooRealVar(n, "offset of the erf",   1.2e3,   0.,     1.5e3)
#    for n in ["widthMainSB", "widthVjetSB", "widthVjetSR", "widthTopSB", "widthTopSR", "widthVVSB", "widthVVSR"]: par[n] = RooRealVar(n, "width of the erf",   1.e3,   50.,     1.e4)
#    # POW
#    for n in ["p0MainSB", "p0VjetSB", "p0VjetSR", "p0TopSB", "p0TopSR", "p0VVSB", "p0VVSR"]: par[n] = RooRealVar(n, "parameter 1 of the powerlaw",   20.,   0., 100)
#    for n in ["p1MainSB", "p1VjetSB", "p1VjetSR", "p1TopSB", "p1TopSR", "p1VVSB", "p1VVSR"]: par[n] = RooRealVar(n, "parameter 2 of the powerlaw",   1.,   0., 1000)
#    for n in ["p2MainSB", "p2VjetSB", "p2VjetSR", "p2TopSB", "p2TopSR", "p2VVSB", "p2VVSR"]: par[n] = RooRealVar(n, "parameter 3 of the powerlaw",   1.,   -1000., 1000)
#
#    if not EXTRAPOLATE:
#        #par["denMainSB"].setMin(0.)
#
#    #    if nLept==0: # and nBtag==1:
#    #        for n, p in par.iteritems():
#    #            if n.startswith('c1'): p.setMax(0.04)
#    #        par["denMainSB"].setMin(1000.)
#    #        par["denMainSB"].setMax(2000.)
#    #        par["denVjetSB"].setMin(1400.)
#    #        par["denVjetSB"].setMax(2000.)
#    #        par["denVjetSR"].setMin(1000.)
#    #        par["denVjetSR"].setMax(2000.)
#    #        par["denTopSR"].setMax(0.)
#    #        par["denVVSR"].setMax(0.)
#        if nLept==0:
##            par["numMainSB"].setMin(-1.e-1)
##            par["denMainSB"].setMax(1.e+6)
##            par["denMainSB"].setVal(350.e+3)
#    #        par["numVjetSB"].setVal(-3.4e-3)
#    #        par["numVjetSR"].setVal(-3.8e-3)
#    #        par["denVjetSB"].setVal(1600)
#    #        par["denVjetSR"].setVal(1900)
#            par["denVVSR"].setMin(1000)
#            par["denVVSR"].setMax(5000)
#            par["denTopSB"].setVal(-1300)
#    #        par["denTopSB"].setMax(0)
#            #par["c1VjetSB"].setMax(0.025)
#            if nBtag==1:
##                par["c1VjetSR"].setVal(0.050)
##                par["c1VjetSR"].setMin(0.035)
##                par["c1VjetSR"].setMax(0.100)
##                par["denVjetSB"].setVal(1760)
##                par["denVjetSB"].setMin(1250)
##                par["denVjetSB"].setMax(2500)
##                par["numVjetSR"].setVal(-2.5e-3)
##                par["numVjetSR"].setMin(-4.e-3)
##                par["numVjetSR"].setMax(-1.e-3)
#                par["c1VjetSR"].setVal(0.01)
#                par["c1VjetSR"].setMax(0.025)
##                par["denVVSB"].setVal(-1000)
##                par["denVVSB"].setMax(-500)
##                par["denVVSB"].setMin(-2000)
#                par["c1VVSR"].setVal(0.01)
#                par["c1VVSR"].setMax(0.03)
#            #par["c1VVSB"].setMax(-0.05)
#            #par["c1VVSR"].setMax(+0.05)
#            par["c1TopSB"].setVal(-0.01)
#            if nBtag==2:
#                par["numTopSR"].setVal(-0.007)
#                par["numTopSR"].setMin(-0.01)
#                par["numTopSR"].setMax(-0.005)
#        if nElec==1:
#            if nBtag==1:
#                par["denVjetSB"].setVal(1400)
#                par["denVjetSB"].setMin(1200)
#                par["denVjetSB"].setMax(2000)
#        #        par["denVjetSR"].setVal(400)
#        #        par["denVjetSR"].setMin(200)
#        #        par["denVjetSR"].setMax(800)
#                par["denVVSR"].setVal(-1700)
#                par["denVVSR"].setMin(-1800)
#                par["denVVSR"].setMax(-1550)
#                par["c1VVSR"].setMin(-0.05)
#                par["c1TopSR"].setVal(-0.01)
#                par["c1TopSR"].setMax(+0.01)
#                par["c1TopSR"].setMin(-0.05)
#            if nBtag==2:
#                par["numVjetSR"].setVal(-3.75e-3)
#                par["numVjetSR"].setMin(-7.00e-3)
#                par["numVjetSR"].setMax(-1.50e-3)
#                par["denVjetSR"].setVal(-700)
#                par["denVjetSR"].setMin(-1500)
#                par["denVjetSR"].setMax(-300)
##                par["numVjetSB"].setVal(-2.65e-3)
##                par["numVjetSB"].setMin(-5.00e-2)
##                par["numVjetSB"].setMax(-1.00e-4)
##                par["denVjetSB"].setVal(1000)
##                par["denVjetSB"].setMin(500)
##                par["denVjetSB"].setMax(2000)
##                par["numVVSR"].setVal(-0.0050)
##                par["numVVSR"].setMin(-0.0057)
##                par["numVVSR"].setMax(-0.0043)
##                par["denVVSR"].setVal(-1700)
##                par["denVVSR"].setMin(-1800)
##                par["denVVSR"].setMax(-1550)
#                par["c1VVSR"].setMin(-0.05)
#        if nMuon==1:
#            if nBtag==1:
#                par["c1VjetSR"].setMin(0.02)
#        #        par["c1VjetSB"].setMin(-0.20)
#                par["denVjetSB"].setVal(2500)
#                par["denVjetSB"].setMin(1400)
#                par["denVjetSB"].setMax(4000)
#                par["denVjetSR"].setVal(1868)
#                par["denVjetSR"].setMin(800)
#                par["denVjetSR"].setMax(4000)
#                par["denVVSR"].setVal(-250)
#    #            par["denVVSR"].setMin(-600)
#    #            par["denVVSR"].setMax(-0)
#            elif nBtag==2:
#    #            par["denVjetSR"].setVal(-100)
#    #            par["denVjetSR"].setMin(-200)
#    #            par["denVjetSR"].setMin(0)
#                par["c1VjetSB"].setMin(-0.05)
#                par["c1VjetSR"].setMin(-0.01)
##                par["numVVSR"].setVal(-0.0025)
##                par["numVVSR"].setMin(-0.0028)
##                par["numVVSR"].setMax(-0.0022)
#                par["numVVSR"].setVal(-0.0025)
#                par["numVVSR"].setMin(-0.0035)
#                par["numVVSR"].setMax(-0.0015)
#                par["denVVSR"].setVal(1300)
#                par["denVVSR"].setMin(500)
#                par["denVVSR"].setMax(2000)
##                par["denTopSR"].setVal(-300)
##                par["denTopSR"].setMin(-330)
##                par["denTopSR"].setMax(-280)
#        if nElec==2:
#            if nBtag==1:
#                par["c1TopSR"].setMin(-0.05)
#    #            par["denVjetSR"].setVal(1200.)
#    #            par["denVjetSR"].setMin(-300.)
#    #            par["denVjetSR"].setMax(2000.)
##                par["denVjetSB"].setVal(1300.)
##                par["denVjetSB"].setMin(300.)
##                par["denVjetSB"].setMax(3000.)
##                par["numVjetSB"].setMin(-5.e-3)
##                par["numVjetSB"].setMax(-2.e-3)
#                par["numVVSR"].setVal(-0.0025)
#                par["numVVSR"].setMin(-0.0030)
#                par["numVVSR"].setMax(-0.0020)
#            if nBtag==2:
#                par["denMainSB"].setMin(0.)
#                par["denMainSB"].setMax(1.e4)
#    #            par["denVjetSB"].setMin(1000.)
##                par["numTopSR"].setVal(-0.005)
##                par["numTopSR"].setMax(-0.001)
##                par["numTopSR"].setMin(-0.01)
#                par["denTopSR"].setVal(1000.)
#                par["denTopSR"].setMax(200.)
#                par["denTopSR"].setMin(0.)
#        if nMuon==2:
#            par["denVjetSB"].setMax(1.e5)
#            par["denVjetSR"].setMax(1.e5)
#            par["denMainSB"].setMin(0.)
#            if nBtag==1:
#                par["numTopSR"].setVal(-0.003)
#                par["numTopSR"].setMax(-0.001)
#                par["numTopSR"].setMin(-0.004)
#                par["denTopSR"].setVal(3000.)
#                par["denTopSR"].setMax(5000.)
#                par["denTopSR"].setMin(1000.)
#                par["numVjetSB"].setVal(-4.e-3)
#                par["numVjetSB"].setMin(-6.e-3)
#                par["numVjetSB"].setMax(-2.e-3)
#                par["denVjetSB"].setVal(1500)
#                par["denVjetSB"].setMin(1000)
#                par["denVjetSB"].setMax(2000)
#                par["denVjetSR"].setVal(700)
##                par["denVjetSR"].setMin(500)
##                par["denVjetSR"].setMax(2000)
#            if nBtag==2:
#                par["numTopSR"].setVal(-0.0067)
#                par["numTopSR"].setMax(-0.0050)
#                par["numTopSR"].setMin(-0.0085)
#                par["denTopSR"].setVal(1700.)
#                par["denTopSR"].setMax(3500.)
#                par["denTopSR"].setMin(500.)
#
#    #    if nLept==0:
#    #        par["c1MainSB"].setMax(0.04)
#    #        par["c1VjetSB"].setMax(0.04)
#    #        par["c1VjetSR"].setMax(0.04)
#    #        #par["c1MainSB"].setMin(0.005)
#    #        par["c1VjetSB"].setMin(0.01)
#    #        par["c1VjetSR"].setMin(0.01)
#    #        par["c1VVSB"].setMax(0.01)
#    #        par["c1VVSR"].setMax(0.01)
#    #        par["c1TopSB"].setMax(0.03)
#    #        # FIXME: set 0.05 as max for all ExpTail
#    #    if nLept==1:
#    #        par["c1TopSB"].setMin(-0.1)
#    #        par["c0MainSB"].setVal(210)
#    #        par["c0VjetSB"].setVal(245)
#    #        par["c0VjetSR"].setVal(200)
#    ##        if nElec==1 or (nMuon==1 and nBtag==2):
#    #        par["denVjetSR"].setVal(3.e-3)
#    #        par["denVjetSR"].setMin(0.)
#    #        #par["denVjetSB"].setMin(0.)
#    #        par["denVjetSR"].setMax(60.)
#
#    #    if nLept==2:
#    #        par["denTopSR"].setMin(0.)
#    #        par["denVjetSR"].setMax(60.)
#
#        if nLept==1 and nBtag==1:
#            par["c1VVSR"].setVal(-0.02)
#
##################################33
#
##        #if nBtag==1: par["c0VjetSR"].setVal(200)
##        #else: par["c0VjetSR"].setVal(300)
###        if nElec==1 and nBtag==1:
###            par["denVjetSB"].setMin(0.)
###            par["c1VjetSB"].setMin(-1.)
###            par["c1VjetSR"].setMin(-1.)
###            #par["c1TopSR"].setMin(-0.1)
###            par["c0MainSB"].setVal(230)
###            par["c0VjetSB"].setVal(225)
###            par["c0VjetSR"].setVal(285)
##            #par["c0VjetSR"].setMax(290)
##            #par["c0VjetSR"].setMin(280)
##            #par["c1MainSB"].setVal(0.027)
##            #par["c1VjetSB"].setVal(0.030)
##            #par["c1VjetSR"].setVal(0.012)
##            #par["c1VjetSR"].setMin(-0.1)
##
###    if channel == "XZHnnb":
####        par["denTopSB"].setMax(1000)
####        par["denVVSB"].setMax(1000)
###        par["denTopSR"] = RooRealVar("denTopSR", "term ~1/x of the expN",  1.e+1,   1.e-6,   5.e+3) #1.2
###        par["numVjetSB"] = RooRealVar("numVjetSB", "term ~x of the expN",  -3.e-3,   -4.e-3, -2.e-3)
###        par["numVjetSR"] = RooRealVar("numVjetSR", "term ~x of the expN",  -4.e-3,   -5.e-3, -3.e-3)
###        par["denVjetSB"] = RooRealVar("denVjetSB", "term ~1/x of the expN",  2150.,   1500,   2500)
###        par["denVjetSR"] = RooRealVar("denVjetSR", "term ~1/x of the expN",  1575.,   1000,   2000)
###        par["denVjetSB"] = RooRealVar("denVjetSB", "term ~1/x of the expN",  1375.,   1000,   2000)
###    if channel == "XZHnnbb":
####        par["denVjetSR"].setMax(2000)
####        #par["denVjetSB"].setMax(2500)
####        par["denMainSB"].setMax(500)#FIXME
###        par["denVjetSB"] = RooRealVar("denVjetSB", "term ~1/x of the expN",   250,   1.,   1000)
###        par["denVjetSB"] = RooRealVar("denVjetSB", "term ~1/x of the expN",  1000,   1.,   5000)
###        par["denVjetSR"] = RooRealVar("denVjetSR", "term ~1/x of the expN",   350,   1.,   5000)
###        par["denTopSB"] = RooRealVar("denTopSB", "term ~1/x of the expN",  1.e+1,   1.e-6,   5.e+3)
##    if channel == "XWHenb":
##        par["denVjetSR"].setVal(1000)
##        par["denVjetSR"].setMin(-1000)
##        #par["denTopSB"].setMin(-2000)
##        #par["denVjetSR"].setMax(20000)
##        par["numVjetSB"].setVal(-0.01)
##        par["denVjetSB"].setVal(4000)
##        par["denVjetSB"].setMax(10000)
##        par["denVjetSB"].setMin(1500)
##        #par["c1VjetSR"].setMin(-1000)
##
###        par["denVjetSB"] = RooRealVar("denVjetSB", "term ~1/x of the expN",  10,   0.,  500)
###        par["denVjetSR"] = RooRealVar("denVjetSR", "term ~1/x of the expN",  50,   0.,   1000)
###        par["c1TopSR"] = RooRealVar("c1TopSR", "term ~x^1 of the pol1", 1.e-4, 0.,  0.015)
###    if channel == "XWHenbb":
###        par["denVVSB"] = RooRealVar("denVVSB", "term ~1/x of the expN",  1.,   1.e-6,   1.e+3)
###        par["denVVSR"] = RooRealVar("denVVSR", "term ~1/x of the expN",  1.,   1.e-6,   1.e+3)
###        par["denTopSB"] = RooRealVar("denTopSB", "term ~1/x of the expN",  1.,   -1.e4,   1.e+3)
###    if channel == "XWHmnb":
###        par["c0VjetSR"] = RooRealVar("c0VjetSR", "term ~x^0 of the pol1", 190., 100., 300)
###        par["c0VjetSB"] = RooRealVar("c0VjetSB", "term ~x^0 of the pol1", 240., 150., 350)
###        par["c1VjetSR"] = RooRealVar("c1VjetSR", "term ~x^1 of the pol1", 0.032, 0.01,  0.05)
###        par["c1VjetSB"] = RooRealVar("c1VjetSB", "term ~x^1 of the pol1", 0.025, 0.01,  0.05)
###    if channel == "XWHmnbb":
####        par["numVjetSR"] = RooRealVar("numVjetSR", "term ~x of the expN",  -1.e-3,   -1.e-1, -1.e-6)
###        par["denVjetSR"] = RooRealVar("denVjetSR", "term ~1/x of the expN",  600,   -1.e4,   1.e+5)
###        par["denVjetSB"] = RooRealVar("denVjetSR", "term ~1/x of the expN",  600,   -1.e4,   1.e+5)
###        par["denTopSB"] = RooRealVar("denTopSB", "term ~1/x of the expN",  1.,   -1.e4,   1.e+3)
###    if channel == "XZHmmb":
###        par["c0MainSB"] = RooRealVar("c0MainSB", "term ~x^0 of the pol1", 60., 20., 100)
###        par["c0VjetSR"] = RooRealVar("c0VjetSR", "term ~x^0 of the pol1", 220., 100., 300)
###        par["c1MainSB"] = RooRealVar("c1MainSB", "term ~x^1 of the pol1", 0.05, 0.01,  0.10)
###        par["c1VjetSR"] = RooRealVar("c1VjetSR", "term ~x^1 of the pol1", 0.03, 0.01,  0.05)
##    if channel == "XZHeeb":
##        par["denMainSB"].setMax(3000)
###        par["c0VjetSR"] = RooRealVar("c0VjetSR", "term ~x^0 of the pol1", 300., 200, 400)
###        par["c1VjetSB"] = RooRealVar("c1VjetSB", "term ~x^1 of the pol1", 0.01, 0.,  7.5e-2)
###        par["c1VjetSR"] = RooRealVar("c1VjetSR", "term ~x^1 of the pol1", 0.002, 0., 0.005)
##    if channel == "XZHeebb":
##        #par["denVjetSR"].setMax(300)
##        par["denVjetSR"].setVal(200)
##        par["denVjetSR"].setMin(-500)
##        par["denVjetSR"].setMax(800)
###        par["c1VjetSB"] = RooRealVar("c1VjetSB", "term ~x^1 of the pol1", 0.1, 1.e-6,  1.)
#
#    # Define PRIMARY PDF for shape
#    if functions[category]["Shape"] == "EXP":
#        for n in ["MainSB", "VjetSB", "VjetSR", "TopSB", "TopSR", "VVSB", "VVSR"]: model[n] = RooExponential(n+"", "Exp", X_mass, par["slope"+n])
#        alpha = RooAlphaExp("alpha", "#alpha function (Exp)", X_mass, par["slopeVjetSR"], par["slopeVjetSB"], X_mass.getMin(), X_mass.getMax())
#    elif functions[category]["Shape"] == "EXP2":
#        for n in ["MainSB", "VjetSB", "VjetSR", "TopSB", "TopSR", "VVSB", "VVSR"]: model[n] = Roo2ExpPdf(n+"", "Exp2", X_mass, par["const1"+n], par["const2"+n], par["frac"+n])
#        alpha = RooAlpha42ExpPdf("alpha", "#alpha function (Exp2)", X_mass, par["const1VjetSR"], par["const2VjetSR"], par["fracVjetSR"], par["const1VjetSB"], par["const2VjetSB"], par["fracVjetSB"])
#    elif functions[category]["Shape"] == "EXPN":
#        for n in ["MainSB", "VjetSB", "VjetSR", "TopSB", "TopSR", "VVSB", "VVSR"]: model[n] = RooExpNPdf(n+"", "ExpN", X_mass, par["num"+n], par["den"+n])
#        alpha = RooAlpha4ExpNPdf("alpha", "#alpha function (ExpN)", X_mass, par["numVjetSR"], par["denVjetSR"], par["numVjetSB"], par["denVjetSB"])
#    elif functions[category]["Shape"] == "EXPTAIL":
#        for n in ["MainSB", "VjetSB", "VjetSR", "TopSB", "TopSR", "VVSB", "VVSR"]: model[n] = RooExpTailPdf(n+"", "ExpTail", X_mass, par["c0"+n], par["c1"+n])
#        alpha = RooAlpha4ExpTailPdf("alpha", "#alpha function (ExpTail)", X_mass, par["c0VjetSR"], par["c1VjetSR"], par["c0VjetSB"], par["c1VjetSB"])
#    elif functions[category]["Shape"] == "ERFEXP":
#        for n in ["MainSB", "VjetSB", "VjetSR", "TopSB", "TopSR", "VVSB", "VVSR"]: model[n] = RooErfExpPdf(n+"", "ErfExp", X_mass, par["const"+n], par["offset"+n], par["width"+n])
#        alpha = RooAlpha("alpha", "#alpha function (ErfExp)", X_mass, par["constVjetSR"], par["offsetVjetSR"], par["widthVjetSR"], par["constVjetSB"], par["offsetVjetSB"], par["widthVjetSB"], X_mass.getMin(), X_mass.getMax())
#    elif functions[category]["Shape"] == "POW1":
#        for n in ["MainSB", "VjetSB", "VjetSR", "TopSB", "TopSR", "VVSB", "VVSR"]: model[n] = RooGenericPdf(n+"", "POW1", "1/pow(@0/13000, @1)", RooArgList(X_mass, par["p0"+n]))
#        alpha = RooGenericPdf("alpha", "#alpha function (Powerlaw)", "( 1./pow(@0/13000., @1) )/( 1./pow(@0/13000., @2) )", RooArgList(X_mass, par["p0VjetSR"], par["p0VjetSB"]))
#    elif functions[category]["Shape"] == "POW2":
#        for n in ["MainSB", "VjetSB", "VjetSR", "TopSB", "TopSR", "VVSB", "VVSR"]: model[n] = RooGenericPdf(n+"", "POW2", "pow(1-@0/13000, @1) / pow(@0/13000, @2)", RooArgList(X_mass, par["p0"+n], par["p1"+n]))
#        alpha = RooGenericPdf("alpha", "#alpha function (Powerlaw)", "( pow(1-@0/13000, @1) / pow(@0/13000, @2) )/( pow(1-@0/13000, @3) / pow(@0/13000, @4) )", RooArgList(X_mass, par["p0VjetSR"], par["p1VjetSR"], par["p0VjetSB"], par["p1VjetSB"]))
#    elif functions[category]["Shape"] == "POW3":
#        for n in ["MainSB", "VjetSB", "VjetSR", "TopSB", "TopSR", "VVSB", "VVSR"]: model[n] = RooGenericPdf(n+"", "POW3", "pow(1-@0/13000, @1) / pow(@0/13000, @2+@3*log(@0/13000))", RooArgList(X_mass, par["p0"+n], par["p1"+n], par["p2"+n]))
#        alpha = RooGenericPdf("alpha", "#alpha function (Powerlaw)", "( pow(1-@0/13000, @1) / pow(@0/13000, @2+@3*log(@0/13000)) )/( pow(1-@0/13000, @4) / pow(@0/13000, @5+@6*log(@0/13000)) )", RooArgList(X_mass, par["p0VjetSR"], par["p1VjetSR"], par["p2VjetSR"], par["p0VjetSB"], par["p1VjetSB"], par["p2VjetSB"]))
#    else:
#        print "  ERROR! Pdf", functions[category]["Shape"], "is not implemented"
#        exit()
#
#    #for n in ["MainSB", "TopSB", "TopSR", "VVSB", "VVSR"]: model[n] = RooExponential(n+"", "exponential for X mass", X_mass, par["const"+n])
##    if nLept==2:
##        par["c1TopSR"].setVal(0.)
##        par["c1TopSR"].setConstant(True)
##        par["c1TopSB"].setVal(0.)
##        par["c1TopSB"].setConstant(True)
#        #for n in ["TopSB", "TopSR"]: model[n] = RooExponential(n+"", "Exp", X_mass, par["slope"+n]) #FIXME
#    #if nLept==1:
#    #    model["TopSB"] = RooErfExpPdf("TopSB", "ErfExp", X_mass, par["constTopSB"], par["offsetTopSB"], par["widthTopSB"])
#    #if nLept==0 and nBtag==1:
#    #    model["TopSR"] = RooExponential("TopSR", "Exp", X_mass, par["slopeTopSR"])
#
#
#    # Define ALTERNATIVE PDF for shape
#    if functions[category]["ShapeAlt"] == "EXP":
#        for n in ["MainSB", "VjetSB", "VjetSR", "TopSB", "TopSR", "VVSB", "VVSR"]: model[n+"2"] = RooExponential(n+"2", "exponential for X mass", X_mass, par["slope"+n])
#        alpha2 = RooAlphaExp("alpha2", "alternative #alpha (Exp)", X_mass, par["slopeVjetSR"], par["slopeVjetSB"], X_mass.getMin(), X_mass.getMax())
#    elif functions[category]["ShapeAlt"] == "EXP2":
#        for n in ["MainSB", "VjetSB", "VjetSR", "TopSB", "TopSR", "VVSB", "VVSR"]: model[n+"2"] = Roo2ExpPdf(n+"2", "double exponential for X mass", X_mass, par["const1"+n], par["const2"+n], par["frac"+n])
#        alpha2 = RooAlpha42ExpPdf("alpha2", "alternative #alpha (Exp2)", X_mass, par["const1VjetSR"], par["const2VjetSR"], par["fracVjetSR"], par["const1VjetSB"], par["const2VjetSB"], par["fracVjetSB"])
#    elif functions[category]["ShapeAlt"] == "EXPN":
#        for n in ["MainSB", "VjetSB", "VjetSR", "TopSB", "TopSR", "VVSB", "VVSR"]: model[n+"2"] = RooExpNPdf(n+"2", "Nexponential for X mass", X_mass, par["num"+n], par["den"+n])
#        alpha2 = RooAlpha4ExpNPdf("alpha2", "alternative #alpha (ExpN)", X_mass, par["numVjetSR"], par["denVjetSR"], par["numVjetSB"], par["denVjetSB"])
#    elif functions[category]["ShapeAlt"] == "EXPTAIL":
#        for n in ["MainSB", "VjetSB", "VjetSR", "TopSB", "TopSR", "VVSB", "VVSR"]: model[n+"2"] = RooExpTailPdf(n+"2", "exponential tail for X mass", X_mass, par["c0"+n], par["c1"+n])
#        alpha2 = RooAlpha4ExpTailPdf("alpha2", "alternative #alpha (ExpTail)", X_mass, par["c0VjetSR"], par["c1VjetSR"], par["c0VjetSB"], par["c1VjetSB"])
#    elif functions[category]["ShapeAlt"] == "ERFEXP":
#        for n in ["MainSB", "VjetSB", "VjetSR", "TopSB", "TopSR", "VVSB", "VVSR"]: model[n+"2"] = RooErfExpPdf(n+"2", "error function for X mass", X_mass, par["const"+n], par["offset"+n], par["width"+n])
#        alpha2 = RooAlpha("alpha2", "alternative #alpha (ErfExp)", X_mass, par["constVjetSR"], par["offsetVjetSR"], par["widthVjetSR"], par["constVjetSB"], par["offsetVjetSB"], par["widthVjetSB"], X_mass.getMin(), X_mass.getMax())
#    elif functions[category]["ShapeAlt"] == "POW":
#        for n in ["MainSB", "VjetSB", "VjetSR", "TopSB", "TopSR", "VVSB", "VVSR"]: model[n+"2"] = RooGenericPdf(n+"2", "POW1", "@0^@1", RooArgList(X_mass, par["p0"+n]))
#        alpha2 = RooGenericPdf("alpha2", "alternative #alpha (Powerlaw)", "@0^@1/@0^@2", RooArgList(X_mass, par["p0VjetSR"], par["p0VjetSB"]))
#    elif functions[category]["ShapeAlt"] == "POW2":
#        for n in ["MainSB", "VjetSB", "VjetSR", "TopSB", "TopSR", "VVSB", "VVSR"]: model[n+"2"] = RooGenericPdf(n+"2", "POW2", "pow(1-@0/13000, @1) / pow(@0/13000, @2)", RooArgList(X_mass, par["p0"+n], par["p1"+n]))
#        alpha2 = RooGenericPdf("alpha2", "#alpha function (Powerlaw)", "( pow(1-@0/13000, @1) / pow(@0/13000, @2) )/( pow(1-@0/13000, @3) / pow(@0/13000, @4) )", RooArgList(X_mass, par["p0VjetSR"], par["p1VjetSR"], par["p0VjetSB"], par["p1VjetSB"]))
#    else:
#        print "  ERROR! Pdf", functions[category]["ShapeAlt"], "is not implemented"
#        exit()
#
#
#    # the relative normalization of the varius bkg is taken from MC by counting all the events in the full fatJetMass range
#
#    # Declare PRIMARY composite pdf
#    model["Vjets"] = RooProdPdf("Vjets",  "Main background estimation with alpha", alpha, model["MainSB"])
#    model["MainSR"] = RooProdPdf("MainSR",  "Main background estimation with alpha", alpha, model["MainSB"])
#    model["BkgSB"] = RooAddPdf("BkgSB", "Sum of the backgrounds in SB", RooArgList(model["MainSB"], model["VVSB"], model["TopSB"]), RooArgList(fMainSB, fVVSB)) #RooArgList(nTop, nVV, nVjet)
#    model["BkgSR"] = RooAddPdf("BkgSR", "Sum of the backgrounds in SR", RooArgList(model["MainSR"], model["VVSR"], model["TopSR"]), RooArgList(fMainSR, fVVSR))
#    # Definitive versions for combine
#    #model["Main"] = RooProdPdf("Main",  "Main background estimation with alpha", alpha, model["MainSB"])
#    #model["Bkg"] = RooAddPdf("Bkg", "Sum of the backgrounds in SR", RooArgList(model["Main"], model["VV"], model["Top"]), RooArgList(fMainSR, fVVSR))
#
#    # Declare ALTERNATIVE composite pdf
#    model["MainSR2"] = RooProdPdf("MainSR2",  "Main background estimation with alternative alpha", alpha2, model["MainSB"])
#    model["BkgSB2"] = RooAddPdf("BkgSB2", "Sum of the backgrounds in SB", RooArgList(model["MainSB2"], model["VVSB"], model["TopSB"]), RooArgList(fMainSB, fVVSB))
#    model["BkgSR2"] = RooAddPdf("BkgSR2", "Sum of the backgrounds in SR", RooArgList(model["MainSR2"], model["VVSR"], model["TopSR"]), RooArgList(fMainSR, fVVSR))
#
#    # PART 1: fit the sub-dominant backgrounds in the sidebands
#
#    #************************************************************#
#    #                                                            #
#    #   1: fit the sub-dominant backgrounds in the SB and SR     #
#    #                                                            #
#    #************************************************************#
#
#    # Fit the Top in SB
#    frTopSB = model["TopSB"].fitTo(setTopSB, RooFit.SumW2Error(True), RooFit.Range("X_reasonable_range"), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Save(1), RooFit.PrintLevel(-1))
#    if VERBOSE: print "********** Fit result [X MASS TOP SB] ***", category, "*"*40, "\n", frTopSB.Print(), "\n", "*"*80
#    drawPlot("TopSB", category, X_mass, model["TopSB"], setTopSB, [frTopSB])
#    
#    # Fit the VV in SB
#    frVVSB = model["VVSB"].fitTo(setVVSB, RooFit.SumW2Error(True), RooFit.Range("X_reasonable_range"), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Save(1), RooFit.PrintLevel(-1))
#    if VERBOSE: print "********** Fit result [X MASS VV SB] ***", category, "*"*40, "\n", frVVSB.Print(), "\n", "*"*80
#    drawPlot("VVSB", category, X_mass, model["VVSB"], setVVSB, [frVVSB])
#
#    # Fit the Top in SR
#    frTopSR = model["TopSR"].fitTo(setTopSR, RooFit.SumW2Error(True), RooFit.Range("X_reasonable_range"), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Save(1), RooFit.PrintLevel(-1))
#    frTopSR2 = model["TopSR2"].fitTo(setTopSR, RooFit.SumW2Error(True), RooFit.Range("X_reasonable_range"), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Save(1), RooFit.PrintLevel(-1))
#    if REGENERATE: model["TopSR"], frTopSR  = reGenerate(setTopSR, model["TopSR"], X_mass)
#    if VERBOSE: print "********** Fit result [X MASS TOP SR] ***", category, "*"*40, "\n", frTopSR.Print(), "\n", "*"*80
#    drawPlot("TopSR", category, X_mass, model["TopSR"], setTopSR, [frTopSR], -1, None, "", model["TopSR2"])
#
#    # Fit the VV in SR
#    frVVSR = model["VVSR"].fitTo(setVVSR, RooFit.SumW2Error(True), RooFit.Range("X_reasonable_range"), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Save(1), RooFit.PrintLevel(-1))
#    frVVSR2 = model["VVSR2"].fitTo(setVVSR, RooFit.SumW2Error(True), RooFit.Range("X_reasonable_range"), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Save(1), RooFit.PrintLevel(-1))
#    if REGENERATE: model["VVSR"], frVVSR  = reGenerate(setVVSR, model["VVSR"], X_mass)
#    if VERBOSE: print "********** Fit result [X MASS VV SR] ***", category, "*"*40, "\n", frVVSR.Print(), "\n", "*"*80
#    drawPlot("VVSR", category, X_mass, model["VVSR"], setVVSR, [frVVSR], -1, None, "", model["VVSR2"])
#    
##    # Pre-fit V+jets
##    frVjetSR = model["VjetSR"].fitTo(setVjetSR, RooFit.SumW2Error(True), RooFit.Range("X_reasonable_range"), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Save(1), RooFit.PrintLevel(-1))
##    if VERBOSE: print "********** Fit result [X MASS Vjet SR] ***", category, "*"*40, "\n", frVjetSR.Print(), "\n", "*"*80
##    frVjetSB = model["VjetSB"].fitTo(setVjetSB, RooFit.SumW2Error(True), RooFit.Range("X_reasonable_range"), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Save(1), RooFit.PrintLevel(-1))
##    if VERBOSE: print "********** Fit result [X MASS Vjet SB] ***", category, "*"*40, "\n", frVjetSB.Print(), "\n", "*"*80
##    frMainSB = model["MainSB"].fitTo(setDataSB, RooFit.SumW2Error(False), RooFit.Range("X_reasonable_range"), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Save(1), RooFit.PrintLevel(-1))
##    if VERBOSE: print "********** Fit result [X MASS Main SB] ***", category, "*"*40, "\n", frMainSB.Print(), "\n", "*"*80
#
##    for n in ["numVjetSR", "denVjetSR", "numVjetSB", "denVjetSR", "numMainSB", "denMainSB"]:
##        par[n].setMin(par[n].getVal()-par[n].getError())
##        par[n].setMax(par[n].getVal()+par[n].getError())
#        
## FIXME
##    # Set errors as uncertainties
##    for n in ["numTopSRErr", "denTopSRErr", "c0TopSRErr", "c1TopSRErr", "numVVSRErr", "denVVSRErr", "c0VVSRErr", "c1VVSRErr"]:
##        num = par[n.replace('Err', '')].getError()
##        den = par[n.replace('Err', '')].getVal()
##        par[n].setVal( min(abs(num / den) if den>0. else 0., 0.5) )
#
#    # Now fix the parameters of the sub-dominant backgrounds and background fractions
#    for n in [x for x in par.keys() if ('Top' in x or 'VV' in x)]:
#        if hasattr(par[n], "setConstant"): par[n].setConstant(True)
#
#    fMainSB.setConstant(True)
#    fTopSB.setConstant(True)
#    fVVSB.setConstant(True)
#    fMainSR.setConstant(True)
#    fTopSR.setConstant(True)
#    fVVSR.setConstant(True)
#
#    # PART 3: fit simultaneously data SB and the dominant background in the SB and SR, with top and VV fixed
#
#    #*******************************************************#
#    #                                                       #
#    #   2: fit simultaneously data SB and the dominant      #
#    #  background in the SB and SR, with top and VV fixed   #
#    #                                                       #
#    #*******************************************************#
#
#    # define the three categories (not ranges) to be used in the fit
#    reg = RooCategory("reg", "reg")
#    reg.defineType("mcSR")
#    reg.defineType("mcSB")
#    reg.defineType("dataSB")
#    # combine all the datasets with the corresponding categories together in one big sample
#    setMulti = RooDataSet("setMulti", "setMulti", variables, RooFit.Index(reg), RooFit.WeightVar(weight), RooFit.Import("mcSR", setVjetSR), RooFit.Import("mcSB", setVjetSB), RooFit.Import("dataSB", setDataSB))
#
#    # define the simultaneous object by linking to the big-dataset the three PDF that will be used in each of the regions
#    simObj = RooSimultaneous("simObj", "simultaneous pdf", RooArgList(model["VjetSR"], model["VjetSB"], model["BkgSB"]), reg)
#
#    frSim = simObj.fitTo(setMulti, RooFit.Range("X_reasonable_range"), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Minos(True), RooFit.SumW2Error(True), RooFit.Save(1), RooFit.PrintLevel(-1))
#    # Print
#    if VERBOSE: print "********** Fit result [SIMULTANEOUS] ***", category, "*"*40, "\n", frSim.Print(), "\n", "*"*80
#    if VERBOSE: frSim.correlationMatrix().Print()
#
#    # Perform alternative simultaneous fit
#    simObj2 = RooSimultaneous("simObj2", "alternative simultaneous pdf", RooArgList(model["VjetSR2"], model["VjetSB2"], model["BkgSB2"]), reg)
#    frSim2 = simObj2.fitTo(setMulti, RooFit.Range("X_reasonable_range"), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.SumW2Error(True), RooFit.Save(1), RooFit.PrintLevel(-1))
#    if VERBOSE: print "********** Fit result [SIMULTANEOUS 2] ***", category, "*"*40, "\n", frSim2.Print(), "\n", "*"*80
#
#    # Now fix also V+jets in SB and SR, and the main background in SB and the sum of the backgrounds in SB
#    for n in [x for x in par.keys() if 'Vjet' in x or 'MainSB' in x or 'BkgSB' in x]: par[n].setConstant(True)
#
#    drawPlot("VjetSB", category, X_mass, simObj, setMulti, [frSim], -1, reg, "mcSB", model["VjetSB2"], setVjetSB.sumEntries())
#    drawPlot("VjetSR", category, X_mass, simObj, setMulti, [frSim], -1, reg, "mcSR", model["VjetSR2"], setVjetSR.sumEntries())
#    drawPlot("BkgSB", category, X_mass, simObj, setMulti, [frSim, frTopSB, frVVSB], setDataSB.sumEntries(), reg, "dataSB", model["BkgSB2"], setDataSB.sumEntries())
#
#    drawAlphaPlot("alpha", category, X_mass, alpha, model["BkgSB"], model["BkgSR"], frSim, alpha2, model["BkgSB2"], model["BkgSR2"], frSim2, RatioSRSB)
#
#    drawPlot("BkgSR", category, X_mass, model["BkgSR"], setDataSR if not BLIND else None, [frSim, frTopSR, frVVSR], BkgYield)
#
#    if SCAN:
#        likelihoodScan(model["VjetSR"], setVjetSR, [par["denVjetSR"], par["numMainSB"]])
#
#    if DIJET:
#        par_p0 = RooRealVar("Bkg_norm", "Number of background events", BkgYield, 0., 1.e10)
#        par_p1 = RooRealVar(PREFIX+category+"_p1", "p1", 6, -1000., 1000.)
#        par_p2 = RooRealVar(PREFIX+category+"_p2", "p2", 1, -200., 1000.)
#        modelBkg = RooGenericPdf("Bkg", "POW2", "pow(1-@0/13000, @1) / pow(@0/13000, @2)", RooArgList(X_mass, par_p1, par_p2))
#        frBkg = modelBkg.fitTo(setDataSR, RooFit.Range("X_reasonable_range"), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.SumW2Error(False), RooFit.Save(1), RooFit.PrintLevel(-1))
#        if VERBOSE: print "********** Fit result [DIJET] ***", category, "*"*40, "\n", frBkg.Print(), "\n", "*"*80
#        drawPlot("Dijet", category, X_mass, modelBkg, setDataSR, [frBkg], BkgYield)
#        par_p0.setConstant(True)
#
#    # Money plot
#    signal = getSignal(category, stype, 2000)
#    drawPlot("BkgSR_"+category, category, X_mass, model["BkgSR"], setDataSR if not BLIND else None, [frSim, frTopSR, frVVSR], BkgYield, None, "", model["BkgSR2"], BkgYield2, signal[0], signal[1]*signal[2] )
#
##    # SECONDARY backgrounds shape uncertainties
#
##    # Part 1: define RooRealVar and assign fixed values
##    for n in ["Top_"+category+"_p0_fit", "Top_"+category+"_p1_fit", "Top_p0_jes", "Top_p0_QCD_scale", "VV_"+category+"_p0_fit", "VV_"+category+"_p1_fit", "VV_p0_jes", "VV_p0_QCD_scale"]:
##        par[PREFIX+n] = RooRealVar(PREFIX+n, "fit uncertainties for Secondary Bkg shape", 0., -10, 10) # flag in the datacard
##        par[n] = RooRealVar(n, "fit uncertainties for Secondary Bkg shape", 0., -1.e6, 1.e6) # uncertainty value
##        par[PREFIX+n].setConstant(True)
##        par[n].setConstant(True)
#
##    par["Top_p0_jes"].setVal(0.0008)
##    par["VV_p0_jes"].setVal(0.0002)
##    par["Top_p0_QCD_scale"].setVal(0.0004)
##    par["VV_p0_QCD_scale"].setVal(0.0003)
#
##    # Part 2: copy fitted parameters and errors
##    if functions[category]["Shape"] == "EXPN":
##        par["Top_"+category+"_p0"] = RooRealVar("Top_"+category+"_p0", "Top background p0", par["numTopSR"].getVal(), par["numTopSR"].getMin(), par["numTopSR"].getMax())
##        par["Top_"+category+"_p1"] = RooRealVar("Top_"+category+"_p1", "Top background p1", par["denTopSR"].getVal(), par["denTopSR"].getMin(), par["denTopSR"].getMax())
##        par["VV_"+category+"_p0"] = RooRealVar("VV_"+category+"_p0", "VV background p0", par["numVVSR"].getVal(), par["numVVSR"].getMin(), par["numVVSR"].getMax())
##        par["VV_"+category+"_p1"] = RooRealVar("VV_"+category+"_p1", "VV background p1", par["denVVSR"].getVal(), par["denVVSR"].getMin(), par["denVVSR"].getMax())
##        par["Top_"+category+"_p0_fit"].setVal( par["numTopSR"].getError()/par["numTopSR"].getVal() if not par["numTopSR"].getVal() == 0. else 0. )
##        par["Top_"+category+"_p1_fit"].setVal( par["denTopSR"].getError()/par["denTopSR"].getVal() if not par["denTopSR"].getVal() == 0. else 0. )
##        par["VV_"+category+"_p0_fit"].setVal( par["numVVSR"].getError()/par["numVVSR"].getVal() if not par["numVVSR"].getVal() == 0. else 0. )
##        par["VV_"+category+"_p1_fit"].setVal( par["denVVSR"].getError()/par["denVVSR"].getVal() if not par["denVVSR"].getVal() == 0. else 0. )
##    elif functions[category]["Shape"] == "EXPTAIL":
##        par["Top_"+category+"_p0"] = RooRealVar("Top_"+category+"_p0", "Top background p0", par["c0TopSR"].getVal(), par["c0TopSR"].getMin(), par["c0TopSR"].getMax())
##        par["Top_"+category+"_p1"] = RooRealVar("Top_"+category+"_p1", "Top background p1", par["c1TopSR"].getVal(), par["c1TopSR"].getMin(), par["c1TopSR"].getMax())
##        par["VV_"+category+"_p0"] = RooRealVar("VV_"+category+"_p0", "VV background p0", par["c0VVSR"].getVal(), par["c0VVSR"].getMin(), par["c0VVSR"].getMax())
##        par["VV_"+category+"_p1"] = RooRealVar("VV_"+category+"_p1", "VV background p1", par["c1VVSR"].getVal(), par["c1VVSR"].getMin(), par["c1VVSR"].getMax())
##        par["Top_"+category+"_p0_fit"].setVal( par["c0TopSR"].getError()/par["c0TopSR"].getVal() if not par["c0TopSR"].getVal() == 0. else 0. )
##        par["Top_"+category+"_p1_fit"].setVal( par["c1TopSR"].getError()/par["c1TopSR"].getVal() if not par["c1TopSR"].getVal() == 0. else 0. )
##        par["VV_"+category+"_p0_fit"].setVal( par["c0VVSR"].getError()/par["c0VVSR"].getVal() if not par["c0VVSR"].getVal() == 0. else 0. )
##        par["VV_"+category+"_p1_fit"].setVal( par["c1VVSR"].getError()/par["c1VVSR"].getVal() if not par["c1VVSR"].getVal() == 0. else 0. )
##    elif functions[category]["Shape"] == "POW2":
##        par["Top_"+category+"_p0"] = RooRealVar("Top_"+category+"_p0", "Top background p0", par["p0TopSR"].getVal(), par["p0TopSR"].getMin(), par["p0TopSR"].getMax())
##        par["Top_"+category+"_p1"] = RooRealVar("Top_"+category+"_p1", "Top background p1", par["p1TopSR"].getVal(), par["p1TopSR"].getMin(), par["p1TopSR"].getMax())
##        par["VV_"+category+"_p0"] = RooRealVar("VV_"+category+"_p0", "VV background p0", par["p0VVSR"].getVal(), par["p0VVSR"].getMin(), par["p0VVSR"].getMax())
##        par["VV_"+category+"_p1"] = RooRealVar("VV_"+category+"_p1", "VV background p1", par["p1VVSR"].getVal(), par["p1VVSR"].getMin(), par["p1VVSR"].getMax())
##        par["Top_"+category+"_p0_fit"].setVal( par["p0TopSR"].getError()/par["p0TopSR"].getVal() if not par["p0TopSR"].getVal() == 0. else 0. )
##        par["Top_"+category+"_p1_fit"].setVal( par["p1TopSR"].getError()/par["p1TopSR"].getVal() if not par["p1TopSR"].getVal() == 0. else 0. )
##        par["VV_"+category+"_p0_fit"].setVal( par["p0VVSR"].getError()/par["p0VVSR"].getVal() if not par["p0VVSR"].getVal() == 0. else 0. )
##        par["VV_"+category+"_p1_fit"].setVal( par["p1VVSR"].getError()/par["p1VVSR"].getVal() if not par["p1VVSR"].getVal() == 0. else 0. )
##    else:
##        print "  ERROR! Pdf", functions[category]["Shape"], "is not implemented"
##        exit()
#
##    print "-------------------", par["Top_"+category+"_p0_fit"].getVal(), par["Top_"+category+"_p1_fit"].getVal(), par["VV_"+category+"_p0_fit"].getVal(), par["VV_"+category+"_p1_fit"].getVal(), par["denVVSR"].getError(), frVVSR.correlationMatrix()(0, 0), frVVSR.correlationMatrix()(1, 1)
#
##    for s in ["Top_"+category+"_p0_fit", "Top_"+category+"_p1_fit", "VV_"+category+"_p0_fit", "VV_"+category+"_p1_fit"]:
##        if abs(par[s].getVal()) > 0.3:
##            print "  WARNING: par", s, "has value", par[s].getVal(), "is forced within boundary"
##            par[s].setVal(0.3)
#
#
##    # Part 3: build up formulas
##    par["Top_"+category+"_p0_sys"] = RooFormulaVar("Top_"+category+"_p0_sys", "@0*(1 + @1*@2 + @3*@4 + @4*@5)", RooArgList(par["Top_"+category+"_p0"], par["Top_"+category+"_p0_fit"], par[PREFIX+"Top_"+category+"_p0_fit"], par["Top_p0_jes"], par[PREFIX+"Top_p0_jes"], par["Top_p0_QCD_scale"], par[PREFIX+"Top_p0_QCD_scale"]))
##    par["Top_"+category+"_p1_sys"] = RooFormulaVar("Top_"+category+"_p1_sys", "@0*(1 + @1*@2)", RooArgList(par["Top_"+category+"_p1"], par["Top_"+category+"_p1_fit"], par[PREFIX+"Top_"+category+"_p1_fit"]))
##    par["VV_"+category+"_p0_sys"] = RooFormulaVar("VV_"+category+"_p0_sys", "@0*(1 + @1*@2 + @3*@4 + @4*@5)", RooArgList(par["VV_"+category+"_p0"], par["VV_"+category+"_p0_fit"], par[PREFIX+"VV_"+category+"_p0_fit"], par["VV_p0_jes"], par[PREFIX+"VV_p0_jes"], par["VV_p0_QCD_scale"], par[PREFIX+"VV_p0_QCD_scale"]))
##    par["VV_"+category+"_p1_sys"] = RooFormulaVar("VV_"+category+"_p1_sys", "@0*(1 + @1*@2)", RooArgList(par["VV_"+category+"_p1"], par["VV_"+category+"_p1_fit"], par[PREFIX+"VV_"+category+"_p1_fit"]))
#
##    # Part 4: redefine secondary backgrounds pdfs
##    if functions[category]["Shape"] == "EXPN":
##        model["Top_"+category] = RooExpNPdf("Top_"+category, "Top ExpN", X_mass, par["Top_"+category+"_p0_sys"], par["Top_"+category+"_p1_sys"])
##        model["VV_"+category] = RooExpNPdf("VV_"+category, "VV ExpN", X_mass, par["VV_"+category+"_p0_sys"], par["VV_"+category+"_p1_sys"])
##    elif functions[category]["Shape"] == "EXPTAIL":
##        model["Top_"+category] = RooExpTailPdf("Top_"+category, "Top ExpTail", X_mass, par["Top_"+category+"_p0_sys"], par["Top_"+category+"_p1_sys"])
##        model["VV_"+category] = RooExpTailPdf("VV_"+category, "VV ExpTail", X_mass, par["VV_"+category+"_p0_sys"], par["VV_"+category+"_p1_sys"])
##    elif functions[category]["Shape"] == "POW2":
##        model["Top_"+category] = RooGenericPdf("Top_"+category, "Top POW2", "pow(1-@0/13000, @1) / pow(@0/13000, @2)", RooArgList(X_mass, par["Top_"+category+"_p0_sys"], par["Top_"+category+"_p1"]))
##        model["VV_"+category] = RooGenericPdf("VV_"+category, "VV POW2", "pow(1-@0/13000, @1) / pow(@0/13000, @2)", RooArgList(X_mass, par["VV_"+category+"_p0_sys"], par["VV_"+category+"_p1_sys"]))
##    else:
##        print "  ERROR! Pdf", functions[category]["Shape"], "is not implemented"
##        exit()
#
##    plotSys("SysTop_JES", category, X_mass, model["Top_"+category], par[PREFIX+"Top_p0_jes"])
##    plotSys("SysTop_Scale", category, X_mass, model["Top_"+category], par[PREFIX+"Top_p0_QCD_scale"])
##    plotSys("SysVV_JES", category, X_mass, model["VV_"+category], par[PREFIX+"Top_p0_jes"])
##    plotSys("SysVV_Scale", category, X_mass, model["VV_"+category], par[PREFIX+"VV_p0_QCD_scale"])
#
#
#
#    # Block everything
#    for n, p in par.iteritems():
#        if hasattr(par[n], "setConstant"):
#            p.setConstant(True)
#            # Boundaries consistency check
#            if p.getMax() < p.getVal() or p.getMin() > p.getVal():
#                print "WARNING: in category", category, " parameter", n, "is outside the boudaries"
#                p.setVal( min(max(p.getVal(), p.getMin()), p.getMax()) )
#
#    if EXTRAPOLATE or SCAN: exit()
#
#    #*******************************************************#
#    #                                                       #
#    #                    Signal shape                       #
#    #                                                       #
#    #*******************************************************#
#
#    setSignal = {}
#    tmean  = {}
#    tsigma = {}
#    smean  = {}
#    ssigma = {}
#    salpha = {}
#    sslope = {}
#    sbrwig = {}
#    signal = {}
#    signalExt = {}
#    signalYield = {}
#    frSignal = {}
#
#    # Signal shape uncertainties (common amongst all mass points)
#    # xmean_e = RooRealVar("mean_scale_e", "Variation of the resonance mass position with the electron energy scale", 0.005, -1., 1.)
#    # smean_e = RooRealVar(PREFIX+"sig_p1_scale_e", "Change of the resonance mass position with the electron energy scale", 0, -10, 10)
#    # xmean_m = RooRealVar("mean_scale_m", "Variation of the resonance mass position with the muon energy scale", 0.113, -1., 1.)
#    # smean_m = RooRealVar(PREFIX+"sig_p1_scale_m", "Change of the resonance mass position with the muon energy scale", 0, -10, 10)
#    # xmean_jes = RooRealVar("mean_scale_jes", "Variation of the resonance mass position with the jet energy scale", 0.01, -1., 1.) #0.001
#    # smean_jes = RooRealVar(PREFIX+"sig_p1_jes", "Change of the resonance mass position with the jet energy scale", 0, -10, 10)
#    #
#    # xsigma_e = RooRealVar("sigma_scale_e", "Variation of the resonance mass width with the electron energy scale", 0.004, -1., 1.)
#    # ssigma_e = RooRealVar(PREFIX+"sig_p2_scale_e", "Change of the resonance mass width with the electron energy scale", 0, -10, 10)
#    # xsigma_m = RooRealVar("sigma_scale_m", "Variation of the resonance mass width with the muon energy scale", 0.104, -1., 1.)
#    # ssigma_m = RooRealVar(PREFIX+"sig_p2_scale_m", "Change of the resonance mass width with the muon energy scale", 0, -10, 10)
#    # xsigma_jes = RooRealVar("sigma_scale_jes", "Variation of the resonance mass width with the jet energy scale", 0.01, -1., 1.) #0.001
#    # ssigma_jes = RooRealVar(PREFIX+"sig_p2_jes", "Change of the resonance mass width with the jet energy scale", 0, -10, 10)
#    # xsigma_jer = RooRealVar("sigma_scale_jer", "Variation of the resonance mass width with the jet energy resolution", 0.01, -1., 1.)
#    # ssigma_jer = RooRealVar(PREFIX+"sig_p2_jer", "Change of the resonance mass width with the jet energy resolution", 0, -10, 10)
#    #
#    # xmean_e.setConstant(True)
#    # smean_e.setConstant(True)
#    # xmean_m.setConstant(True)
#    # smean_m.setConstant(True)
#    # xmean_jes.setConstant(True)
#    # smean_jes.setConstant(True)
#    #
#    # xsigma_e.setConstant(True)
#    # ssigma_e.setConstant(True)
#    # xsigma_m.setConstant(True)
#    # ssigma_m.setConstant(True)
#    # xsigma_jes.setConstant(True)
#    # ssigma_jes.setConstant(True)
#    # xsigma_jer.setConstant(True)
#    # ssigma_jer.setConstant(True)
#
#    binsSignal = RooBinning(Xbins*5, X_mass.getMin(), X_mass.getMax())
#    binsSignal.addUniform(Xbins*5, X_mass.getMin(), X_mass.getMax())
#
#
#    syst, syst_shape, syst_bkg, syst_sign = {}, {}, {}, {}
#
#    syst_trig = {'nnb'  : 0.030, 'nnbb' : 0.030, 'enb'  : 0.029, 'enbb' : 0.029, 'mnb'  : 0.035, 'mnbb' : 0.035, 'eeb'  : 0.029, 'eebb' : 0.029, 'mmb'  : 0.035, 'mmbb' : 0.035}
#    syst_elec = {'nnb'  : 0.010, 'nnbb' : 0.010, 'enb'  : 0.019, 'enbb' : 0.019, 'mnb'  : 0.000, 'mnbb' : 0.000, 'eeb'  : 0.036, 'eebb' : 0.036, 'mmb'  : 0.000, 'mmbb' : 0.000}
#    syst_muon = {'nnb'  : 0.010, 'nnbb' : 0.010, 'enb'  : 0.000, 'enbb' : 0.000, 'mnb'  : 0.045, 'mnbb' : 0.045, 'eeb'  : 0.000, 'eebb' : 0.000, 'mmb'  : 0.059, 'mmbb' : 0.059}
#    syst_taus = {'nnb'  : 0.030, 'nnbb' : 0.030, 'enb'  : 0.000, 'enbb' : 0.000, 'mnb'  : 0.000, 'mnbb' : 0.000, 'eeb'  : 0.000, 'eebb' : 0.000, 'mmb'  : 0.000, 'mmbb' : 0.000}
#    syst_mets = {'nnb'  : 0.010, 'nnbb' : 0.010, 'enb'  : 0.000, 'enbb' : 0.000, 'mnb'  : 0.000, 'mnbb' : 0.000, 'eeb'  : 0.000, 'eebb' : 0.000, 'mmb'  : 0.000, 'mmbb' : 0.000}
#
#    syst[PREFIX+"scale_mass"] = 0.010
#    syst[PREFIX+"res_mass"] = [-0.101, +0.112]
#    syst[PREFIX+"eff_H"] = 0.060
#    syst[PREFIX+"eff_b"] = { 800 : [1.028, 0.973],  1000 : [1.031, 0.970],  1100 : [1.033, 0.967],  1200 : [1.036, 0.965],  1300 : [1.039, 0.962],  1400 : [1.042, 0.959],  1500 : [1.044, 0.956],  1600 : [1.047, 0.954],  1700 : [1.049, 0.952],  1800 : [1.051, 0.950],  2000 : [1.054, 0.947],  2500 : [1.061, 0.941],  3000 : [1.065, 0.937],  3500 : [1.068, 0.934],  4000 : [1.070, 0.932],  4500 : [1.072, 0.931],  } if nBtag==2 else { 800 : [0.972, 1.027],  1000 : [0.968, 1.031],  1100 : [0.964, 1.035],  1200 : [0.960, 1.038],  1300 : [0.957, 1.041],  1400 : [0.954, 1.045],  1500 : [0.952, 1.046],  1600 : [0.950, 1.048],  1700 : [0.950, 1.048],  1800 : [0.949, 1.048],  2000 : [0.949, 1.048],  2500 : [0.952, 1.045],  3000 : [0.960, 1.037],  3500 : [0.967, 1.029],  4000 : [0.973, 1.023],  4500 : [0.978, 1.019],  }
#    syst[PREFIX+"eff_e"] = syst_elec[category]+syst_trig[category]
#    syst[PREFIX+"eff_m"] = syst_muon[category]+syst_trig[category]
#    syst[PREFIX+"eff_t"] = syst_taus[category]
#    syst[PREFIX+"eff_met"] = syst_mets[category]+syst_trig[category]
#    syst[PREFIX+"scale_pu"] = 0.001
#    syst[PREFIX+"scale_e"] = 0.010
#    syst[PREFIX+"scale_m"] = 0.010
#    syst["pdf_accept"] = 0.010
#    syst[PREFIX+"lumi"] = 0.025
#    syst["pdf_scale"] = { 1000 : [1.067, 0.933],  1100 : [1.068, 0.932],  1200 : [1.070, 0.930],  1300 : [1.073, 0.927],  1400 : [1.076, 0.924],  1500 : [1.079, 0.921],  1600 : [1.082, 0.918],  1700 : [1.085, 0.915],  1800 : [1.088, 0.912],  1900 : [1.092, 0.908],  2000 : [1.095, 0.905],  2100 : [1.100, 0.900],  2200 : [1.106, 0.894],  2300 : [1.111, 0.889],  2400 : [1.116, 0.884],  2500 : [1.121, 0.879],  2600 : [1.129, 0.871],  2700 : [1.137, 0.863],  2800 : [1.145, 0.855],  2900 : [1.153, 0.847],  3000 : [1.160, 0.840],  3100 : [1.173, 0.827],  3200 : [1.185, 0.815],  3300 : [1.197, 0.803],  3400 : [1.210, 0.790],  3500 : [1.222, 0.778],  3600 : [1.244, 0.756],  3700 : [1.265, 0.735],  3800 : [1.287, 0.713],  3900 : [1.309, 0.691],  4000 : [1.330, 0.670],  4100 : [1.361, 0.639],  4200 : [1.392, 0.608],  4300 : [1.423, 0.577],  4400 : [1.453, 0.547],  4500 : [1.484, 0.516],  }
#    syst["qcd_scale"] = { 1000 : [1.039, 0.963],  1100 : [1.045, 0.958],  1200 : [1.050, 0.954],  1300 : [1.054, 0.950],  1400 : [1.059, 0.947],  1500 : [1.063, 0.944],  1600 : [1.067, 0.940],  1700 : [1.070, 0.938],  1800 : [1.074, 0.935],  1900 : [1.077, 0.932],  2000 : [1.080, 0.930],  2100 : [1.083, 0.927],  2200 : [1.086, 0.925],  2300 : [1.089, 0.922],  2400 : [1.092, 0.920],  2500 : [1.096, 0.917],  2600 : [1.098, 0.915],  2700 : [1.101, 0.913],  2800 : [1.104, 0.911],  2900 : [1.107, 0.909],  3000 : [1.109, 0.907],  3100 : [1.112, 0.905],  3200 : [1.114, 0.903],  3300 : [1.117, 0.901],  3400 : [1.120, 0.899],  3500 : [1.122, 0.897],  3600 : [1.124, 0.896],  3700 : [1.126, 0.894],  3800 : [1.129, 0.893],  3900 : [1.131, 0.891],  4000 : [1.133, 0.889],  4100 : [1.135, 0.888],  4200 : [1.137, 0.887],  4300 : [1.138, 0.886],  4400 : [1.140, 0.885],  4500 : [1.142, 0.883],  }
#    
#    syst_shape[PREFIX+"sig_p1_scale_e"] = 1. #0.001
#    syst_shape[PREFIX+"sig_p1_scale_m"] = 1. #0.001
#    syst_shape[PREFIX+"sig_p1_jes"] = 1. #0.010
#    syst_shape[PREFIX+"sig_p2_scale_e"] = 1. #0.001
#    syst_shape[PREFIX+"sig_p2_scale_m"] = 1. #0.040
#    syst_shape[PREFIX+"sig_p2_jes"] = 1. #0.010
#    syst_shape[PREFIX+"sig_p2_jer"] = 1. #0.020
#    syst_shape[PREFIX+"sig_p1_fit"] = 1.
#    syst_shape[PREFIX+"sig_p2_fit"] = 1.
#    syst_shape[PREFIX+"sig_p3_fit"] = 1.
#    syst_shape[PREFIX+"sig_p4_fit"] = 1.
#    
#    # the alpha method is now done.
#    for m in massPoints:
#        signalName = "%s%s_M%d" % (stype, category, m)
#
#        #*******************************************************#
#        #                                                       #
#        #                      Datacard                         #
#        #                                                       #
#        #*******************************************************#
#        # now let's wrap things up and put together a datacard
#
##        # y = y0 + (y1-y0)*(x-x0)/(x1-x0)
##        CMS_eff_e = 0.010 if nElec==0 else (0.02 if nElec==1 else 0.04)
##        CMS_eff_m = 0.010 if nMuon==0 else (0.02 if nMuon==1 else 0.04)
##        CMS_eff_t = 0.030 if nLept<2 else 0.
##        CMS_eff_b = -( 0.02 + (0.04-0.02)*(m-1000.)/(4000.-1000.) ) if nBtag==1 else 0.07 + (0.03-0.07)*(m-1000.)/(4000.-1000.) # Anticorrelated 1 and 2 b-tags
##        CMS_scale_j = 0.01 + (0.03-0.01)*(m-1000.)/(4000.-1000.)
##        CMS_res_j = 0.02 + (0.03-0.02)*(m-1000.)/(4000.-1000.)
##        #QCD_scale = 0.04 + (0.12-0.04)*(m-1000.)/(4000.-1000.)
##        pdf_xsec = ((1.481023E-12*m*m*m + 0.04084374) if 'Z' in channel else (6.202152E-16*m*m*m*m + 0.03953903))
#
#        card  = "imax 1\n"
#        card += "jmax *\n"
#        card += "kmax *\n"
#        card += "-----------------------------------------------------------------------------------\n"
#        card += "shapes            %-15s  %-5s    %s%s.root    %s\n" % (signalName, category, WORKDIR, channel, "VH_2016:$PROCESS")
#        card += "shapes            %-15s  %-5s    %s%s.root    %s\n" % ("Vjets_"+category, category, WORKDIR, category, "VH_2016:$PROCESS")
#        card += "shapes            %-15s  %-5s    %s%s.root    %s\n" % ("Top_"+category, category, WORKDIR, category, "VH_2016:$PROCESS")
#        card += "shapes            %-15s  %-5s    %s%s.root    %s\n" % ("VV_"+category, category, WORKDIR, category, "VH_2016:$PROCESS")
#        card += "shapes            %-15s  %-5s    %s%s.root    %s\n" % ("data_obs", category, WORKDIR, category, "VH_2016:data_obs")
#        card += "-----------------------------------------------------------------------------------\n"
#        card += "bin               %s\n" % category
#        card += "observation       %s\n" % "-1.0"
#        card += "-----------------------------------------------------------------------------------\n"
#        card += "bin                                               %-20s%-20s%-20s%-20s\n" % (category, category, category, category)
#        card += "process                                           %-20s%-20s%-20s%-20s\n" % (signalName, "Vjets_"+category, "Top_"+category, "VV_"+category)
#        card += "process                                           %-20s%-20s%-20s%-20s\n" % ("0", "1", "2", "3")
#        card += "rate                                              %-20f%-20f%-20f%-20f\n" % (1, MainYield, TopYield, VVYield)
#        card += "-----------------------------------------------------------------------------------\n"
#        card += "%-35s     lnN       %-20s%-20.3f%-20.3s%-20.3s\n" % (PREFIX+"Vjets_"+category+"_norm", "-", (1.+MainYieldErr/MainYield), "-", "-")
#        card += "%-35s     lnN       %-20s%-20.3f%-20.3s%-20.3s\n" % (PREFIX+"Vjets_"+category+"_altf", "-", (1.+MainYieldAlt/MainYield), "-", "-")
#        card += "%-35s     lnN       %-20s%-20.3s%-20.3f%-20.3s\n" % (PREFIX+"Top_"+category+"_norm",  "-", "-", (1.+TopYieldErr/TopYield), "-")
#        card += "%-35s     lnN       %-20s%-20.3s%-20.3s%-20.3f\n" % (PREFIX+"VV_"+category+"_norm",   "-", "-", "-", (1.+VVYieldErr/VVYield))
#        card += "%-35s     lnN       %-20s%-20.3s%-20.3f%-20.3s\n" % (PREFIX+"Top_"+category+"_sf",  "-", "-", (1.+topSF[category][1]/topSF[category][0]), "-")
#        card += "%-35s     lnN       %-20.3f%-20s%-20.3f%-20.3f\n" % (PREFIX+"eff_b",    1.-(0.007 if nLept<2 else 0.), "-", 1.-0.029, 1.-0.007+(0.038 if nBtag<2 else 0.052))
#        card += "%-35s     lnN       %-20s%-20.3s%-20.3f%-20.3f\n" % (PREFIX+"eff_e",   "-", "-", 1.+syst_elec[category], 1.+syst_elec[category]+syst_trig[category])
#        card += "%-35s     lnN       %-20s%-20.3s%-20.3f%-20.3f\n" % (PREFIX+"eff_m",   "-", "-", 1.+syst_muon[category], 1.+syst_muon[category]+syst_trig[category])
#        card += "%-35s     lnN       %-20s%-20.3s%-20.3s%-20.3f\n" % (PREFIX+"eff_t",   "-", "-", "-", 1.+syst_taus[category])
#        card += "%-35s     lnN       %-20s%-20.3s%-20.3s%-20.3f\n" % (PREFIX+"eff_met",   "-", "-", "-", 1.+syst_mets[category]+syst_trig[category])
#        card += "%-35s     lnN       %-20s%-20.3s%-20.3s%-20.3f\n" % (PREFIX+"scale_mass",   "-", "-", "-", 1.+0.063)
#        card += "%-35s     lnN       %-20s%-20.3s%-20.3s%-20.3f\n" % (PREFIX+"res_mass",   "-", "-", "-", 1.+0.063)
#        card += "%-35s     lnN       %-20s%-20.3s%-20.3s%-20.3f\n" % (PREFIX+"scale_pu",   "-", "-", "-", 1.+0.010)
#        card += "%-35s     lnN       %-20s%-20.3s%-20.3s%-20.3f\n" % (PREFIX+"lumi",   "-", "-", "-", 1.+0.025)
#        card += "%-35s     lnN       %-20s%-20.3s%-20.3f%-20.3f\n" % ("pdf_accept",  "-", "-", 1.001, 1.+0.017)
#        card += "%-35s     lnN       %-20s%-20.3s%-20.3f%-20.3f\n" % ("pdf_scale",   "-", "-", 1.001, 1.+0.022+0.020)
#        card += "%-35s     lnN       %-20s%-20.3s%-20.3f%-20.3f\n" % ("qcd_scale",   "-", "-", 1.010, 1.+0.025+0.164)
#
#        # normalization systematics for the signal
#        for s in sorted(syst):
#            if type(syst[s]) == dict:
#                sy = syst[s].get(m, syst[s][min(syst[s].keys(), key=lambda k: abs(k-m))])
#                card += "%-35s     lnN       %-20s%-20s%-20s%-20s\n" % (s.replace('_migration', ''), "%.3f/%.3f" % (sy[0], sy[1]), "-", "-", "-")
#            elif type(syst[s]) == list: card += "%-35s     lnN       %-20s%-20s%-20s%-20s\n" % (s, "%.3f/%.3f" % (1.+syst[s][0], 1.+syst[s][1]), "-", "-", "-")
#            else: card += "%-35s     lnN       %-20.3f%-20s%-20s%-20s\n" % (s,    1.+syst[s], "-", "-", "-")
#        # shape systematics for the signal
#        for s in sorted(syst_shape): card += "%-35s     param     %-20.1f%-20.1f\n" % (s, 0., syst_shape[s])
#
##        card += "%-35s     lnN       %-20.3f%-20s%-20.3f%-20.3f\n" % (PREFIX+"eff_e",    1.+CMS_eff_e, "-", 1.+CMS_eff_e if nLept>=2 else 1., 1.+CMS_eff_e)
##        card += "%-35s     lnN       %-20.3f%-20s%-20.3f%-20.3f\n" % (PREFIX+"eff_m",    1.+CMS_eff_m, "-", 1.+CMS_eff_m if nLept>=2 else 1., 1.+CMS_eff_m)
##        card += "%-35s     lnN       %-20.3f%-20s%-20.3s%-20.3f\n" % (PREFIX+"eff_t",    1.+CMS_eff_t if nLept<2 else 1., "-", "-", 1.+CMS_eff_t if nLept<2 else 1.)
##        #card += "%-35s     lnN       %-20.3f%-20s%-20.3f%-20.3f\n" % (PREFIX+"eff_b",    1.+CMS_eff_b, "-", shapesys[channel]['CMS_eff_b']['Top'][0], shapesys[channel]['CMS_eff_b']['VV'][0])
##        #card += "%-35s     lnN       %-20.3f%-20s%-20.3f%-20.3f\n" % (PREFIX+"scale_j",  1.+CMS_scale_j, "-", shapesys[channel]['CMS_scale_j']['Top'][0], shapesys[channel]['CMS_scale_j']['VV'][0])
##        card += "%-35s     lnN       %-20.3f%-20s%-20.3s%-20.3s\n" % (PREFIX+"res_j",  1.+CMS_res_j, "-", "-", "-")
##        card += "%-35s     lnN       %-20.3f%-20s%-20.3s%-20.3f\n" % (PREFIX+"scale_met", 1.010 if nLept==0 else 1., "-", "-", 1.003 if nLept==0 else 1.)
##        card += "%-35s     lnN       %-20.3f%-20s%-20.3s%-20.3f\n" % (PREFIX+"res_met", 1.010 if nLept==0 else 1., "-", "-", 1.010 if nLept==0 else 1.)
##        card += "%-35s     lnN       %-20.3f%-20s%-20.3f%-20.3f\n" % (PREFIX+"scale_pu", 1.030, "-", 1.030 if nLept>=2 else 1., 1.030)
##        #card += "%-35s     lnN       %-20.3f%-20s%-20.3f%-20.3f\n" % ("QCD_scale",    1.+QCD_scale, "-", shapesys[channel]['QCD_scale']['Top'][0], shapesys[channel]['QCD_scale']['VV'][0])
##        card += "%-35s     lnN       %-20.3f%-20s%-20.3f%-20.3f\n" % ("pdf_accept",          1.030, "-", 1.002 if nLept>=2 else 1., 1.002)
##        #card += "%-35s     lnN       %-20.3f%-20s%-20.3s%-20.3s\n" % ("pdf_xsec",            1.+pdf_xsec, "-", "-", "-")
##        card += "%-35s     lnN       %-20.3f%-20s%-20.3f%-20.3f\n" % ("lumi",   1.046, "-", 1.046 if nLept>=2 else 1., 1.046)
#        # Main background shape uncertainties
#        for i in range(6):
#            card += "%-35s     param     %-20.1f%-20.1f\n" % (PREFIX+"Vjets_"+category+"_eig%d" % i, 0., 1.)
#        # Secondary background shape uncertainties
#        for i in range(2):
#            card += "%-35s     param     %-20.1f%-20.1f\n" % (PREFIX+"Top_"+category+"_eig%d" % i, 0., 1.)
#        for i in range(2):
#            card += "%-35s     param     %-20.1f%-20.1f\n" % (PREFIX+"VV_"+category+"_eig%d" % i, 0., 1.)
##        for n in [PREFIX+"Top_"+category+"_p0_fit", PREFIX+"Top_"+category+"_p1_fit", PREFIX+"Top_p0_jes", PREFIX+"Top_p0_QCD_scale", PREFIX+"VV_"+category+"_p0_fit", PREFIX+"VV_"+category+"_p1_fit", PREFIX+"VV_p0_jes", PREFIX+"VV_p0_QCD_scale"]:
##        for n in [PREFIX+"Top_p0_jes", PREFIX+"Top_p0_QCD_scale", PREFIX+"VV_p0_jes", PREFIX+"VV_p0_QCD_scale"]:
##            card += "%-35sparam     %-20.1f%-20.1f\n" % (n, 0., 1.)
#
#        # , PREFIX+"sig_p1_scale_e", PREFIX+"sig_p2_scale_e", PREFIX+"sig_p1_scale_m", PREFIX+"sig_p2_scale_m", PREFIX+"sig_p1_jes", PREFIX+"sig_p2_jes", PREFIX+"sig_p2_jer"
#
#        card += "theory group = pdf_scale qcd_scale\n"
#        card += "norm group = "+PREFIX+"Vjets_"+category+"_norm "+PREFIX+"Vjets_"+category+"_altf\n"
#        card += "shape1 group = "
#        for i in range(6): card += PREFIX+"Vjets_"+category+"_eig%d " % i
#        card += "\n"
#        card += "shape2 group = "
#        for i in range(2): card += PREFIX+"Top_"+category+"_eig%d " % i + " " + PREFIX+"VV_"+category+"_eig%d " % i
#        card += "\n"
#        card += "shapeS group = "
#        for i in syst_shape.keys(): card += i + " "
#        card += "\n"
#
#        if DIJET:
#            card  = "imax 1\n"
#            card += "jmax *\n"
#            card += "kmax *\n"
#            card += "-----------------------------------------------------------------------------------\n"
#            card += "shapes            %-15s  %-5s    %s%s.root    %s\n" % (signalName, category, WORKDIR, channel, "VH_2016:$PROCESS")
#            card += "shapes            %-15s  %-5s    %s%s.root    %s\n" % ("Bkg", category, WORKDIR, category, "VH_2016:$PROCESS")
#            card += "shapes            %-15s  %-5s    %s%s.root    %s\n" % ("data_obs", category, WORKDIR, category, "VH_2016:data_obs")
#            card += "-----------------------------------------------------------------------------------\n"
#            card += "bin               %s\n" % category
#            card += "observation       %s\n" % "-1.0"
#            card += "-----------------------------------------------------------------------------------\n"
#            card += "bin                                     %-20s%-20s\n" % (category, category)
#            card += "process                                 %-20s%-20s\n" % (signalName, "Bkg")
#            card += "process                                 %-20s%-20s\n" % ("0", "1")
#            card += "rate                                    %-20f%-20f\n" % (1, 1)
#            card += "-----------------------------------------------------------------------------------\n"
#            for p in range(1, 3): card += "%-35s     flatParam\n" % (PREFIX+category+"_p%d" % p)
#            card += "%-35s     lnN       %-20s%-20.3f\n" % (PREFIX+category+"_norm", "-", (1.+TotalYieldErr/TotalYield))
#            #card += "%-35s     lnU       %-20s%-20.0f\n" % (PREFIX+category+"_norm",    "-", 4.)
#            for s in sorted(syst):
#                if type(syst[s]) == dict:
#                    sy = syst[s].get(m, syst[s][min(syst[s].keys(), key=lambda k: abs(k-m))])
#                    card += "%-35s     lnN       %-20s%-20s\n" % (s.replace('_migration', ''), "%.3f/%.3f" % (sy[0], sy[1]), "-")
#                elif type(syst[s]) == list: card += "%-35s     lnN       %-20s%-20s\n" % (s, "%.3f/%.3f" % (1.+syst[s][0], 1.+syst[s][1]), "-")
#                else: card += "%-35s     lnN       %-20.3f%-20s\n" % (s,    1.+syst[s], "-")
##            for n in [PREFIX+"sig_p1_scale_e", PREFIX+"sig_p2_scale_e", PREFIX+"sig_p1_scale_m", PREFIX+"sig_p2_scale_m", PREFIX+"sig_p1_jes", PREFIX+"sig_p2_jes", PREFIX+"sig_p2_jer"]:
##                if ('_e_' in n and nElec==0) or ('_m_' in n and nMuon==0): continue
##                card += "%-35s     param     %-20.1f%-20.1f\n" % (n, 0., 1.)
#            card += "theory group = pdf_scale qcd_scale\n"
#            card += "norm group = "+PREFIX+category+"_norm\n"
#            card += "shape1 group = "
#            for p in range(1, 3): card += PREFIX+category+"_p%d " % p
#            card += "\n"
#
#        
#
#        for s in signalList:
#            #if nLept==1 and s in ['AZh', 'BBAZh']: continue
#            if s == stype: outcard = card
#            else: outcard = card.replace(stype, s)
#            outname = CARDDIR+"alpha/%s%s_M%d.txt" % (s, category, m)
#            cardfile = open(outname, 'w')
#            cardfile.write(outcard)
#            cardfile.close()
#            if VERBOSE: print "Datacards for mass", m, "in channel", channel, "saved in", outname
#
#    # Summary signal plot
#    #drawMultiPlot("Signal", channel, X_mass, signal, [], signalYield)
#
#    # Generate pseudo data
##    if BLIND:
##        setDataSR = RooDataSet()
##        setDataSR.SetName("data_obs")
##        setDataSR = model["BkgSR"].generate(RooArgSet(X_mass), BkgYield)
#
#    #*******************************************************#
#    #                                                       #
#    #                   Generate workspace                  #
#    #                                                       #
#    #*******************************************************#
#
#    # Set supefine binning, otherwise combine goes nuts
#    #X_mass.setBins( int(X_mass.getMax() - X_mass.getMin()) )
#
#    # create workspace
#    w = RooWorkspace("VH_2016", "workspace")
#    # Dataset
#    getattr(w, "import")(setDataSR, RooFit.Rename("data_obs"))
#
#    # diagonalization
#    # the uncertainties are 0% or 100% correlated for the combine
#    # therefore we need to diagonalize the covariance matrix and extract the eigenvalues of it to get the 0% correlated sigmas
#    diago = PdfDiagonalizer(category, w, frSim, PREFIX+"Vjets_")
#    BkgSR_eig = diago.diagonalize(model["Vjets"])
#    getattr(w, "import")(BkgSR_eig, RooFit.Rename("Vjets_eig_"+category), RooFit.RecycleConflictNodes())
#    
#    model["Top"] = model["TopSR"].Clone("Top")
#    diago_Top = PdfDiagonalizer(category, w, frTopSR, PREFIX+"Top_")
#    TopSR_eig = diago_Top.diagonalize(model["Top"])
#    getattr(w, "import")(TopSR_eig, RooFit.Rename("Top_eig_"+category), RooFit.RecycleConflictNodes())
#    
#    model["VV"] = model["VVSR"].Clone("VV")
#    diago_VV = PdfDiagonalizer(category, w, frVVSR, PREFIX+"VV_")
#    VVSR_eig = diago_VV.diagonalize(model["VV"])
#    getattr(w, "import")(VVSR_eig, RooFit.Rename("VV_eig_"+category), RooFit.RecycleConflictNodes())
##    getattr(w, "import")(model["VVSR"], RooFit.Rename(model["VVSR"].GetName()))
#    
##    parameters = frSim.floatParsFinal()
##    n = parameters.getSize()
#
##    cov = TMatrixDSym(frSim.covarianceMatrix())
##    eigen = TMatrixDSymEigen(cov)
#
##    vectors = eigen.GetEigenVectors() # TMatrixD
##    values  = eigen.GetEigenValues() # TVectorD
#
##    eigenVars = RooArgList()
##    replacements = RooArgList()
##
##    # create unit gaussians per eigen-vector
##    for i in range(n): eigenVars.add(w.factory("%s_eig%d[-5,5]" % (category, i)))
##
##    # put them in a list, with a one at the end to set the mean
##    eigvVarsPlusOne = RooArgList(eigenVars)
##    if w.var("_one_") == 0: w.factory("_one_[1]")
##    eigvVarsPlusOne.add(w.var("_one_"))
#
##    # then go create the linear combinations
##    # each is equal to the transpose matrx times the square root of the eigenvalue (so that we get unit gaussians)
##    for i in range(n):
##        coeffs = RooArgList()
##        for j in range(n): coeffs.add(w.factory( "%s_eigCoeff_%d_%d[%g]" % (category, i, j, vectors(i,j)*math.sqrt(values(j))) ))
##        coeffs.add(w.factory( "%s_eigBase_%d[%g]" % (category, i, parameters.at(i).getVal()) ))
##        add = RooAddition("%s_eigLin_%d" % (category, i), "%s_eigLin_%d" % (category, i), RooArgList(coeffs), RooArgList(eigvVarsPlusOne))
##        getattr(w, "import")(add, RooFit.Rename(add.GetName()))
##        replacements.add(add)
##
##    pdf = model["Vjets"]
##    if not pdf.dependsOn(parameters): print "ERROR"
#
##    # now do the customization
##    custom = RooCustomizer(pdf, category)
##    for i in range(n):
##        if pdf.dependsOn(parameters[i]): custom.replaceArg(parameters[i], replacements[i])
#
##    ret = RooAbsPdf(custom.build())
##    ret.SetName(pdf.GetName() + "_" + category)
##    getattr(w, "import")(ret, RooFit.Rename("Vjets_eig_"+category), RooFit.RecycleConflictNodes())
#
#
##    getattr(w, "import")(model["Top_"+category], RooFit.Rename(model["Top_"+category].GetName()))
##    getattr(w, "import")(model["VV_"+category], RooFit.Rename(model["VV_"+category].GetName()))
#    getattr(w, "import")(model["BkgSR"], RooFit.Rename(model["BkgSR"].GetName()))
#    getattr(w, "import")(model["BkgSR2"], RooFit.Rename(model["BkgSR2"].GetName())) # FIXME
#
#    # number of events
#    getattr(w, "import")(nBkgSR, RooFit.Rename(nBkgSR.GetName()))
#
#    # fit results
#    getattr(w, "import")(frSim, True)
#    getattr(w, "import")(frTopSR, True)
#    getattr(w, "import")(frVVSR, True)
#
#    # mj
#    getattr(w, "import")(setDataSRSB, RooFit.Rename(setDataSRSB.GetName()))
#    getattr(w, "import")(setDataSRSBVR, RooFit.Rename(setDataSRSBVR.GetName()))
#    getattr(w, "import")(BkgMass, RooFit.Rename(BkgMass.GetName()))
#    getattr(w, "import")(BkgMassYield, RooFit.Rename(BkgMassYield.GetName()))
#    getattr(w, "import")(VjetMass2, RooFit.Rename(VjetMass2.GetName())) # for the alternate function
#    getattr(w, "import")(nVjet2, RooFit.Rename(nVjet2.GetName()))
#    getattr(w, "import")(frMass, True)
#
#    if DIJET:
#        w = RooWorkspace("VH_2016", "workspace")
#        getattr(w, "import")(setDataSR, RooFit.Rename("data_obs"))
#        getattr(w, "import")(par_p0, RooFit.Rename(modelBkg.GetName()+"_norm"))
#        getattr(w, "import")(modelBkg, RooFit.Rename(modelBkg.GetName()))
#
#    # save workspace
#    if VERBOSE: w.Print()
#    w.writeToFile("%s%s.root" % (WORKDIR, category), True)
#    print "Workspace", "%s%s.root" % (WORKDIR, category), "saved successfully with (internal/plot) binning", X_mass.getBins(), "/", X_mass.getBins("PLOT")
#
#
#    
#
#    # daje!
#
#    # Try also getattr(w, 'import')(ds, ROOT.RooCmdArg())
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
def drawPlot(name, channel, variable, model, dataset, fitRes=[], norm=-1, reg=None, cat="", alt=None, anorm=-1, signal=None, snorm=-1):
    isData = norm>0
    isMass = "Mass" in name
    isSignal = '_M' in name
    isCategory = reg is not None
    isBottomPanel = not isSignal
    postfix = "Mass" if isMass else ('SR' if 'SR' in name else ('SB' if 'SB' in name else ""))
#    VVTop_component =
#    VV_component = "VV"+postfix+""
#    Vjet_component = "Vjet"+postfix+""
#    VjetTop_component = "Vjet"+postfix+""+",Top"+postfix+""
    cut = "reg==reg::"+cat if reg is not None else ""
    normRange = "h_extended_reasonable_range" if isMass else "X_reasonable_range"
    dataRange = "LSBrange,HSBrange" if isMass and isData else normRange

    #if reg is None: cut = "((%s<%d && %s<%d) || (%s>%d && %s<%d))" % (variable.GetName(), LOWMIN, variable.GetName(), LOWMAX, variable.GetName(), HIGMIN, variable.GetName(), HIGMAX)
    cmsLabel = "Preliminary" if isData else "Simulation Preliminary"
    if not type(fitRes) is list: cmsLabel = "Preliminary"
    if 'paper' in name: cmsLabel = ""
    pullRange = 5
    #*(1. if not channel=="XZHeebb" else 1.25)

    dataMin, dataMax = array('d', [0.]), array('d', [0.])
    dataset.getRange(variable, dataMin, dataMax)
    xmin, xmax = dataMin[0], dataMax[0]

    lastBin = variable.getMax()
    if not isMass and not isSignal:
        if 'nn' in channel or 'll' in channel or 'ee' in channel or 'mm' in channel: lastBin = 3500.
        else: lastBin = 4500.
#    if isData and not signal==None and not isMass:
#        for n in range(variable.getBinning("PLOT").numBoundaries()):
#            b = variable.getBinning("PLOT").binHigh(n)
#            if b > xmax:
#                lastBin = b
#                break

    # print "Plotting", ("data" if isData else "MC"), "RooDataSet with", nevents, "events between [%.1f, %.1f]" % (xmin, xmax)

    # ====== CONTROL PLOT ======
    c = TCanvas("c_"+name, "Fitting "+name, 800, 800 if isBottomPanel else 600)
    if isBottomPanel:
        c.Divide(1, 2)
        setTopPad(c.GetPad(1), RATIO)
        setBotPad(c.GetPad(2), RATIO)
    else: setPad(c.GetPad(0))
    c.cd(1)
    frame = variable.frame()
    if isBottomPanel: setPadStyle(frame, 1.25, True)

    # Plot Data
    data, res = None, None
    if dataset is not None: data = dataset.plotOn(frame, RooFit.Cut(cut), RooFit.Binning(variable.getBinning("PLOT")), RooFit.DataError(RooAbsData.Poisson if isData else RooAbsData.SumW2), RooFit.Range(dataRange), RooFit.DrawOption("PE0"), RooFit.Name("data_obs"))
    if data is not None and isData: fixData(data.getHist(), True)

    # ---------- SIMPLE FIT ----------
    if isData:
        if isCategory:
            model.plotOn(frame, RooFit.Slice(reg, cat), RooFit.ProjWData(RooArgSet(reg), dataset), RooFit.DrawOption("F"), RooFit.LineColor(getColor(name, channel)), RooFit.FillColor(getColor(name, channel)), RooFit.FillStyle(1001), RooFit.VLines(), RooFit.Name("Vjet")) #RooFit.Normalization(norm, RooAbsReal.NumEvent), RooFit.Range(normRange), FIXME
            res = frame.pullHist()
            model.plotOn(frame, RooFit.Slice(reg, cat), RooFit.ProjWData(RooArgSet(reg), dataset), RooFit.Components("VV"+postfix+",Top"+postfix), RooFit.DrawOption("F"), RooFit.LineColor(798), RooFit.FillColor(798), RooFit.VLines(), RooFit.Name("Top"))
            model.plotOn(frame, RooFit.Slice(reg, cat), RooFit.ProjWData(RooArgSet(reg), dataset), RooFit.Components("VV"+postfix), RooFit.DrawOption("F"), RooFit.LineColor(602), RooFit.FillColor(602), RooFit.VLines(), RooFit.Name("VV"))
            if alt is not None: alt.plotOn(frame, RooFit.Normalization(anorm, RooAbsReal.NumEvent), RooFit.LineStyle(7), RooFit.LineColor(922), RooFit.Name("Alternate"))
            if type(fitRes) is list:
                for f in fitRes:
                    if f is not None: model.plotOn(frame, RooFit.Slice(reg, cat), RooFit.ProjWData(RooArgSet(reg), dataset), RooFit.VisualizeError(f, 1, False), RooFit.SumW2Error(True), RooFit.LineColor(0), RooFit.FillColor(1), RooFit.FillStyle(3002), RooFit.Name("Uncertainty"))
                    #model.paramOn(frame, RooFit.Label(model.GetTitle()), RooFit.Layout(0.5, 0.95, 0.94), RooFit.Format("NEAU")) #FIXME
            elif fitRes is not None: frame.addObject(fitRes, "E3")
        else:
            if isMass:
                model.plotOn(frame, RooFit.Normalization(norm, RooAbsReal.NumEvent), RooFit.Range(normRange), RooFit.LineColor(602), RooFit.DrawOption("F"), RooFit.FillColor(602), RooFit.FillStyle(1001), RooFit.VLines(), RooFit.Name("VV"))
                res = frame.pullHist()
                model.plotOn(frame, RooFit.Normalization(norm, RooAbsReal.NumEvent), RooFit.Range(normRange), RooFit.Components("Vjet"+postfix+",Top"+postfix), RooFit.LineColor(798), RooFit.DrawOption("F"), RooFit.FillColor(798), RooFit.FillStyle(1001), RooFit.VLines(), RooFit.Name("Top"))
                model.plotOn(frame, RooFit.Normalization(norm, RooAbsReal.NumEvent), RooFit.Range(normRange), RooFit.Components("Vjet"+postfix), RooFit.LineColor(getColor(name, channel)), RooFit.DrawOption("F"), RooFit.FillColor(getColor(name, channel)), RooFit.FillStyle(1001), RooFit.VLines(), RooFit.Name("Vjet"))
                if alt is not None: alt.plotOn(frame, RooFit.Normalization(anorm if anorm>0 else norm, RooAbsReal.NumEvent), RooFit.Range(normRange), RooFit.LineStyle(7), RooFit.LineColor(922), RooFit.Name("Alternate"))
                if type(fitRes) is list:
                    for f in fitRes:
                        if f is not None: model.plotOn(frame, RooFit.Normalization(norm, RooAbsReal.NumEvent), RooFit.Range(normRange), RooFit.VisualizeError(f, 1, False), RooFit.SumW2Error(True), RooFit.LineColor(0), RooFit.FillColor(1), RooFit.FillStyle(3002), RooFit.Name("Uncertainty"))
                        #model.paramOn(frame, RooFit.Label(model.GetTitle()), RooFit.Layout(0.5, 0.95, 0.94), RooFit.Format("NEAU")) #FIXME
                elif fitRes is not None: frame.addObject(fitRes, "E3")
            else:
                model.plotOn(frame, RooFit.Normalization(norm, RooAbsReal.NumEvent), RooFit.Range(normRange), RooFit.LineColor(getColor(name, channel)), RooFit.DrawOption("F"), RooFit.FillColor(getColor(name, channel)), RooFit.FillStyle(1001), RooFit.VLines(), RooFit.Name("Vjet"))
                res = frame.pullHist()
                model.plotOn(frame, RooFit.Normalization(norm, RooAbsReal.NumEvent), RooFit.Range(normRange), RooFit.Components("VV"+postfix+",Top"+postfix), RooFit.LineColor(798), RooFit.DrawOption("F"), RooFit.FillColor(798), RooFit.FillStyle(1001), RooFit.VLines(), RooFit.Name("Top"))
                model.plotOn(frame, RooFit.Normalization(norm, RooAbsReal.NumEvent), RooFit.Range(normRange), RooFit.Components("VV"+postfix), RooFit.LineColor(602), RooFit.DrawOption("F"), RooFit.FillColor(602), RooFit.FillStyle(1001), RooFit.VLines(), RooFit.Name("VV"))
                if alt is not None: alt.plotOn(frame, RooFit.Normalization(anorm if anorm>0 else norm, RooAbsReal.NumEvent), RooFit.Range(normRange), RooFit.LineStyle(7), RooFit.LineColor(921), RooFit.Name("Alternate"))
                if signal is not None: signal.plotOn(frame, RooFit.Normalization(snorm, RooAbsReal.NumEvent), RooFit.Range(normRange), RooFit.LineColor(629), RooFit.DrawOption("L"), RooFit.Name("Signal"))
                if type(fitRes) is list:
                    for f in fitRes:
                        if f is not None: model.plotOn(frame, RooFit.Normalization(norm, RooAbsReal.NumEvent), RooFit.Range(normRange), RooFit.VisualizeError(f, 1, False), RooFit.SumW2Error(True), RooFit.LineColor(0), RooFit.FillColor(1), RooFit.FillStyle(3002), RooFit.Name("Uncertainty"))
                        #model.paramOn(frame, RooFit.Label(model.GetTitle()), RooFit.Layout(0.5, 0.95, 0.94), RooFit.Format("NEAU")) #FIXME
                elif fitRes is not None: frame.addObject(fitRes, "E3")


    # Simple fit
    else:
        if isCategory:
            if type(fitRes) is list:
                for f in fitRes:
                    if f is not None:
                        model.plotOn(frame, RooFit.Slice(reg, cat), RooFit.ProjWData(RooArgSet(reg), dataset), RooFit.VisualizeError(f, 1, False), RooFit.SumW2Error(True), RooFit.FillColor(1), RooFit.FillStyle(3002))
                        if VERBOSE: model.plotOn(frame, RooFit.Slice(reg, cat), RooFit.ProjWData(RooArgSet(reg), dataset), RooFit.VisualizeError(f), RooFit.SumW2Error(True), RooFit.FillColor(2), RooFit.FillStyle(3004))
                    #model.paramOn(frame, RooFit.Label(model.GetTitle()), RooFit.Layout(0.5, 0.95, 0.94), RooFit.Format("NEAU")) #Parameters( RooArgSet(Mean,Sigma))
            elif fitRes is not None: frame.addObject(fitRes, "E3")
            model.plotOn(frame, RooFit.Slice(reg, cat), RooFit.ProjWData(RooArgSet(reg), dataset), RooFit.LineColor(getColor(name, channel)))
            res = frame.pullHist()
#            model.plotOn(frame, RooFit.Slice(reg, cat), RooFit.ProjWData(RooArgSet(reg), dataset), RooFit.LineColor(getColor(name, channel)), RooFit.LineStyle(2), RooFit.Components("baseTop"))
#            model.plotOn(frame, RooFit.Slice(reg, cat), RooFit.ProjWData(RooArgSet(reg), dataset), RooFit.LineColor(getColor(name, channel)), RooFit.LineStyle(2), RooFit.Components("baseVV"))
            if alt is not None: alt.plotOn(frame, RooFit.Normalization(anorm, RooAbsReal.NumEvent), RooFit.LineStyle(7), RooFit.LineColor(922), RooFit.Name("Alternate"))
        else:
            if type(fitRes) is list:
                for f in fitRes:
                    if f is not None:
                        model.plotOn(frame, RooFit.VisualizeError(f, 1, False), RooFit.Normalization(norm if norm>0 or dataset is None else dataset.sumEntries(), RooAbsReal.NumEvent), RooFit.SumW2Error(True), RooFit.Range(normRange), RooFit.FillColor(1), RooFit.FillStyle(3002), RooFit.DrawOption("F"))
                        if VERBOSE: model.plotOn(frame, RooFit.VisualizeError(f), RooFit.Normalization(norm if norm>0 or dataset is None else dataset.sumEntries(), RooAbsReal.NumEvent), RooFit.SumW2Error(True), RooFit.Range(normRange), RooFit.FillColor(2), RooFit.FillStyle(3004), RooFit.DrawOption("F"))
                    model.paramOn(frame, RooFit.Label(model.GetTitle()), RooFit.Layout(0.5, 0.95, 0.94), RooFit.Format("NEAU"))
            elif fitRes is not None: frame.addObject(fitRes, "E3")
            model.plotOn(frame, RooFit.LineColor(getColor(name, channel)), RooFit.Range(normRange), RooFit.Normalization(norm if norm>0 or dataset is None else dataset.sumEntries(), RooAbsReal.NumEvent)) #RooFit.Normalization(norm if norm>0 or dataset is None else dataset.sumEntries(), RooAbsReal.NumEvent)
            res = frame.pullHist() #if not isSignal else frame.residHist()
            # plot components
            for comp in ["baseTop", "gausW", "gausT", "baseVV", "gausVW", "gausVZ", "gausVH"]: model.plotOn(frame, RooFit.LineColor(getColor(name, channel)), RooFit.Range(normRange), RooFit.LineStyle(2), RooFit.Components(comp), RooFit.Normalization(norm if norm>0 or dataset is None else dataset.sumEntries(), RooAbsReal.NumEvent))
            if alt is not None: alt.plotOn(frame, RooFit.Range(normRange), RooFit.LineStyle(7), RooFit.LineColor(922), RooFit.Name("Alternate"))

    # Replot data
    if dataset is not None: data = dataset.plotOn(frame, RooFit.Cut(cut), RooFit.Binning(variable.getBinning("PLOT")), RooFit.DataError(RooAbsData.Poisson if isData else RooAbsData.SumW2), RooFit.Range(dataRange), RooFit.DrawOption("PE0"), RooFit.Name("data_obs"))
    if data is not None and isData: fixData(data.getHist(), True)

    if not isMass and not isSignal: # Log scale
        frame.SetMaximum(frame.GetMaximum()*10)
        frame.SetMinimum(max(frame.SetMinimum(), 8.e-2 if isData else 1.e-4))
        c.GetPad(1).SetLogy()
    else:
        frame.GetYaxis().SetRangeUser(0, frame.GetMaximum())
        frame.SetMaximum(frame.GetMaximum()*1.25)
        frame.SetMinimum(0)
    frame.GetYaxis().SetTitleOffset(frame.GetYaxis().GetTitleOffset()*1.15)
    frame.Draw()
    drawCMS(LUMI, cmsLabel)
    drawAnalysis(channel)
    drawRegion(channel + ("" if isData and not isCategory else ('SR' if 'SR' in name else ('SB' if 'SB' in name else ""))), True)
    if isSignal: drawMass(name)
    if isData and isMass:
        box = drawBox(LOWMAX, frame.GetMinimum(), SIGMIN, frame.GetMaximum()/1.30, "") #"(blind)"
        lineL = drawLine(LOWMAX, frame.GetMinimum(), LOWMAX, frame.GetMaximum()/1.30)
        lineM = drawLine(SIGMIN, frame.GetMinimum(), SIGMIN, frame.GetMaximum()/1.30)
        lineU = drawLine(SIGMAX, frame.GetMinimum(), SIGMAX, frame.GetMaximum()/1.30)
        textL = drawText((LOWMAX+LOWMIN)/2, frame.GetMaximum()/1.35, "LSB")
        textV = drawText((SIGMIN+LOWMAX)/2, frame.GetMaximum()/1.35, "VR")
        textH = drawText((SIGMAX+SIGMIN)/2, frame.GetMaximum()/1.35, "SR")
        textU = drawText(HIGMIN+10, frame.GetMaximum()/1.35, "HSB")

    if isData:
        leg = TLegend(0.6-0.005, 0.6, 0.9, 0.9)
        leg.SetBorderSize(0)
        leg.SetFillStyle(0) #1001
        leg.SetFillColor(0)
        leg.AddEntry("data_obs", "Data", "PE")
        if 'll' in channel or 'ee' in channel or 'mm' in channel: leg.AddEntry("Vjet", "Z(ll)+jets", "F")
        elif 'ln' in channel or 'en' in channel or 'mn' in channel: leg.AddEntry("Vjet", "W(l#nu)+jets", "F")
        else: leg.AddEntry("Vjet", "Z(#nu#nu),W(l#nu)+jets", "F")
        leg.AddEntry("Top", "t#bar{t}, t+X", "F")
        leg.AddEntry("VV", "VV, Vh", "F")
        if type(fitRes) is list: leg.AddEntry("Uncertainty", "Bkg. unc.", "F")
        elif fitRes is not None: leg.AddEntry(fitRes, "Fit unc.", "F")
        if alt is not None: leg.AddEntry("Alternate", "Alt. func.", "L")
        if signal is not None: leg.AddEntry("Signal", signal.GetTitle(), "L")
        leg.SetY1(0.9-leg.GetNRows()*0.06)
        leg.Draw()
        if signal is not None:
            latex = TLatex()
            latex.SetNDC()
            latex.SetTextSize(0.045)
            latex.SetTextFont(42)
            latex.DrawLatex(0.67, leg.GetY1()-0.045, "HVT model B g_{V}=3") #("Z'" if 'Z' in channel else "W'")+

    if isBottomPanel:
        c.cd(2)
        frame_res = variable.frame()
        setPadStyle(frame_res, 1.25)
        #res = frame.residHist()
        if res is not None and isData: fixData(res)
        if dataset is not None: frame_res.addPlotable(res, "P")
    #    if not type(fitRes) is list:
    #        fitPull = fitRes.Clone()
    #        for i in range(fitPull.GetN()):
    #            upnorm = fitPull.GetErrorYhigh(i)
    #            downnorm = fitPull.GetErrorYlow(i)
    #            uperr = ROOT.Math.gamma_quantile_c((1 - 0.6827)/2, upnorm+1, 1)
    #            downerr = (0 if upnorm==0 else ROOT.Math.gamma_quantile((1 - 0.6827)/2, downnorm, 1.))
    #            print i, fitPull.GetX()[i], uperr, fitPull.GetY()[i], downerr
    #            fitPull.SetPoint(i, fitPull.GetX()[i], 0.)
    #            fitPull.SetPointError(i, fitPull.GetErrorXlow(i), fitPull.GetErrorXhigh(i), (downerr)/downnorm, (upnorm)/upnorm)
    #        frame_res.addObject(fitPull, "E3")
        setBotStyle(frame_res, RATIO, False)
        #frame_res.GetXaxis().SetRangeUser(HBINMIN, HBINMAX)
        frame_res.GetYaxis().SetRangeUser(-pullRange, pullRange)
        frame_res.GetYaxis().SetTitleOffset(frame_res.GetYaxis().GetTitleOffset()*1.12)
        frame_res.GetYaxis().SetTitle("(N^{data}-N^{bkg})/#sigma")
        frame_res.Draw()
        # GOF
        #drawChi2(frame.chiSquare())
        chi2, nbins, npar = 0., 0, 0
    #    if isMass and not fitRes==None and len(fitRes)>0: fitRes[0].floatParsFinal().getSize()
        if not res==None:
            for i in range(0, res.GetN()):
                if data.getHist().GetY()[i] > 1.e-3:
                    nbins = nbins + 1
                    chi2 += res.GetY()[i]**2
        #if isData:
        #drawChi2(chi2, nbins - npar, True)

        #if isData and not isMass:
        frame.GetXaxis().SetRangeUser(variable.getMin(), lastBin)
        frame_res.GetXaxis().SetRangeUser(variable.getMin(), lastBin)
        line_res = drawLine(frame_res.GetXaxis().GetXmin(), 0, lastBin, 0)
        
        if isData and isMass:
            line_res = drawLine(frame_res.GetXaxis().GetXmin(), 0, lastBin, 0)
            box_res = drawBox(LOWMAX, -pullRange, SIGMIN, pullRange)
            lineL_res = drawLine(LOWMAX, -pullRange, LOWMAX, pullRange)
            lineM_res = drawLine(SIGMIN, -pullRange, SIGMIN, pullRange)
            lineU_res = drawLine(SIGMAX, -pullRange, SIGMAX, pullRange)

    if 'paper' in name:
        c.SaveAs(PLOTDIR+name+".pdf")
        c.SaveAs(PLOTDIR+name+".png")
        return
    if isSignal:
        c.SaveAs(PLOTDIR+channel+"/"+name+".pdf")
        c.SaveAs(PLOTDIR+channel+"/"+name+".png")
        return
#    if not os.path.exists(PLOTDIR+channel):
#        c.SaveAs(PLOTDIR+name+".pdf")
#        c.SaveAs(PLOTDIR+name+".png")
#        return
    c.SaveAs(PLOTDIR+channel+"/"+name+".pdf")
    c.SaveAs(PLOTDIR+channel+"/"+name+".png")
    #if VERBOSE: raw_input("Press Enter to continue...")
    # ======   END PLOT   ======



def drawAlphaPlot(name, channel, var, alpha, bkgSB, bkgSR, fitRes, alpha2=None, bkgSB2=None, bkgSR2=None, fitRes2=None, ratio=1.):
    #norm = 1.#ratio#*variable.getBinning().numBins()
    variable = RooRealVar( var )
    variable.setBins(100)
    norm = 1.#variable.getBins()

    # ====== CONTROL PLOT ======
    c = TCanvas("c_"+name, "Alpha function", 800, 800)
    c.cd()
    frame = variable.frame()
    setPadStyle(frame, 1.1)
    #bkgSB.plotOn(frame, RooFit.LineColor(602)) #FIXME
    #bkgSR.plotOn(frame, RooFit.LineColor(2)) #FIXME
    alpha.plotOn(frame, RooFit.VisualizeError(fitRes, 2, False), RooFit.Normalization(norm), RooFit.LineColor(400), RooFit.FillColor(400), RooFit.Name("2sigma"))
    alpha.plotOn(frame, RooFit.VisualizeError(fitRes, 1, False), RooFit.Normalization(norm), RooFit.LineColor(416), RooFit.FillColor(416), RooFit.Name("1sigma"))
    alpha.plotOn(frame, RooFit.Normalization(norm), RooFit.LineColor(1), RooFit.Name("alpha"))
    if ALTERNATIVE:
        #alpha2.plotOn(frame, RooFit.VisualizeError(fitRes2, 2, False), RooFit.DrawOption("L"), RooFit.LineColor(922), RooFit.LineStyle(8))
        #alpha2.plotOn(frame, RooFit.VisualizeError(fitRes2, 1, False), RooFit.DrawOption("L"), RooFit.LineColor(922), RooFit.LineStyle(7))
        alpha2.plotOn(frame, RooFit.Normalization(norm), RooFit.LineColor(922), RooFit.LineStyle(7), RooFit.Name("alpha2"))
    frame.GetXaxis().SetRangeUser(variable.getMin(), variable.getMax())
    #frame.GetYaxis().SetRangeUser(0., 0.15)
    frame.SetYTitle("")
    frame.Draw()
    #drawCMS(-1, "Simulation")
    drawAnalysis("VH")
    drawRegion(channel, True)
    drawCMS(LUMI, "Preliminary")

    leg = TLegend(0.5, 0.65, 0.95, 0.9)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0) #1001
    leg.SetFillColor(0)
    leg.AddEntry("alpha", alpha.GetTitle(), "L")
    leg.AddEntry("1sigma", "#alpha function #pm 1#sigma", "F")
    leg.AddEntry("2sigma", "#alpha function #pm 2#sigma", "F")
    if ALTERNATIVE: leg.AddEntry("alpha2", alpha2.GetTitle(), "L")
    leg.Draw()


    c.SaveAs(PLOTDIR+channel+"/AlphaRatio.pdf")
    c.SaveAs(PLOTDIR+channel+"/AlphaRatio.png")
    #c.SaveAs(PLOTDIR+channel+"/AlphaRatio.root")
#    frame.SetYTitle("")
#    #bkgSB.plotOn(frame, RooFit.LineColor(602))
#    #bkgSR.plotOn(frame, RooFit.LineColor(2))
#    c.SaveAs(PLOTDIR+channel+"/AlphaMethod.pdf")
#    c.SaveAs(PLOTDIR+channel+"/AlphaMethod.png")
#    #c.SaveAs(PLOTDIR+channel+"/AlphaMethod.root")
#    frame.SetMinimum(max(frame.SetMinimum(), 2.e-3))
#    c.GetPad(0).SetLogy()
#    c.SaveAs(PLOTDIR+channel+"/AlphaMethod_log.pdf")
#    c.SaveAs(PLOTDIR+channel+"/AlphaMethod_log.png")
#    #c.SaveAs(PLOTDIR+channel+"/AlphaMethod_log.root")
    # ======   END PLOT   ======


    # ====== CONTROL PLOT ======
    c_alpha2 = TCanvas("c_alpha2", "Alpha method", 800, 800)
    c_alpha2.cd()
    frame_alpha2 = variable.frame()
    setPadStyle(frame, 1.1)
    alpha.plotOn(frame_alpha2, RooFit.Normalization(norm), RooFit.LineColor(1), RooFit.Name("alpha"))
    alpha.plotOn(frame_alpha2, RooFit.Normalization(norm), RooFit.VisualizeError(fitRes, 2, False), RooFit.LineColor(400), RooFit.FillColor(400), RooFit.Name("2sigma"))
    alpha.plotOn(frame_alpha2, RooFit.Normalization(norm), RooFit.VisualizeError(fitRes, 1, False), RooFit.LineColor(416), RooFit.FillColor(416), RooFit.Name("1sigma"))
    alpha.plotOn(frame_alpha2, RooFit.Normalization(norm), RooFit.LineColor(1), RooFit.Name("alpha"))
    bkgSB.plotOn(frame_alpha2, RooFit.VisualizeError(fitRes, 1, False), RooFit.FillColor(602), RooFit.FillStyle(3002))
    bkgSB.plotOn(frame_alpha2, RooFit.LineColor(602), RooFit.Name("bkgSB"))
    bkgSR.plotOn(frame_alpha2, RooFit.VisualizeError(fitRes, 1, False), RooFit.FillColor(2), RooFit.FillStyle(3002))
    bkgSR.plotOn(frame_alpha2, RooFit.LineColor(2), RooFit.Name("bkgSR"))
    if ALTERNATIVE:
        alpha2.plotOn(frame_alpha2, RooFit.Normalization(norm), RooFit.LineColor(922), RooFit.LineStyle(7), RooFit.Name("alpha2"))
        bkgSB2.plotOn(frame_alpha2, RooFit.LineColor(602), RooFit.LineStyle(7), RooFit.Name("bkgSB2"))
        bkgSR2.plotOn(frame_alpha2, RooFit.LineColor(2), RooFit.LineStyle(7), RooFit.Name("bkgSR2"))
    frame_alpha2.GetXaxis().SetRangeUser(variable.getMin(), variable.getMax())
    #   frame_alpha2.GetYaxis().SetRangeUser(0, frame_alpha2.GetMaximum())
    frame_alpha2.Draw()
    frame_alpha2.SetYTitle("")
    drawAnalysis("VH")
    drawRegion(channel, True)
    drawCMS(LUMI, "Preliminary")

    leg2 = TLegend(0.5, 0.55, 0.95, 0.9)
    leg2.SetBorderSize(0)
    leg2.SetFillStyle(0) #1001
    leg2.SetFillColor(0)
    leg2.AddEntry("alpha", alpha.GetTitle(), "L")
    leg2.AddEntry("bkgSB", "bkg. fit in SB", "L")
    leg2.AddEntry("bkgSR", "bkg. pred. in SR", "L")
    if ALTERNATIVE:
        leg2.AddEntry("alpha2", alpha2.GetTitle(), "L")
        leg2.AddEntry("bkgSB2", "alternative bkg. fit in SB", "L")
        leg2.AddEntry("bkgSR2", "alternative bkg. pred. in SR", "L")
    leg2.Draw()

    c_alpha2.SaveAs(PLOTDIR+channel+"/AlphaMethod.pdf")
    c_alpha2.SaveAs(PLOTDIR+channel+"/AlphaMethod.png")
    #c_alpha2.SaveAs(PLOTDIR+channel+"/AlphaMethod.root")
    frame_alpha2.SetMaximum(1.e+1)
    frame_alpha2.SetMinimum(1.e-6)
    c_alpha2.GetPad(0).SetLogy()
    c_alpha2.SaveAs(PLOTDIR+channel+"/AlphaMethod_log.pdf")
    c_alpha2.SaveAs(PLOTDIR+channel+"/AlphaMethod_log.png")
    #c_alpha2.SaveAs(PLOTDIR+channel+"/AlphaMethod_log.root")

    #if VERBOSE: raw_input("Press Enter to continue...")
    # ======   END PLOT   ======



def drawMultiPlot(name, channel, variable, models, fitRes=[], norm=[]):

    # ====== CONTROL PLOT ======
    c = TCanvas("c_"+name, "Signal", 800, 600)
    c.cd()
    frame = variable.frame()
    setPadStyle(frame, 1.1)
    for m, model in models.iteritems(): model.plotOn(frame, RooFit.Normalization(1 if not m in norm else norm[m].getVal(), RooAbsReal.NumEvent), RooFit.LineColor(getColor("XVH_M%d" % m, channel)), RooFit.LineStyle(1 if not getColor("XVH_M%d" % m, channel)==1 else 3), RooFit.LineWidth(2), RooFit.DrawOption("L"), RooFit.Name(model.GetName()))
    frame.GetXaxis().SetRangeUser(variable.getMin(), variable.getMax())
    frame.SetYTitle("")
    frame.Draw()
    drawAnalysis("VH")
    drawRegion(channel, True)
    drawCMS(-1, "Preliminary Simulation")

    leg = TLegend(0.65, 0.5, 0.99, 0.925)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0) #1001
    leg.SetFillColor(0)
    #leg.SetNColumns(len(models) / 15)
    for m, model in sorted(models.iteritems()):
        if not getColor("XVH_M%d" % m, channel)==getColor("", channel): leg.AddEntry(model.GetName(), model.GetTitle(), "L")
    leg.Draw()
    c.SaveAs("plotsAlpha/"+channel+"/"+name+".pdf")
    c.SaveAs("plotsAlpha/"+channel+"/"+name+".png")

    #if VERBOSE: raw_input("Press Enter to continue...")
    # ======   END PLOT   ======



def plotSys(name, channel, variable, model, sys):
    c_sys = TCanvas("c_sys_"+name, name, 800, 600)
    c_sys.cd()
    frame_sys = variable.frame()
    model.plotOn(frame_sys, RooFit.LineColor(1), RooFit.Name("Central"))
    sys.setVal(1)
    model.plotOn(frame_sys, RooFit.LineColor(634), RooFit.Name("Up"))
    sys.setVal(-1)
    model.plotOn(frame_sys, RooFit.LineColor(598), RooFit.Name("Down"))
    sys.setVal(0)
    frame_sys.GetXaxis().SetRangeUser(variable.getMin(), variable.getMax())
    frame_sys.Draw()
    drawCMS(-1, "Simulation")
    drawAnalysis("VH")
    drawRegion(channel)
    frame_sys.SetMaximum(frame_sys.GetMaximum()*5)
    frame_sys.SetMinimum(1.e-4)
    c_sys.GetPad(0).SetLogy()
    leg = TLegend(0.65, 0.65, 0.95, 0.9)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0) #1001
    leg.SetFillColor(0)
    leg.AddEntry("Up", "+1 #sigma", "L")
    leg.AddEntry("Central", "central", "L")
    leg.AddEntry("Down", "-1 #sigma", "L")
    leg.Draw()

    c_sys.SaveAs(PLOTDIR+channel+"/"+name+".pdf")
    c_sys.SaveAs(PLOTDIR+channel+"/"+name+".png")






#jobs = []
#
#
#if __name__ == "__main__":
#    if options.all:
#        for c in channelList:
#            p = multiprocessing.Process(target=alpha, args=(c,))
#            jobs.append(p)
#            p.start()
#    else:
#        if options.channel in channelList: alpha(options.channel)
#        else:
#            print "Channel not set or not recognized. Quitting..."
#            exit()
