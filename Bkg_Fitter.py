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
from samples import sample
from aliases import alias, aliasSM, deepFlavour, working_points
from aliases import additional_selections as SELECTIONS
#from selections import selection
#from utils import *

import optparse

print "packages imported"

usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage)
parser.add_option("-d", "--test", action="store_true", default=False, dest="bias")
parser.add_option("-v", "--verbose", action="store_true", default=False, dest="verbose")
parser.add_option("-t", "--test_run", action="store_true", default=False, dest="test")
parser.add_option("-M", "--isMC", action="store_true", default=False, dest="isMC")
parser.add_option('-y', '--year', action='store', type='string', dest='year',default='2016')
parser.add_option("-c", "--category", action="store", type="string", dest="category", default="")
parser.add_option("-b", "--btagging", action="store", type="string", dest="btagging", default="tight")
parser.add_option("-u", "--unskimmed", action="store_true", default=False, dest="unskimmed")
parser.add_option("-s", "--selection", action="store", type="string", dest="selection", default="")
#parser.add_option("-S", "--submitted", action="store_true", default=False, dest="submitted")
(options, args) = parser.parse_args()
gROOT.SetBatch(True) #suppress immediate graphic output
if options.test: print "performing test run on small QCD MC sample"

if options.test and not options.isMC:
    print "There is no test sample on data. Select -M if you want to test on MC QCD 2016."
    sys.exit()
if options.test and not options.unskimmed:
    print "There is no skimmed test sample on data. Select -u if you want to test on the unskimmed MC QCD 2016."
    sys.exit()

########## SETTINGS ##########

# Silent RooFit
RooMsgService.instance().setGlobalKillBelow(RooFit.FATAL)

#gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)
gStyle.SetPadTopMargin(0.06)
gStyle.SetPadRightMargin(0.05)
gStyle.SetErrorX(0.)

BTAGGING    = options.btagging
NTUPLEDIR   = "/afs/cern.ch/work/m/msommerh/public/Zprime_to_bb_Analysis/Skim/"
#CARDDIR     = "datacards/"+BTAGGING+"/"
WORKDIR     = "workspace/"+BTAGGING+"/"
RATIO       = 4
SHOWERR     = True
BLIND       = False
VERBOSE     = options.verbose
CUTCOUNT    = False
VARBINS     = False
BIAS        = options.bias
YEAR        = options.year
ISMC        = options.isMC
ADDSELECTION= options.selection!=""

if YEAR=='2016':
    LUMI=35920.
elif YEAR=='2017':
    LUMI=41530.
elif YEAR=='2018':
    LUMI=59740.
elif YEAR=='run2':
    LUMI=137190.
else:
    print "unknown year:",YEAR
    sys.exit()

if BTAGGING not in ['tight', 'medium', 'loose', 'semimedium']:
    print "unknown btagging requirement:", BTAGGING
    sys.exit()

if ISMC:
    #DATA_TYPE = "MC_QCD"
    DATA_TYPE = "MC_QCD_TTbar"
else:
    DATA_TYPE = "data"
PLOTDIR     = "plots/"+BTAGGING+"/{}_{}".format(DATA_TYPE, YEAR)
if options.test: PLOTDIR += "_test"

if options.unskimmed or options.test:
    NTUPLEDIR="/eos/user/m/msommerh/Zprime_to_bb_analysis/weighted/" 

if options.selection not in SELECTIONS.keys():
    print "invalid selection!"
    sys.exit()

#if options.submitted:
#    CARDDIR +="submitted/"
#    WORKDIR +="submitted/"
#    PLOTDIR +="submitted/"

signalList = ['Zprime_to_bb']
categories = ['bb', 'bq', 'qq']

dijet_bins = [955, 1000, 1058, 1118, 1181, 1246, 1313, 1383, 1455, 1530, 1607, 1687, 1770, 1856, 1945, 2037, 2132, 2231, 2332, 2438, 2546, 2659, 2775, 2895, 3019, 3147, 3279, 3416, 3558, 3704, 3854, 4010, 4171, 4337, 4509, 4686, 4869, 5058, 5253, 5455, 5663, 5877, 6099, 6328, 6564, 6808]
bins = [x+30 for x in dijet_bins]
abins = array( 'd', bins )

data = ["data_obs"]
back = ["QCD", "TTbar"]

########## ######## ##########

