#! /usr/bin/env python

import os, multiprocessing
import copy
import math
from array import array
from ROOT import ROOT, gROOT, gStyle, gRandom, TSystemDirectory
from ROOT import TFile, TChain, TTree, TCut, TF1, TH1F, TH2F, THStack
from ROOT import TGraph, TGraphErrors, TGraphAsymmErrors, TVirtualFitter
from ROOT import TStyle, TCanvas, TPad
from ROOT import TLegend, TLatex, TText, TLine

from samples import sample
from variables import variable
from aliases import alias, aliasSM, deepFlavour, working_points
from utils import *

########## SETTINGS ##########

import optparse
usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage)
parser.add_option("-v", "--variable", action="store", type="string", dest="variable", default="")
parser.add_option("-c", "--cut", action="store", type="string", dest="cut", default="")
parser.add_option("-y", "--year", action="store", type="string", dest="year", default="run2")
parser.add_option("-b", "--btagging", action="store", type="string", dest="btagging", default="tight")
parser.add_option("-n", "--norm", action="store_true", default=False, dest="norm")
#parser.add_option("-t", "--top", action="store_true", default=False, dest="top")
#parser.add_option("-a", "--all", action="store_true", default=False, dest="all")
parser.add_option("-B", "--blind", action="store_true", default=False, dest="blind")
parser.add_option("-f", "--final", action="store_true", default=False, dest="final")
(options, args) = parser.parse_args()

########## SETTINGS ##########

gROOT.SetBatch(True)
#gROOT.ProcessLine("TSystemDirectory::SetDirectory(0)")
#gROOT.ProcessLine("TH1::AddDirectory(kFALSE);")
gStyle.SetOptStat(0)
#TSystemDirectory.SetDirectory(0)

BTAGGING    = options.btagging
NTUPLEDIR   = "/afs/cern.ch/work/m/msommerh/public/Zprime_to_bb_Analysis/Skim/"
SIGNAL      = 1 # Signal magnification factor
RATIO       = 4 # 0: No ratio plot; !=0: ratio between the top and bottom pads
NORM        = options.norm
PARALLELIZE = False
BLIND       = False
LUMI        = {"run2" : 137190, "2016" : 35920, "2017" : 41530, "2018" : 59740}
XRANGE      = (1400., 9000.)

########## SAMPLES ##########
data = ["data_obs"]
back = ["TTbar", "QCD"]
#back = ["VV", "ST", "TTbarSL", "WJetsToLNu_HT", "DYJetsToNuNu_HT", "DYJetsToLL_HT"]
sign = ['ZpBB_M2000', 'ZpBB_M4000', 'ZpBB_M6000']#, 'ZpBB_M8000']
#sign = ['ZpBB_M1000', 'ZpBB_M1200', 'ZpBB_M1400', 'ZpBB_M1600', 'ZpBB_M1800', 'ZpBB_M2000', 'ZpBB_M2500', 'ZpBB_M3000', 'ZpBB_M3500', 'ZpBB_M4000', 'ZpBB_M4500', 'ZpBB_M5000', 'ZpBB_M5500', 'ZpBB_M6000', 'ZpBB_M7000', 'ZpBB_M8000']
########## ######## ##########

if BTAGGING not in ['tight', 'medium', 'loose', 'semimedium']:
    print "unknown btagging requirement:", BTAGGING
    sys.exit()

jobs = []