def dijet(category):

    channel = 'bb'
    stype = channel
    isSB = True  # apparently stands for side bands
    isData = not ISMC 
    nTupleDir = NTUPLEDIR
 
    samples = data if isData else back
    pd = []
    if options.test:
        if ISMC and YEAR == '2016':
            pd.append("MC_QCD_"+YEAR)
            nTupleDir = NTUPLEDIR.replace("weighted/","test_for_fit/")
        else:
            print "No test sample for real data was implemented. Select '-M' if you want to test on a small MC QCD sample."
            sys.exit()
    else:
        for sample_name in samples:
            if YEAR=='run2':
                pd += sample[sample_name]['files']
            else:
                pd += [x for x in sample[sample_name]['files'] if YEAR in x]
    print "datasets:", pd
    if not os.path.exists(PLOTDIR): os.makedirs(PLOTDIR)
    if BIAS: print "Running in BIAS mode"
    
    order = 0
    RSS = {}
    
    X_mass = RooRealVar(        "jj_mass_widejet",              "m_{jj}",       1800.,  9000.,  "GeV") #set from 1400 to 1800 for a test FIXME
    #j1_mass = RooRealVar(       "jmass_1",              "jet1 mass",    0.,     700.,   "GeV")
    #j2_mass = RooRealVar(       "jmass_2",              "jet2 mass",    0.,     700.,   "GeV")
    j1_pt = RooRealVar(         "jpt_1",                "jet1 pt",      0.,     4500.,  "GeV")
    #j2_pt = RooRealVar(         "jpt_2",                "jet2 pt",      0.,     4500.,  "GeV")
    #jdeepCSV_1 = RooRealVar(    "jdeepCSV_1",           "",             -2.,   1.       )
    #jdeepCSV_2 = RooRealVar(    "jdeepCSV_2",           "",             -2.,   1.       )
    #jdeepFlavour_1 = RooRealVar("jdeepFlavour_1",       "",             0.,   1.        )
    #jdeepFlavour_2 = RooRealVar("jdeepFlavour_2",       "",             0.,   1.        )
    jbtag_WP_1 = RooRealVar("jbtag_WP_1",       "",             -1.,   4.        )
    jbtag_WP_2 = RooRealVar("jbtag_WP_2",       "",             -1.,   4.        )
    fatjetmass_1 = RooRealVar("fatjetmass_1",   "",             -1.,   2500.     )
    #MET_over_sumEt = RooRealVar("MET_over_SumEt",       "",             0.,     1.      )
    jj_deltaEta = RooRealVar(    "jj_deltaEta",                "",      0.,     5.)
    HLT_AK8PFJet500         = RooRealVar("HLT_AK8PFJet500"         , "",  -1., 1.    )
    HLT_PFJet500            = RooRealVar("HLT_PFJet500"            , "" , -1., 1.    )
    HLT_CaloJet500_NoJetID  = RooRealVar("HLT_CaloJet500_NoJetID"  , "" , -1., 1.    )
    HLT_PFHT900             = RooRealVar("HLT_PFHT900"            , "" , -1., 1.    )
    HLT_AK8PFJet550         = RooRealVar("HLT_AK8PFJet550"         , "",  -1., 1.    )
    HLT_PFJet550            = RooRealVar("HLT_PFJet550"            , "" , -1., 1.    )
    HLT_CaloJet550_NoJetID  = RooRealVar("HLT_CaloJet550_NoJetID"  , "" , -1., 1.    )
    HLT_PFHT1050            = RooRealVar("HLT_PFHT1050"            , "" , -1., 1.    )
    weight = RooRealVar(        "eventWeightLumi",      "",             -1.e9,  1.e9    )

    variables = RooArgSet(X_mass)
    #variables.add(RooArgSet(jdeepFlavour_1, jdeepFlavour_2, weight))
    variables.add(RooArgSet(jbtag_WP_1, jbtag_WP_2, fatjetmass_1, weight))
    variables.add(RooArgSet(j1_pt, jj_deltaEta))
    variables.add(RooArgSet(HLT_AK8PFJet500, HLT_PFJet500, HLT_CaloJet500_NoJetID, HLT_PFHT900, HLT_AK8PFJet550, HLT_PFJet550, HLT_CaloJet550_NoJetID, HLT_PFHT1050))
    X_mass.setBins(int((X_mass.getMax()-X_mass.getMin())/10))

    if VARBINS: binsXmass = RooBinning(len(abins)-1, abins)
    else: binsXmass = RooBinning(int((X_mass.getMax()-X_mass.getMin())/100), X_mass.getMin(), X_mass.getMax())
   
    if BTAGGING=='semimedium': 
        #baseCut = aliasSM[category].format(b_threshold_medium=deepFlavour['medium'][YEAR], b_threshold_loose=deepFlavour['loose'][YEAR])
        baseCut = aliasSM[category]
        #baseCut = aliasSM[category+"_vetoAK8"]
    else:
        #baseCut = alias[category].format(b_threshold=deepFlavour[BTAGGING][YEAR])
        baseCut = alias[category].format(WP=working_points[BTAGGING])
        #baseCut = alias[category+"_vetoAK8"].format(WP=working_points[BTAGGING])

    if ADDSELECTION: baseCut += SELECTIONS[options.selection]

    print stype, "|", baseCut
 
    print " - Reading from Tree"
    treeBkg = TChain("tree")
    if options.unskimmed or options.test:
        for i, ss in enumerate(pd):
            j = 0
            while True:
                if os.path.exists(nTupleDir + ss + "/" + ss + "_flatTuple_{}.root".format(j)):
                    treeBkg.Add(nTupleDir + ss + "/" + ss + "_flatTuple_{}.root".format(j))
                    j += 1
                else:
                    print "found {} files for sample:".format(j), ss
                    break
    else:
        for ss in pd:
            if os.path.exists(nTupleDir + ss + ".root"):
                treeBkg.Add(nTupleDir + ss + ".root")
            else:
                print "found no file for sample:", ss
    #setData = RooDataSet("setData", "Data" if isData else "Data (QCD MC)", variables, RooFit.Cut(baseCut), RooFit.WeightVar(weight), RooFit.Import(treeBkg))
    if isData or options.test:
        setData = RooDataSet("setData", "Data", variables, RooFit.Cut(baseCut), RooFit.Import(treeBkg))
    else:   
        setData = RooDataSet("setData", "Data (QCD MC)", variables, RooFit.Cut(baseCut), RooFit.WeightVar(weight), RooFit.Import(treeBkg))
 
    nevents = setData.sumEntries()
    dataMin, dataMax = array('d', [0.]), array('d', [0.])   # not sure what is happening here...
    setData.getRange(X_mass, dataMin, dataMax)
    xmin, xmax = dataMin[0], dataMax[0]
    
    lastBin = X_mass.getMax()
    if VARBINS: 
        for b in bins:
            if b > xmax:
                lastBin = b
                break
    
    print "Imported", ("data" if isData else "MC"), "RooDataSet with", nevents, "events between [%.1f, %.1f]" % (xmin, xmax)
    xmax = xmax+binsXmass.averageBinWidth() # start form next bin
    
    # 1 parameter
    print "fitting 1 parameter model"
    p1_1 = RooRealVar("CMS"+YEAR+"_"+category+"_p1_1", "p1", 7.0, 0., 2000.)
    modelBkg1 = RooGenericPdf("Bkg1", "Bkg. fit (2 par.)", "1./pow(@0/13000, @1)", RooArgList(X_mass, p1_1))
    normzBkg1 = RooRealVar(modelBkg1.GetName()+"_norm", "Number of background events", nevents, 0., 5.*nevents) #range dependent of actual number of events!
    modelExt1 = RooExtendPdf(modelBkg1.GetName()+"_ext", modelBkg1.GetTitle(), modelBkg1, normzBkg1)
    print "starting actual fit"
    fitRes1 = modelExt1.fitTo(setData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(not isData), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(1 if VERBOSE else -1))
    fitRes1.Print()
    print "drawFit function"
    RSS[1] = drawFit("Bkg1", category, X_mass, modelBkg1, setData, binsXmass, [fitRes1], normzBkg1.getVal())
    
    
    # 2 parameters
    print "fitting 2 parameter model"
    p2_1 = RooRealVar("CMS"+YEAR+"_"+category+"_p2_1", "p1", 0., -100., 1000.)
    p2_2 = RooRealVar("CMS"+YEAR+"_"+category+"_p2_2", "p2", p1_1.getVal(), -100., 600.)
    modelBkg2 = RooGenericPdf("Bkg2", "Bkg. fit (3 par.)", "pow(1-@0/13000, @1) / pow(@0/13000, @2)", RooArgList(X_mass, p2_1, p2_2))
    normzBkg2 = RooRealVar(modelBkg2.GetName()+"_norm", "Number of background events", nevents, 0., 5.*nevents)
    modelExt2 = RooExtendPdf(modelBkg2.GetName()+"_ext", modelBkg2.GetTitle(), modelBkg2, normzBkg2)
    print "starting actual fit"
    fitRes2 = modelExt2.fitTo(setData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(not isData), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(1 if VERBOSE else -1))
    fitRes2.Print()
    print "drawFit function"
    RSS[2] = drawFit("Bkg2", category, X_mass, modelBkg2, setData, binsXmass, [fitRes2], normzBkg2.getVal())
    
    # 3 parameters
    print "fitting 3 parameter model"
    p3_1 = RooRealVar("CMS"+YEAR+"_"+category+"_p3_1", "p1", p2_1.getVal(), -2000., 2000.)
    p3_2 = RooRealVar("CMS"+YEAR+"_"+category+"_p3_2", "p2", p2_2.getVal(), -400., 2000.)
    p3_3 = RooRealVar("CMS"+YEAR+"_"+category+"_p3_3", "p3", -2.5, -500., 500.)
    modelBkg3 = RooGenericPdf("Bkg3", "Bkg. fit (4 par.)", "pow(1-@0/13000, @1) / pow(@0/13000, @2+@3*log(@0/13000))", RooArgList(X_mass, p3_1, p3_2, p3_3))
    normzBkg3 = RooRealVar(modelBkg3.GetName()+"_norm", "Number of background events", nevents, 0., 5.*nevents)
    modelExt3 = RooExtendPdf(modelBkg3.GetName()+"_ext", modelBkg3.GetTitle(), modelBkg3, normzBkg3)
    print "starting actual fit"
    fitRes3 = modelExt3.fitTo(setData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(not isData), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(1 if VERBOSE else -1))
    fitRes3.Print()
    print "drawFit function"
    RSS[3] = drawFit("Bkg3", category, X_mass, modelBkg3, setData, binsXmass, [fitRes3], normzBkg3.getVal())
    
    # 4 parameters
    print "fitting 4 parameter model"
    p4_1 = RooRealVar("CMS"+YEAR+"_"+category+"_p4_1", "p1", p3_1.getVal(), -2000., 2000.)
    p4_2 = RooRealVar("CMS"+YEAR+"_"+category+"_p4_2", "p2", p3_2.getVal(), -2000., 2000.)
    p4_3 = RooRealVar("CMS"+YEAR+"_"+category+"_p4_3", "p3", p3_3.getVal(), -50., 50.)
    p4_4 = RooRealVar("CMS"+YEAR+"_"+category+"_p4_4", "p4", 0.1, -50., 50.)
    modelBkg4 = RooGenericPdf("Bkg4", "Bkg. fit (5 par.)", "pow(1 - @0/13000, @1) / pow(@0/13000, @2+@3*log(@0/13000)+@4*pow(log(@0/13000), 2))", RooArgList(X_mass, p4_1, p4_2, p4_3, p4_4))
    normzBkg4 = RooRealVar(modelBkg4.GetName()+"_norm", "Number of background events", nevents, 0., 5.*nevents)
    modelExt4 = RooExtendPdf(modelBkg4.GetName()+"_ext", modelBkg4.GetTitle(), modelBkg4, normzBkg4)
    print "starting actual fit"
    fitRes4 = modelExt4.fitTo(setData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(not isData), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(1 if VERBOSE else -1))
    fitRes4.Print()
    print "drawFit function"
    RSS[4] = drawFit("Bkg4", category, X_mass, modelBkg4, setData, binsXmass, [fitRes4], normzBkg4.getVal())
    
    # Normalization parameters are should be set constant, but shape ones should not
#    if BIAS:
#        p1_1.setConstant(True)
#        p2_1.setConstant(True)
#        p2_2.setConstant(True)
#        p3_1.setConstant(True)
#        p3_2.setConstant(True)
#        p3_3.setConstant(True)
#        p4_1.setConstant(True)
#        p4_2.setConstant(True)
#        p4_3.setConstant(True)
#        p4_4.setConstant(True)
    normzBkg1.setConstant(True)
    normzBkg2.setConstant(True)
    normzBkg3.setConstant(True)
    normzBkg4.setConstant(True)
    
    #*******************************************************#
    #                                                       #
    #                         Fisher                        #
    #                                                       #
    #*******************************************************#
    
    # Fisher test
    print "-"*25
    print "function & $\\chi^2$ & RSS & ndof & F-test & result \\\\"
    print "\\multicolumn{6}{c}{", "Zprime_to_bb", "} \\\\"
    print "\\hline"
    CL_high = False
    for o1 in range(1, 5):
        o2 = min(o1 + 1, 5)
        print "%d par & %.2f & %.2f & %d & " % (o1+1, RSS[o1]["chi2"], RSS[o1]["rss"], RSS[o1]["nbins"]-RSS[o1]["npar"]),
        if o2 > len(RSS):
            print "\\\\"
            continue #order==0 and 
        CL = fisherTest(RSS[o1]['rss'], RSS[o2]['rss'], o1+1., o2+1., RSS[o1]["nbins"])
        print "%d par vs %d par CL=%f & " % (o1+1, o2+1, CL),
        if CL > 0.10: # The function with less parameters is enough
            if not CL_high:
                order = o1
                print "%d par are sufficient" % (o1+1),
                CL_high=True
        else:
            print "%d par are needed" % (o2+1),
            if not CL_high:
                order = o2
        print "\\\\"
    print "\\hline"
    print "-"*25   
    print "@ Order is", order, "("+category+")"
    
    #order = min(3, order)
    #order = 2
    if order==1:
        modelBkg = modelBkg1#.Clone("Bkg")
        modelAlt = modelBkg2#.Clone("BkgAlt")
        normzBkg = normzBkg1#.Clone("Bkg_norm")
        fitRes = fitRes1
    elif order==2:
        modelBkg = modelBkg2#.Clone("Bkg")
        modelAlt = modelBkg3#.Clone("BkgAlt")
        normzBkg = normzBkg2#.Clone("Bkg_norm")
        fitRes = fitRes2
    elif order==3:
        modelBkg = modelBkg3#.Clone("Bkg")
        modelAlt = modelBkg4#.Clone("BkgAlt")
        normzBkg = normzBkg3#.Clone("Bkg_norm")
        fitRes = fitRes3
    elif order==4:
        modelBkg = modelBkg4#.Clone("Bkg")
        modelAlt = modelBkg3#.Clone("BkgAlt")
        normzBkg = normzBkg4#.Clone("Bkg_norm")
        fitRes = fitRes4
    else:
        print "Functions with", order+1, "or more parameters are needed to fit the background"
        exit()
    
    modelBkg.SetName("Bkg_"+YEAR+"_"+category)
    modelAlt.SetName("Alt_"+YEAR+"_"+category)
    normzBkg.SetName("Bkg_"+YEAR+"_"+category+"_norm")
    
    print "-"*25
    
    # Generate pseudo data
    setToys = RooDataSet()
    setToys.SetName("data_toys")
    setToys.SetTitle("Data (toys)")
    if not isData:
        print " - Generating", nevents, "events for toy data"
        setToys = modelAlt.generate(RooArgSet(X_mass), nevents) #why is it modelAlt and not modelBkg?? FIXME
        print "toy data generated"

    if VERBOSE: raw_input("Press Enter to continue...")
    
    
    #*******************************************************#
    #                                                       #
    #                         Plot                          #
    #                                                       #
    #*******************************************************#
  
    print "starting to plot" 
    c = TCanvas("c_"+category, category, 800, 800)
    c.Divide(1, 2)
    setTopPad(c.GetPad(1), RATIO)
    setBotPad(c.GetPad(2), RATIO)
    c.cd(1)
    frame = X_mass.frame()
    setPadStyle(frame, 1.25, True)
    if VARBINS: frame.GetXaxis().SetRangeUser(X_mass.getMin(), lastBin)
    signal = getSignal(category, stype, 2000)  #replacing Alberto's getSignal by own function FIXME

    graphData = setData.plotOn(frame, RooFit.Binning(binsXmass), RooFit.Scaling(False), RooFit.Invisible())
    modelBkg.plotOn(frame, RooFit.VisualizeError(fitRes, 1, False), RooFit.LineColor(602), RooFit.FillColor(590), RooFit.FillStyle(1001), RooFit.DrawOption("FL"), RooFit.Name("1sigma"))
    modelBkg.plotOn(frame, RooFit.LineColor(602), RooFit.FillColor(590), RooFit.FillStyle(1001), RooFit.DrawOption("L"), RooFit.Name(modelBkg.GetName()))
    modelAlt.plotOn(frame, RooFit.LineStyle(7), RooFit.LineColor(613), RooFit.FillColor(609), RooFit.FillStyle(1001), RooFit.DrawOption("L"), RooFit.Name(modelAlt.GetName()))
    if not isSB and signal[0] is not None: # FIXME remove /(2./3.)
        signal[0].plotOn(frame, RooFit.Normalization(signal[1]*signal[2], RooAbsReal.NumEvent), RooFit.LineStyle(3), RooFit.LineWidth(6), RooFit.LineColor(629), RooFit.DrawOption("L"), RooFit.Name("Signal"))
    graphData = setData.plotOn(frame, RooFit.Binning(binsXmass), RooFit.Scaling(False), RooFit.XErrorSize(0 if not VARBINS else 1), RooFit.DataError(RooAbsData.Poisson if isData else RooAbsData.SumW2), RooFit.DrawOption("PE0"), RooFit.Name(setData.GetName()))
    fixData(graphData.getHist(), True, True, not isData)
    pulls = frame.pullHist(setData.GetName(), modelBkg.GetName(), True)  
    chi = frame.chiSquare(setData.GetName(), modelBkg.GetName(), True)
    #setToys.plotOn(frame, RooFit.DataError(RooAbsData.Poisson), RooFit.DrawOption("PE0"), RooFit.MarkerColor(2))
    if VARBINS: frame.GetYaxis().SetTitle("Events / ( 100 GeV )")
    frame.Draw()
    #print "frame drawn"
    # Get Chi2