def plot(var, cut, year, norm=False, nm1=False):
    ### Preliminary Operations ###
    treeRead = not cut in ["nnqq", "en", "enqq", "mn", "mnqq", "ee", "eeqq", "mm", "mmqq", "em", "emqq", "qqqq"] # Read from tree
    channel = cut
    isBlind = BLIND and 'SR' in channel
    isAH = False #'qqqq' in channel or 'hp' in channel or 'lp' in channel
    showSignal = False if 'SB' in cut or 'TR' in cut else True #'SR' in channel or channel=='qqqq'#or len(channel)==5
    stype = "HVT model B"
    if len(sign)>0 and 'AZh' in sign[0]: stype = "2HDM"
    elif len(sign)>0 and  'monoH' in sign[0]: stype = "Z'-2HDM m_{A}=300 GeV"
    if treeRead:
        for k in sorted(alias.keys(), key=len, reverse=True):
            if BTAGGING=='semimedium':
                #if k in cut: cut = cut.replace(k, aliasSM[k].format(b_threshold_medium=deepFlavour['medium'][year], b_threshold_loose=deepFlavour['loose'][year]))              
                if k in cut: cut = cut.replace(k, aliasSM[k])
            else:
                #if k in cut: cut = cut.replace(k, alias[k].format(b_threshold=deepFlavour[BTAGGING][year]))
                if k in cut: cut = cut.replace(k, alias[k].format(WP=working_points[BTAGGING]))
    
    # Determine Primary Dataset
    pd = sample['data_obs']['files']
    
    print "Plotting from", ("tree" if treeRead else "file"), var, "in", channel, "channel with:"
    print "  dataset:", pd
    print "  cut    :", cut
    
    ### Create and fill MC histograms ###
    # Create dict
    file = {}
    tree = {}
    hist = {}
    
    ### Create and fill MC histograms ###
    for i, s in enumerate(data+back+sign):
        if treeRead: # Project from tree
            tree[s] = TChain("tree")
            for j, ss in enumerate(sample[s]['files']):
                if not 'data' in s or ('data' in s and ss in pd):
                    if year=="run2" or year in ss:
                        tree[s].Add(NTUPLEDIR + ss + ".root")
            if variable[var]['nbins']>0: hist[s] = TH1F(s, ";"+variable[var]['title']+";Events / ( "+str((variable[var]['max']-variable[var]['min'])/variable[var]['nbins'])+" GeV );"+('log' if variable[var]['log'] else ''), variable[var]['nbins'], variable[var]['min'], variable[var]['max'])
            else: hist[s] = TH1F(s, ";"+variable[var]['title'], len(variable[var]['bins'])-1, array('f', variable[var]['bins']))
            hist[s].Sumw2()
            cutstring = "(eventWeightLumi)" + ("*("+cut+")" if len(cut)>0 else "")
            tree[s].Project(s, var, cutstring)
            if not tree[s].GetTree()==None: hist[s].SetOption("%s" % tree[s].GetTree().GetEntriesFast())
        else: # Histogram written to file
            for j, ss in enumerate(sample[s]['files']):
                if not 'data' in s or ('data' in s and ss in pd):
                    file[ss] = TFile(NTUPLEDIR + ss + ".root", "R")
                    if file[ss].IsZombie():
                        print "WARNING: file", NTUPLEDIR + ss + ".root", "does not exist"
                        continue
                    tmphist = file[ss].Get(cut+"/"+var)
                    if tmphist==None: continue
                    if not s in hist.keys(): hist[s] = tmphist
                    else: hist[s].Add(tmphist)
        hist[s].Scale(sample[s]['weight'] if hist[s].Integral() >= 0 else 0)
        hist[s].SetFillColor(sample[s]['fillcolor'])
        hist[s].SetFillStyle(sample[s]['fillstyle'])
        hist[s].SetLineColor(sample[s]['linecolor'])
        hist[s].SetLineStyle(sample[s]['linestyle'])

    
    # X_mass rebin