#    chi2[1] = frame.chiSquare(modelBkg1.GetName(), setData.GetName())
#    chi2[2] = frame.chiSquare(modelBkg2.GetName(), setData.GetName())
#    chi2[3] = frame.chiSquare(modelBkg3.GetName(), setData.GetName())
#    chi2[4] = frame.chiSquare(modelBkg4.GetName(), setData.GetName())
    
    frame.SetMaximum(frame.GetMaximum()*10)
    frame.SetMinimum(max(frame.GetMinimum(), 1.e-1))
    c.GetPad(1).SetLogy()

    drawAnalysis(category)
    drawRegion(category, True)
    drawCMS(LUMI, "Simulation Preliminary")

    leg = TLegend(0.575, 0.6, 0.95, 0.9)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0) #1001
    leg.SetFillColor(0)
    leg.AddEntry(setData.GetName(), setData.GetTitle()+" (%d events)" % nevents, "PEL")
    leg.AddEntry(modelBkg.GetName(), modelBkg.GetTitle(), "FL")#.SetTextColor(629)
    leg.AddEntry(modelAlt.GetName(), modelAlt.GetTitle(), "L")
    if not isSB and signal[0] is not None: leg.AddEntry("Signal", signal[0].GetTitle(), "L")
    leg.SetY1(0.9-leg.GetNRows()*0.05)
    leg.Draw()

    latex = TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.04)
    latex.SetTextFont(42)
    if not isSB: latex.DrawLatex(leg.GetX1()*1.16, leg.GetY1()-0.04, "HVT model B (g_{V}=3)")
#    latex.DrawLatex(0.67, leg.GetY1()-0.045, "#sigma_{X} = 1.0 pb")

    c.cd(2)
    frame_res = X_mass.frame()
    setPadStyle(frame_res, 1.25)
    frame_res.addPlotable(pulls, "P")
    setBotStyle(frame_res, RATIO, False)
    if VARBINS: frame_res.GetXaxis().SetRangeUser(X_mass.getMin(), lastBin)
    frame_res.GetYaxis().SetRangeUser(-5, 5)
    frame_res.GetYaxis().SetTitle("(N^{data}-N^{bkg})/#sigma")
    frame_res.Draw()
    fixData(pulls, False, True, False)

    drawChi2(RSS[order]["chi2"], RSS[order]["nbins"]-(order+1), True)
    line = drawLine(X_mass.getMin(), 0, lastBin, 0)

    if VARBINS:
        c.SaveAs(PLOTDIR+"/BkgSR_"+category+".pdf")
        c.SaveAs(PLOTDIR+"/BkgSR_"+category+".png")
    else:
        c.SaveAs(PLOTDIR+"/BkgSR_"+category+".pdf")
        c.SaveAs(PLOTDIR+"/BkgSR_"+category+".png")
 
     
    ##*******************************************************#
    ##                                                       #
    ##                    Signal shape                       #
    ##                                                       #
    ##*******************************************************#
    #
    ##if not isSB:
    #
    ## nbkg fro cut&count
    #X_mass.setRange("X_data_range", xmax, X_mass.getMax())   ## I don't get it. Why is there a xmax in the spot for the minimum??
    #massArg = RooArgSet(X_mass)
    #integral = modelBkg.createIntegral(massArg, RooFit.NormSet(massArg), RooFit.Range("X_data_range"))
    #integralError = integral.getPropagatedError(fitRes)
    #nbkg = integral.getVal() * nevents
    #nbkgErr = integralError * nevents
    #
    #syst, syst_sig = {}, {}
    #
    #if 'H_dbt' in baseCut:
    #    syst["CMS2016_eff_b"] = { 1000 : [1.033, 0.956],  1100 : [1.033, 0.956],  1200 : [1.033, 0.956],  1300 : [1.033, 0.956],  1400 : [1.033, 0.956],  1500 : [1.034, 0.955],  1600 : [1.035, 0.954],  1700 : [1.041, 0.946],  1800 : [1.047, 0.938],  2000 : [1.058, 0.922],  2500 : [1.066, 0.912],  3000 : [1.066, 0.912],  3500 : [1.066, 0.912],  4000 : [1.066, 0.912],  4500 : [1.066, 0.912],  } if 'bb' in category else { 1000 : [0.968, 1.023],  1100 : [0.965, 1.019],  1200 : [0.963, 1.015],  1300 : [0.963, 1.015],  1400 : [0.962, 1.014],  1500 : [0.961, 1.015],  1600 : [0.960, 1.015],  1700 : [0.953, 1.018],  1800 : [0.946, 1.021],  2000 : [0.933, 1.026],  2500 : [0.924, 1.030],  3000 : [0.924, 1.031],  3500 : [0.923, 1.032],  4000 : [0.923, 1.032],  4500 : [0.923, 1.032],  }
    #elif 'H_csv' in baseCut:
    #    syst["CMS2016_eff_b"] = { 1000 : [1.030, 0.970],  1100 : [1.033, 0.967],  1200 : [1.036, 0.965],  1300 : [1.039, 0.962],  1400 : [1.042, 0.959],  1500 : [1.044, 0.957],  1600 : [1.047, 0.954],  1700 : [1.049, 0.952],  1800 : [1.050, 0.951],  2000 : [1.054, 0.947],  2500 : [1.060, 0.941],  3000 : [1.064, 0.937],  3500 : [1.067, 0.935],  4000 : [1.069, 0.933],  4500 : [1.070, 0.932],  } if 'bb' in category else { 1000 : [0.978, 1.021],  1100 : [0.976, 1.023],  1200 : [0.973, 1.026],  1300 : [0.970, 1.028],  1400 : [0.967, 1.031],  1500 : [0.966, 1.033],  1600 : [0.964, 1.034],  1700 : [0.963, 1.034],  1800 : [0.963, 1.035],  2000 : [0.962, 1.035],  2500 : [0.963, 1.033],  3000 : [0.970, 1.027],  3500 : [0.976, 1.021],  4000 : [0.981, 1.015],  4500 : [0.985, 1.011],  }
    #else:
    #    print 'b-Tagging algorithm not recognized'
    #    exit()
    #syst["CMS2016_extr_V"] = { 800 : [1.051, 0.949],  1000 : [1.071, 0.929],  1500 : [1.107, 0.893],  2000 : [1.132, 0.868],  2500 : [1.151, 0.849],  3000 : [1.167, 0.833],  3500 : [1.180, 0.820],  4000 : [1.191, 0.809],  4500 : [1.201, 0.799],  } if 'hp' in category else { 800 : [0.979, 1.021],  1000 : [0.969, 1.031],  1500 : [0.952, 1.048],  2000 : [0.940, 1.060],  2500 : [0.931, 1.069],  3000 : [0.924, 1.076],  3500 : [0.918, 1.082],  4000 : [0.913, 1.087],  4500 : [0.908, 1.092],  }
    #syst["pdf_scale"] = { 1000 : [1.067, 0.933],  1100 : [1.068, 0.932],  1200 : [1.070, 0.930],  1300 : [1.073, 0.927],  1400 : [1.076, 0.924],  1500 : [1.079, 0.921],  1600 : [1.082, 0.918],  1700 : [1.085, 0.915],  1800 : [1.088, 0.912],  1900 : [1.092, 0.908],  2000 : [1.095, 0.905],  2100 : [1.100, 0.900],  2200 : [1.106, 0.894],  2300 : [1.111, 0.889],  2400 : [1.116, 0.884],  2500 : [1.121, 0.879],  2600 : [1.129, 0.871],  2700 : [1.137, 0.863],  2800 : [1.145, 0.855],  2900 : [1.153, 0.847],  3000 : [1.160, 0.840],  3100 : [1.173, 0.827],  3200 : [1.185, 0.815],  3300 : [1.197, 0.803],  3400 : [1.210, 0.790],  3500 : [1.222, 0.778],  3600 : [1.244, 0.756],  3700 : [1.265, 0.735],  3800 : [1.287, 0.713],  3900 : [1.309, 0.691],  4000 : [1.330, 0.670],  4100 : [1.361, 0.639],  4200 : [1.392, 0.608],  4300 : [1.423, 0.577],  4400 : [1.453, 0.547],  4500 : [1.484, 0.516],  }
    #syst["qcd_scale"] = { 1000 : [1.039, 0.963],  1100 : [1.045, 0.958],  1200 : [1.050, 0.954],  1300 : [1.054, 0.950],  1400 : [1.059, 0.947],  1500 : [1.063, 0.944],  1600 : [1.067, 0.940],  1700 : [1.070, 0.938],  1800 : [1.074, 0.935],  1900 : [1.077, 0.932],  2000 : [1.080, 0.930],  2100 : [1.083, 0.927],  2200 : [1.086, 0.925],  2300 : [1.089, 0.922],  2400 : [1.092, 0.920],  2500 : [1.096, 0.917],  2600 : [1.098, 0.915],  2700 : [1.101, 0.913],  2800 : [1.104, 0.911],  2900 : [1.107, 0.909],  3000 : [1.109, 0.907],  3100 : [1.112, 0.905],  3200 : [1.114, 0.903],  3300 : [1.117, 0.901],  3400 : [1.120, 0.899],  3500 : [1.122, 0.897],  3600 : [1.124, 0.896],  3700 : [1.126, 0.894],  3800 : [1.129, 0.893],  3900 : [1.131, 0.891],  4000 : [1.133, 0.889],  4100 : [1.135, 0.888],  4200 : [1.137, 0.887],  4300 : [1.138, 0.886],  4400 : [1.140, 0.885],  4500 : [1.142, 0.883],  }

    #syst_sig["CMS2016_sig_p1_jes"] = 1. #0.010
    #syst_sig["CMS2016_sig_p2_jes"] = 1.
    #syst_sig["CMS2016_sig_p2_jer"] = 1. #0.020
    #
    #syst["CMS2016_scale_j"] = 0.010
    #syst["CMS2016_res_j"] = 0.010
#   # syst["CMS2016_scale_mass"] = 0.020
#   # syst["CMS2016_res_mass"] = -0.104
    #if stype=='XVH':
    #    syst["CMS2016_scale_mass"] = [0.004+0.004, -0.009-0.005]
    #    syst["CMS2016_res_mass"] = [-0.101-0.030, +0.112+0.022]
    #    syst["CMS2016_scale_mass_migration"] = { 800 : [0.968, 1.035],  1000 : [0.964, 1.032],  1100 : [0.964, 1.034],  1200 : [0.963, 1.036],  1300 : [0.964, 1.033],  1400 : [0.965, 1.030],  1500 : [0.966, 1.030],  1600 : [0.967, 1.030],  1700 : [0.968, 1.030],  1800 : [0.968, 1.030],  2000 : [0.967, 1.029],  2500 : [0.966, 1.031],  3000 : [0.967, 1.031],  3500 : [0.968, 1.033],  4000 : [0.968, 1.030],  4500 : [0.967, 1.026],  } if 'wr' in channel else { 800 : [1.067, 0.922],  1000 : [1.071, 0.933],  1100 : [1.072, 0.929],  1200 : [1.074, 0.925],  1300 : [1.073, 0.928],  1400 : [1.073, 0.931],  1500 : [1.074, 0.928],  1600 : [1.076, 0.926],  1700 : [1.074, 0.925],  1800 : [1.072, 0.923],  2000 : [1.079, 0.922],  2500 : [1.081, 0.922],  3000 : [1.073, 0.927],  3500 : [1.072, 0.925],  4000 : [1.069, 0.932],  4500 : [1.063, 0.940],  }
    #    syst["CMS2016_res_mass_migration"] = { 800 : [0.964, 1.023],  1000 : [0.957, 1.031],  1100 : [0.957, 1.034],  1200 : [0.956, 1.037],  1300 : [0.956, 1.037],  1400 : [0.956, 1.038],  1500 : [0.954, 1.037],  1600 : [0.951, 1.036],  1700 : [0.953, 1.035],  1800 : [0.955, 1.035],  2000 : [0.953, 1.039],  2500 : [0.952, 1.047],  3000 : [0.948, 1.051],  3500 : [0.945, 1.056],  4000 : [0.941, 1.055],  4500 : [0.943, 1.048],  } if 'wr' in channel else { 800 : [0.981, 1.006],  1000 : [0.999, 0.991],  1100 : [1.001, 0.988],  1200 : [1.002, 0.984],  1300 : [1.003, 0.985],  1400 : [1.004, 0.986],  1500 : [1.006, 0.988],  1600 : [1.009, 0.991],  1700 : [1.006, 0.989],  1800 : [1.004, 0.987],  2000 : [1.009, 0.983],  2500 : [1.010, 0.978],  3000 : [1.010, 0.977],  3500 : [1.015, 0.975],  4000 : [1.003, 0.981],  4500 : [0.990, 0.994],  }
    #elif stype=='XWH':
    #    syst["CMS2016_scale_mass"] = [0.003+0.008, -0.008-0.009]
    #    syst["CMS2016_res_mass"] = [-0.105-0.036, +0.118+0.029]
    #    syst["CMS2016_scale_mass_migration"] = { 800 : [0.974, 1.028],  1000 : [0.971, 1.024],  1100 : [0.970, 1.026],  1200 : [0.969, 1.027],  1300 : [0.970, 1.024],  1400 : [0.971, 1.022],  1500 : [0.973, 1.021],  1600 : [0.975, 1.021],  1700 : [0.976, 1.021],  1800 : [0.977, 1.021],  2000 : [0.974, 1.020],  2500 : [0.975, 1.022],  3000 : [0.974, 1.023],  3500 : [0.974, 1.025],  4000 : [0.974, 1.023],  4500 : [0.976, 1.015],  } if 'wr' in channel else { 800 : [1.113, 0.880],  1000 : [1.128, 0.886],  1100 : [1.131, 0.880],  1200 : [1.135, 0.873],  1300 : [1.138, 0.875],  1400 : [1.142, 0.876],  1500 : [1.142, 0.872],  1600 : [1.142, 0.867],  1700 : [1.139, 0.866],  1800 : [1.137, 0.864],  2000 : [1.156, 0.858],  2500 : [1.143, 0.867],  3000 : [1.131, 0.874],  3500 : [1.134, 0.870],  4000 : [1.124, 0.881],  4500 : [1.105, 0.907],  }
    #    syst["CMS2016_res_mass_migration"] = { 800 : [0.929, 1.064],  1000 : [0.925, 1.071],  1100 : [0.924, 1.074],  1200 : [0.924, 1.076],  1300 : [0.925, 1.075],  1400 : [0.926, 1.074],  1500 : [0.924, 1.073],  1600 : [0.922, 1.072],  1700 : [0.925, 1.071],  1800 : [0.927, 1.070],  2000 : [0.924, 1.073],  2500 : [0.923, 1.085],  3000 : [0.921, 1.087],  3500 : [0.917, 1.091],  4000 : [0.912, 1.094],  4500 : [0.914, 1.085],  } if 'wr' in channel else { 800 : [1.065, 0.902],  1000 : [1.107, 0.872],  1100 : [1.113, 0.862],  1200 : [1.119, 0.852],  1300 : [1.121, 0.850],  1400 : [1.123, 0.848],  1500 : [1.133, 0.845],  1600 : [1.142, 0.842],  1700 : [1.138, 0.839],  1800 : [1.135, 0.836],  2000 : [1.149, 0.824],  2500 : [1.134, 0.819],  3000 : [1.128, 0.832],  3500 : [1.143, 0.831],  4000 : [1.110, 0.840],  4500 : [1.083, 0.869],  }
    #elif stype=='XZH':
    #    syst["CMS2016_scale_mass"] = [+0.008-0.004, -0.011+0.002]
    #    syst["CMS2016_res_mass"] = [-0.092-0.020, +0.102+0.009]
    #    syst["CMS2016_scale_mass_migration"] = { 800 : [0.952, 1.055],  1000 : [0.942, 1.059],  1100 : [0.942, 1.064],  1200 : [0.942, 1.068],  1300 : [0.942, 1.065],  1400 : [0.943, 1.062],  1500 : [0.939, 1.064],  1600 : [0.935, 1.066],  1700 : [0.935, 1.068],  1800 : [0.935, 1.070],  2000 : [0.939, 1.067],  2500 : [0.932, 1.067],  3000 : [0.939, 1.066],  3500 : [0.942, 1.064],  4000 : [0.941, 1.057],  4500 : [0.931, 1.069],  } if 'wr' in channel else { 800 : [1.032, 0.955],  1000 : [1.031, 0.965],  1100 : [1.031, 0.963],  1200 : [1.032, 0.961],  1300 : [1.030, 0.963],  1400 : [1.028, 0.965],  1500 : [1.033, 0.963],  1600 : [1.037, 0.961],  1700 : [1.035, 0.959],  1800 : [1.033, 0.958],  2000 : [1.033, 0.960],  2500 : [1.041, 0.958],  3000 : [1.032, 0.964],  3500 : [1.028, 0.965],  4000 : [1.026, 0.971],  4500 : [1.030, 0.964],  }
    #    syst["CMS2016_res_mass_migration"] = { 800 : [1.069, 0.900],  1000 : [1.069, 0.893],  1100 : [1.072, 0.894],  1200 : [1.075, 0.896],  1300 : [1.072, 0.898],  1400 : [1.070, 0.901],  1500 : [1.067, 0.898],  1600 : [1.065, 0.895],  1700 : [1.065, 0.894],  1800 : [1.065, 0.894],  2000 : [1.069, 0.900],  2500 : [1.065, 0.894],  3000 : [1.062, 0.904],  3500 : [1.063, 0.912],  4000 : [1.055, 0.901],  4500 : [1.057, 0.898],  } if 'wr' in channel else { 800 : [0.916, 1.085],  1000 : [0.923, 1.076],  1100 : [0.923, 1.075],  1200 : [0.922, 1.073],  1300 : [0.925, 1.074],  1400 : [0.927, 1.074],  1500 : [0.928, 1.077],  1600 : [0.929, 1.079],  1700 : [0.928, 1.078],  1800 : [0.926, 1.076],  2000 : [0.928, 1.075],  2500 : [0.930, 1.082],  3000 : [0.927, 1.078],  3500 : [0.922, 1.078],  4000 : [0.922, 1.088],  4500 : [0.919, 1.088],  }
    #else:
    #    print 'Signal not recognized'
    #    exit()