#    if var=='X_mass' or var=='X_tmass':
#        if 'XZhnn' in channel: rebin = 10
#        elif 'XWh' in channel: rebin = 5
#        else: rebin = 2
#        for i, s in enumerate(data+back+sign): hist[s].Rebin(rebin)
    if channel.endswith('TR') and channel.replace('TR', '') in topSF:
        hist['TTbarSL'].Scale(topSF[channel.replace('TR', '')][0])
        hist['ST'].Scale(topSF[channel.replace('TR', '')][0])
    
    hist['BkgSum'] = hist['data_obs'].Clone("BkgSum") if 'data_obs' in hist else hist[back[0]].Clone("BkgSum")
    hist['BkgSum'].Reset("MICES")
    hist['BkgSum'].SetFillStyle(3003)
    hist['BkgSum'].SetFillColor(1)
    for i, s in enumerate(back): hist['BkgSum'].Add(hist[s])
    
    if options.norm:
        for i, s in enumerate(back + ['BkgSum']): hist[s].Scale(hist[data[0]].Integral()/hist['BkgSum'].Integral())

    # Create data and Bkg sum histograms
    if options.blind or 'SR' in channel:
        hist['data_obs'] = hist['BkgSum'].Clone("data_obs")
        hist['data_obs'].Reset("MICES")
    # Set histogram style
    hist['data_obs'].SetMarkerStyle(20)
    hist['data_obs'].SetMarkerSize(1.25)
    
    for i, s in enumerate(data+back+sign+['BkgSum']): addOverflow(hist[s], False) # Add overflow
    for i, s in enumerate(sign): hist[s].SetLineWidth(3)
    for i, s in enumerate(sign): sample[s]['plot'] = True#sample[s]['plot'] and s.startswith(channel[:2])
    
    
    if isAH:
        for i, s in enumerate(back):
            hist[s].SetFillStyle(3005)
            hist[s].SetLineWidth(2)
        #for i, s in enumerate(sign):
        #    hist[s].SetFillStyle(0)
        if not var=="Events":
            sfnorm = hist[data[0]].Integral()/hist['BkgSum'].Integral()
            print "Applying SF:", sfnorm
            for i, s in enumerate(back+['BkgSum']): hist[s].Scale(sfnorm)
        if BLIND and var.endswith("Mass"):
            for i, s in enumerate(data+back+['BkgSum']):
                first, last = hist[s].FindBin(65), hist[s].FindBin(135)
                for j in range(first, last): hist[s].SetBinContent(j, -1.e-4)
        if BLIND and var.endswith("Tau21"):
            for i, s in enumerate(data):
                first, last = hist[s].FindBin(0), hist[s].FindBin(0.6)
                for j in range(first, last): hist[s].SetBinContent(j, -1.e-4)
    
    # Create stack
    bkg = THStack("Bkg", ";"+hist['BkgSum'].GetXaxis().GetTitle()+";Events / ( "+str((variable[var]['max']-variable[var]['min'])/variable[var]['nbins'])+" GeV )")
    for i, s in enumerate(back): bkg.Add(hist[s])
    
    
    # Legend
    leg = TLegend(0.65, 0.6, 0.95, 0.9)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0) #1001
    leg.SetFillColor(0)
    if len(data) > 0:
        leg.AddEntry(hist[data[0]], sample[data[0]]['label'], "pe")
    for i, s in reversed(list(enumerate(['BkgSum']+back))):
        leg.AddEntry(hist[s], sample[s]['label'], "f")
    if showSignal:
        for i, s in enumerate(sign):
            if sample[s]['plot']: leg.AddEntry(hist[s], sample[s]['label'], "fl")
        
    leg.SetY1(0.9-leg.GetNRows()*0.05)
    
    
    # --- Display ---
    c1 = TCanvas("c1", hist.values()[0].GetXaxis().GetTitle(), 800, 800 if RATIO else 600)
    
    if RATIO:
        c1.Divide(1, 2)
        setTopPad(c1.GetPad(1), RATIO)
        setBotPad(c1.GetPad(2), RATIO)
    c1.cd(1)
    c1.GetPad(bool(RATIO)).SetTopMargin(0.06)
    c1.GetPad(bool(RATIO)).SetRightMargin(0.05)
    c1.GetPad(bool(RATIO)).SetTicks(1, 1)
    
    log = "log" in hist['BkgSum'].GetZaxis().GetTitle()
    if log: c1.GetPad(bool(RATIO)).SetLogy()
        
    # Draw
    bkg.Draw("HIST") # stack
    hist['BkgSum'].Draw("SAME, E2") # sum of bkg
    if not isBlind and len(data) > 0: hist['data_obs'].Draw("SAME, PE") # data
    #data_graph.Draw("SAME, PE")
    if showSignal:
        smagn = 1. #if treeRead else 1.e2 #if log else 1.e2
        for i, s in enumerate(sign):
    #        if sample[s]['plot']:
                hist[s].Scale(smagn)
                hist[s].Draw("SAME, HIST") # signals Normalized, hist[s].Integral()*sample[s]['weight']
        textS = drawText(0.80, 0.9-leg.GetNRows()*0.05 - 0.02, stype+" (x%d)" % smagn, True)
    #bkg.GetYaxis().SetTitleOffset(bkg.GetYaxis().GetTitleOffset()*1.075)
    bkg.GetYaxis().SetTitleOffset(0.9)
    #bkg.GetYaxis().SetTitleOffset(2.)
    bkg.SetMaximum((5. if log else 1.25)*max(bkg.GetMaximum(), hist['data_obs'].GetBinContent(hist['data_obs'].GetMaximumBin())+hist['data_obs'].GetBinError(hist['data_obs'].GetMaximumBin())))
    #if bkg.GetMaximum() < max(hist[sign[0]].GetMaximum(), hist[sign[-1]].GetMaximum()): bkg.SetMaximum(max(hist[sign[0]].GetMaximum(), hist[sign[-1]].GetMaximum())*1.25)
    bkg.SetMinimum(max(min(hist['BkgSum'].GetBinContent(hist['BkgSum'].GetMinimumBin()), hist['data_obs'].GetMinimum()), 5.e-1)  if log else 0.)
    if log:
        bkg.GetYaxis().SetNoExponent(bkg.GetMaximum() < 1.e4)
        #bkg.GetYaxis().SetMoreLogLabels(True)
    bkg.GetXaxis().SetRangeUser(XRANGE[0], XRANGE[1])  ## newly inserted 
 
    #if log: bkg.SetMinimum(1)
    leg.Draw()
    drawCMS(LUMI[year], "Preliminary")
    drawRegion('XVH'+channel, True)
    drawAnalysis(channel)
    
    #if nm1 and not cutValue is None: drawCut(cutValue, bkg.GetMinimum(), bkg.GetMaximum()) #FIXME
    #if len(sign) > 0:
    #    if channel.startswith('X') and len(sign)>0: drawNorm(0.9-0.05*(leg.GetNRows()+1), "#sigma(X) = %.1f pb" % 1.)
    
    setHistStyle(bkg, 1.2 if RATIO else 1.1)
    setHistStyle(hist['BkgSum'], 1.2 if RATIO else 1.1)
       
    if RATIO:
        c1.cd(2)
        err = hist['BkgSum'].Clone("BkgErr;")
        err.SetTitle("")
        err.GetYaxis().SetTitle("Data / Bkg")
        err.GetXaxis().SetRangeUser(XRANGE[0], XRANGE[1])  ## newly inserted     
        for i in range(1, err.GetNbinsX()+1):
            err.SetBinContent(i, 1)
            if hist['BkgSum'].GetBinContent(i) > 0:
                err.SetBinError(i, hist['BkgSum'].GetBinError(i)/hist['BkgSum'].GetBinContent(i))
        setBotStyle(err)
        errLine = err.Clone("errLine")
        errLine.SetLineWidth(1)
        errLine.SetFillStyle(0)
        res = hist['data_obs'].Clone("Residues")
        for i in range(0, res.GetNbinsX()+1):
            if hist['BkgSum'].GetBinContent(i) > 0: 
                res.SetBinContent(i, res.GetBinContent(i)/hist['BkgSum'].GetBinContent(i))
                res.SetBinError(i, res.GetBinError(i)/hist['BkgSum'].GetBinContent(i))
        setBotStyle(res)
        #err.GetXaxis().SetLabelOffset(err.GetXaxis().GetLabelOffset()*5)
        #err.GetXaxis().SetTitleOffset(err.GetXaxis().GetTitleOffset()*2)
        err.Draw("E2")
        errLine.Draw("SAME, HIST")
        if not isBlind and len(data) > 0:
            res.Draw("SAME, PE0")
            #res_graph.Draw("SAME, PE0")
            if len(err.GetXaxis().GetBinLabel(1))==0: # Bin labels: not a ordinary plot
                drawRatio(hist['data_obs'], hist['BkgSum'])
                drawStat(hist['data_obs'], hist['BkgSum'])

    c1.Update()

    if gROOT.IsBatch():
        if channel=="": channel="nocut"
        varname = var.replace('.', '_').replace('()', '')
        if not os.path.exists("plots/"+channel): os.makedirs("plots/"+channel)
        suffix = ''
        if "b" in channel: suffix+="_"+BTAGGING
        c1.Print("plots/"+channel+"/"+varname+"_"+year+suffix+".png")
        c1.Print("plots/"+channel+"/"+varname+"_"+year+suffix+".pdf")
    
    # Print table
    printTable(hist, sign)
    
    if not gROOT.IsBatch(): raw_input("Press Enter to continue...")

    