#   # syst["CMS2016_scale_mass_migration"] = [0.056, -0.069] if 'wr' in channel else [-0.050, 0.036]
#   # syst["CMS2016_res_mass_migration"] = -0.049 if 'wr' in channel else +0.050
    #syst["CMS2016_eff_V"] = 0.110 if 'hp' in category else -0.230
    #syst["CMS2016_eff_H"] = 0.060
    #syst["CMS2016_eff_trigger"] = 0.010
    #syst["CMS2016_eff_e"] = 0.010
    #syst["CMS2016_eff_m"] = 0.010
    #syst["CMS2016_eff_met"] = 0.010
    #syst["CMS2016_scale_pu"] = 0.001
    #syst["pdf_accept"] = 0.010
    #syst["CMS2016_lumi"] = 0.025
    # 
    #for i, m in enumerate(massPoints):
    #    isShape = (m <= xmax + binsXmass.averageBinWidth()) if CUTCOUNT and not BIAS else True
    #    signalName = "%s%s_M%d" % (stype, category, m)
    #    signalColor = sample[signalName]['linecolor'] if signalName in sample else 1
    #    
    #    sig_norm, sig_int, nsig = 0., 0., 0.
    #    if not isShape:
    #        sig = getSignal(category, stype, m)
    #        sig_norm = sig[1] # _norm
    #        sig_int = (sig[0].createIntegral(massArg, RooFit.NormSet(massArg), RooFit.Range("X_data_range"))).getVal()
    #        nsig = sig_norm * sig_int
    #    
    #    #*******************************************************#
    #    #                                                       #
    #    #                      Datacard                         #
    #    #                                                       #
    #    #*******************************************************#

    #    generate_datacard(YEAR, category, m, CARDDIR+"%s_M%d%s%s.txt" % (category, m, "_MC" if ISMC else "" , "_test" if options.test, else ""))

    #    card  = "imax 1\n"
    #    card += "jmax *\n"
    #    card += "kmax *\n"
    #    card += "-----------------------------------------------------------------------------------\n"
    #    if isShape:
    #        card += "shapes            %-15s  %-5s    %s%s.root    %s\n" % (signalName, category, WORKDIR, channel, "VH_2016:$PROCESS")
    #        card += "shapes            %-15s  %-5s    %s%s.root    %s\n" % (modelBkg.GetName(), category, WORKDIR, category, "VH_2016:$PROCESS")
    #        card += "shapes            %-15s  %-5s    %s%s.root    %s\n" % ("data_obs", category, WORKDIR, category, "VH_2016:data_obs")
    #    else:
    #        card += "shapes * * FAKE\n"
    #    card += "-----------------------------------------------------------------------------------\n"
    #    card += "bin               %s\n" % category
    #    card += "observation       %0.f\n" % (-1. if isShape else 0.)
    #    card += "-----------------------------------------------------------------------------------\n"
    #    card += "bin                                     %-20s%-20s\n" % (category, category)
    #    card += "process                                 %-20s%-20s\n" % (signalName, modelBkg.GetName()) #"roomultipdf"
    #    card += "process                                 %-20s%-20s\n" % ("0", "1")
    #    if isShape:
    #        card += "rate                                    %-20d%-20f\n" % (1, 1) #signalYield[m].getVal(), nevents
    #    else:
    #        card += "rate                                    %-20.6f%-20.6f\n" % (nsig, nbkg)
    #    card += "-----------------------------------------------------------------------------------\n"
    #    if isShape:
    #        for p in range(1, order+1): card += "%-35s     flatParam\n" % ("CMS2016_"+category+"_p%d_%d" % (order, p))
    #        for s in sorted(syst_sig): card += "%-35s     param     %-20.1f%-20.1f\n" % (s, 0., syst_sig[s])
    #        card += "%-35s     lnU       %-20s%-20.0f\n" % ("CMS2016_"+category+"_norm",    "-", 4.)
    #    else:
    #        card += "%-35s     lnN       %-20s%-20.3f\n" % ("CMS2016_"+category+"_norm",    "-", (1.+nbkgErr/nbkg))
    #    # log-normal uncertainties
    #    for s in sorted(syst):
    #        if type(syst[s]) == dict:
    #            sy = syst[s].get(m, syst[s][min(syst[s].keys(), key=lambda k: abs(k-m))])
    #            card += "%-35s     lnN       %-20s%-20s\n" % (s.replace('_migration', ''), "%.3f/%.3f" % (sy[0], sy[1]), "-")
    #        elif type(syst[s]) == list: card += "%-35s     lnN       %-20s%-20s\n" % (s, "%.3f/%.3f" % (1.+syst[s][0], 1.+syst[s][1]), "-")
    #        else: card += "%-35s     lnN       %-20.3f%-20s\n" % (s,    1.+syst[s], "-")
    #        
    #    # uncertanty groups
    #    card += "theory group = pdf_scale qcd_scale\n"
    #    card += "norm group = CMS2016_"+category+"_norm\n"
    #    if isShape:
    #        card += "shape group = "
    #        for p in range(1, order+1): card += "CMS2016_"+category+"_p%d_%d " % (order, p)
    #        card += "\n"
    #        card += "shapeS group = "
    #        for i in syst_sig.keys(): card += i + " "
    #        card += "\n"
    #    
    #    for s in signalList:
    #        if s == stype: outcard = card
    #        else: outcard = card.replace(stype, s)
    #        outname = CARDDIR+"dijet/%s%s_M%d.txt" % (s, category, m)
    #        cardfile = open(outname, 'w')
    #        cardfile.write(outcard)
    #        cardfile.close()
    #        #print "Datacards for mass", m, "in channel", channel, "saved in", outname

    #    if BIAS:
    #        outcard = card.replace(modelBkg.GetName(), "roomultipdf")
    #        outcard.replace("rate                                    %-20.6f%-20.6f\n" % (1, 1), "rate                                    %-20.6f%-20.6f\n" % (10, 1))
    #        outcard += "%-35s     discrete\n" % ("pdf_index")
    #        outname = CARDDIR+"bias/%s%s_M%d.txt" % (stype, category, m)
    #        cardfile = open(outname, 'w')
    #        cardfile.write(outcard)
    #        cardfile.close()


    #*******************************************************#
    #                                                       #
    #                   Generate workspace                  #
    #                                                       #
    #*******************************************************#
    
    if BIAS:
        gSystem.Load("libHiggsAnalysisCombinedLimit.so")
        from ROOT import RooMultiPdf
        cat = RooCategory("pdf_index", "Index of Pdf which is active");
        pdfs = RooArgList(modelBkg, modelAlt)
        roomultipdf = RooMultiPdf("roomultipdf", "All Pdfs", cat, pdfs)
        normulti = RooRealVar("roomultipdf_norm", "Number of background events", nevents, 0., 1.e6)
    
    # create workspace
    w = RooWorkspace("Zprime_"+YEAR, "workspace")
    # Dataset
    #if isData: getattr(w, "import")(setData, RooFit.Rename("data_obs"))
    #else: getattr(w, "import")(setToys, RooFit.Rename("data_obs"))
    getattr(w, "import")(setToys, RooFit.Rename("data_obs")) ## the original lines above set a newly generated toy dataset as data_obs if MC is chosen. I don't see why this should be done and thus use the setData as data_obs for both FIXME
    if BIAS:
        getattr(w, "import")(cat, RooFit.Rename(cat.GetName()))
        getattr(w, "import")(normulti, RooFit.Rename(normulti.GetName()))
        getattr(w, "import")(roomultipdf, RooFit.Rename(roomultipdf.GetName()))
    getattr(w, "import")(modelBkg, RooFit.Rename(modelBkg.GetName()))
    getattr(w, "import")(modelAlt, RooFit.Rename(modelAlt.GetName()))
    getattr(w, "import")(normzBkg, RooFit.Rename(normzBkg.GetName()))
    #getattr(w, "import")(roomultipdf, RooFit.Rename(roomultipdf.GetName()))
    #for m in signal.keys():
    #    getattr(w, "import")(signal[m], RooFit.Rename(signal[m].GetName()))
    #    getattr(w, "import")(signalYield[m], RooFit.Rename(signalYield[m].GetName()))
    #w.Print()
    w.writeToFile(WORKDIR+"%s_%s%s.root" % (DATA_TYPE+"_"+YEAR, category, "_test" if options.test else ""), True)
    print "Workspace", WORKDIR+"%s_%s%s.root" % (DATA_TYPE+"_"+YEAR, category, "_test" if options.test else ""), "saved successfully"
    
    if VERBOSE: raw_input("Press Enter to continue...")
    # ======   END PLOT   ======
    


def fisherTest(RSS1, RSS2, o1, o2, N):
    #print "Testing functions with parameters", o1, "and", o2, "with RSS", RSS1, "and", RSS2
    #if (RSS1-RSS2)/(RSS2) < 0.125: return True
    #return (RSS1-RSS2)/RSS1 < (o2-o1)/o1
    dof1 = N - o1
    dof2 = N - o2
    n1 = N - dof1 - 1
    n2 = N - dof2 - 1
    F = ((RSS1-RSS2)/(n2-n1)) / (RSS2/(N-n2))
    #F_dist = TF1("F_distr", "TMath::Sqrt( (TMath::Power([0]*x,[0]) * TMath::Power([1],[1])) / (TMath::Power([0]*x + [1],[0]+[1])) ) / (x*TMath::Beta([0]/2,[1]/2))", 0, 1000)
    #F_dist.SetParameter(0, n2-n1)
    #F_dist.SetParameter(1, N-n2)
    #CL = 1 - F_dist.Integral(0.00000001, F)
    CL =  1.-TMath.FDistI(F, n2-n1, N-n2)
    #print F, N, n2-n1, N-n2, TMath.FDistI(F, n2-n1, N-n2)
    #print "F-test:", o1+1, "par vs", o2, "par & : F =", F, ", CL = %.4f" % CL
    
    return CL