########## ######## ##########


def plotAll():
    gROOT.SetBatch(True)
    
    hists = {}
    
    file = TFile(NTUPLEDIR + "TT.root", 'READ')
    file.cd()
    # Looping over file content
    for key in file.GetListOfKeys():
        obj = key.ReadObj()
        # Histograms
        if obj.IsA().InheritsFrom('TH1'): continue
        #    hists.append(obj.GetName())
        # Tree
        elif obj.IsA().InheritsFrom('TTree'): continue
        # Directories
        if obj.IsFolder() and (obj.GetName().endswith('qq') or len(obj.GetName())==2):
            subdir = obj.GetName()
            hists[subdir] = []
            file.cd(subdir)
            for subkey in file.GetDirectory(subdir).GetListOfKeys():
                subobj = subkey.ReadObj()
                if subobj.IsA().InheritsFrom('TH1'):
                    hists[subdir].append(subobj.GetName())
            file.cd('..')
    file.Close() 
    
    for c, l in hists.iteritems():
        #if not os.path.exists("plots/"+c):
        #    os.mkdir("plots/"+c)
        if 'qqqq' in c: continue
        if not len(c) > 2: continue
        if not 'nn' in c: continue
        for h in l:
            plot(h, c)


#if options.all: plotAll()
#elif options.norm: plotNorm(options.variable, options.cut)
#elif options.top: plotTop()
plot(options.variable, options.cut, options.year)