def drawFit(name, category, variable, model, dataset, binning, fitRes=[], norm=-1):
    isData = (not 'MC' in dataset.GetTitle())
    order = int(name[-1])
    npar = fitRes[0].floatParsFinal().getSize() if len(fitRes)>0 else 0
    varArg = RooArgSet(variable)
    
    c = TCanvas("c_"+category, category, 800, 800)
    c.Divide(1, 2)
    setTopPad(c.GetPad(1), RATIO)
    setBotPad(c.GetPad(2), RATIO)
    c.cd(1)
    frame = variable.frame()
    setPadStyle(frame, 1.25, True)
    print "dataset.plotOn(frame, RooFit.Binning(binning), RooFit.Invisible())"
    dataset.plotOn(frame, RooFit.Binning(binning), RooFit.Invisible())
    print "."
    if len(fitRes) > 0: model.plotOn(frame, RooFit.VisualizeError(fitRes[0], 1, False), RooFit.Normalization(norm if norm>0 else dataset.sumEntries(), RooAbsReal.NumEvent), RooFit.LineColor(getColor(order, category)[0]), RooFit.FillColor(getColor(order, category)[1]), RooFit.FillStyle(1001), RooFit.DrawOption("FL"))
    print "model.plotOn(frame, RooFit.Normalization(norm if norm>0 else dataset.sumEntries(), RooAbsReal.NumEvent), RooFit.LineColor(getColor(order, category)[0]), RooFit.FillColor(getColor(order, category)[1]), RooFit.FillStyle(1001), RooFit.DrawOption('L'), RooFit.Name(model.GetName()))"
    model.plotOn(frame, RooFit.Normalization(norm if norm>0 else dataset.sumEntries(), RooAbsReal.NumEvent), RooFit.LineColor(getColor(order, category)[0]), RooFit.FillColor(getColor(order, category)[1]), RooFit.FillStyle(1001), RooFit.DrawOption("L"), RooFit.Name(model.GetName()))
    print "."
    model.paramOn(frame, RooFit.Label(model.GetTitle()), RooFit.Layout(0.45, 0.95, 0.94), RooFit.Format("NEAU"))
    print "graphData = dataset.plotOn(frame, RooFit.Binning(binning), RooFit.DataError(RooAbsData.Poisson if isData else RooAbsData.SumW2), RooFit.DrawOption('PE0'), RooFit.Name(dataset.GetName()))"
    graphData = dataset.plotOn(frame, RooFit.Binning(binning), RooFit.DataError(RooAbsData.Poisson if isData else RooAbsData.SumW2), RooFit.DrawOption("PE0"), RooFit.Name(dataset.GetName()))
    print "."
    fixData(graphData.getHist(), True, True, not isData)
    pulls = frame.pullHist(dataset.GetName(), model.GetName(), True)
    residuals = frame.residHist(dataset.GetName(), model.GetName(), False, True) # this is y_i - f(x_i)
    roochi2 = frame.chiSquare()#dataset.GetName(), model.GetName()) #model.GetName(), dataset.GetName()
    frame.SetMaximum(frame.GetMaximum()*10)
    frame.SetMinimum(max(frame.GetMinimum(), 1.e-2))
    c.GetPad(1).SetLogy()
    frame.Draw()

    drawAnalysis(category)
    drawRegion(category, True)
    drawCMS(LUMI, "Simulation Preliminary")

    c.cd(2)
    frame_res = variable.frame()
    setPadStyle(frame_res, 1.25)
    frame_res.addPlotable(pulls, "P")
    setBotStyle(frame_res, RATIO, False)
    frame_res.GetYaxis().SetRangeUser(-5, 5)
    frame_res.GetYaxis().SetTitle("(N^{data}-N^{bkg})/#sigma")
    frame_res.Draw()
    fixData(pulls, False, True, False)

    # calculate RSS
    nbins, res, rss, chi1, chi2 = 0, 0., 0., 0., 0.
    hist = graphData.getHist()
    xmin, xmax = array('d', [0.]), array('d', [0.])
    dataset.getRange(variable, xmin, xmax)
    #print "hist.GetN() =", hist.GetN()
    for i in range(0, hist.GetN()):
        if hist.GetX()[i] - hist.GetErrorXlow(i) > xmax[0] and hist.GetX()[i] + hist.GetErrorXhigh(i) > xmax[0]: continue# and abs(pulls.GetY()[i]) < 5:
        if hist.GetY()[i] <= 0.: continue
        #print "i =", i
        #print "residuals.GetY() =", residuals.GetY()
        #print "residuals.GetY()[i] =", residuals.GetY()[i]
        res += residuals.GetY()[i]
        rss += residuals.GetY()[i]**2
        #print i, pulls.GetY()[i]
        chi1 += abs(pulls.GetY()[i])
        chi2 += pulls.GetY()[i]**2
        nbins = nbins + 1
        #data = hist.GetY()[i]
        #bkg = norm * (model.createIntegral(varArg, RooFit.NormSet(varArg), RooFit.Range(bins[i], bins[i+1]))).getVal() / (bins[i+1] - bins[i])
        #bkg2 = model.Eval( (bins[i+1] - bins[i])/2. )
        #print i, bins[i], bins[i+1], data, bkg#, bkg2
    rss = math.sqrt(rss)
    out = {"chi2" : chi2, "chi1" : chi1, "rss" : rss, "res" : res, "nbins" : nbins, "npar" : npar}
    drawChi2(chi2, binning.numBins() - npar)
    line = drawLine(variable.getMin(), 0, variable.getMax(), 0)

    if len(name) > 0 and len(category) > 0:
        c.SaveAs(PLOTDIR+"/"+name+"_"+category+".pdf")
        c.SaveAs(PLOTDIR+"/"+name+"_"+category+".png")

#    if( hMassNEW.GetXaxis().GetBinLowEdge(bin+1)>=fFitXmin and hMassNEW.GetXaxis().GetBinUpEdge(bin-1)<=fFitXmax ):
#       NumberOfVarBins += 1
#       data = hMassNEW.GetBinContent(bin)
#       # data = g.Integral(hMassNEW.GetXaxis().GetBinLowEdge(bin) , hMassNEW.GetXaxis().GetBinUpEdge(bin) )
#       err_data_low = g.GetErrorYlow(bin-1) 
#       err_data_high= g.GetErrorYhigh(bin-1)
#       fit = BKGfit.Integral(hMassNEW.GetXaxis().GetBinLowEdge(bin) , hMassNEW.GetXaxis().GetBinUpEdge(bin) )
#       fit = fit / ( hMassNEW.GetBinWidth(bin) )
#       # fit = BKGfit.Eval(hMassNEW.GetBinCenter(bin)) #yields same results
#       if(fit > data):
#         err_tot = err_data_high
#       else:
#         err_tot = err_data_low
#       fit_residual = (data - fit) / err_tot
#       err_fit_residual = 1
#       
#       if (hMassNEW.GetBinContent(bin)>0):
#         NumberOfObservations_VarBin+=1
#         chi2_VarBin += pow( (data - fit) , 2 ) / pow( err_tot , 2 )    
#chi2_VarBin_notNorm += pow( (data - fit) , 2 )
    #print "  Integral:", integral, "-", norm
    #print "  RSS:", rss
    #print "  Chi2:", chi2, " - ", roochi2
    return out

def getSignal(cat, sig, mass):   
    #try:
    #    sample = "" # FIXME
    #    file = TFile(NTUPLEDIR+sample+"/"+sample+"_flatTuple_0.root", "READ")
    #    w = file.Get("VH_2016")
    #    signal = w.pdf("%s%s_M%d" % (sig, cat, mass))
    #    norm = w.var("%s%s_M%d_norm" % (sig, cat, mass))
    #    xs = w.var("%s%s_M%d_xs" % (sig, cat, mass))
    #    return [signal, norm.getVal(), xs.getVal()]
    #except:
    #    print "WARNING: failed to get signal pdf"
    #    return [None, 0., 0.]
    return [None, 0., 0. ]

def generate_datacard(year, category, masspoint, outname):
    card  = "imax 1\n"
    card += "jmax 1\n"
    card += "kmax *\n"
    card += "-----------------------------------------------------------------------------------\n"
    card += "shapes            sig  *    signal_workspace/MC_signal_{year}_{category}.root     Zprime_{year}:Zprimebb_{masspoint}\n".format(year=year, category=category, masspoint=masspoint)
    card += "shapes            bkg  *    bkg_workspace/data_{year}_{category}.root    Zprime_{year}:Bkg_{category}\n".format(year=year, category=category)
    card += "shapes            data_obs  *    bkg_workspace/data_{year}_{category}.root    Zprime_{year}:data_obs\n".format(year=year, category=category)
    card += "-----------------------------------------------------------------------------------\n"
    card += "bin               {}\n".format(category)
    card += "observation       -1\n"
    card += "-----------------------------------------------------------------------------------\n"
    card += "bin                                     {:20}{:20}\n".format(category, category)
    card += "process                                 {:20}{:20}\n".format("sig", "bkg") 
    card += "process                                 {:20}{:20}\n".format("0", "1")
    card += "rate                                    {:20}{:20}\n".format(1, 1) 
    card += "-----------------------------------------------------------------------------------\n"
    cardfile = open(outname, 'w')
    cardfile.write(card)
    cardfile.close()
    print "Datacards for mass", masspoint, "in category", ccategory, "saved in", outname


if __name__ == "__main__":
    if options.category!='':
        dijet(options.category)
    else:
        jobs=[]
        for c in categories:
            p = multiprocessing.Process(target=dijet, args=(c,))
            jobs.append(p)
            p.start()
