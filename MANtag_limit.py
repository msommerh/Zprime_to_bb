#! /usr/bin/env python

###
### Macro for creating the exclusion limits plots from the combine outputs.
###

import os, sys, getopt
import copy
import time
import math
from array import array
from ROOT import gROOT, gRandom
from ROOT import TFile, TTree, TCut, TH1F, TH2F, TGraph, TGraph2D, TGraphErrors, TGraphAsymmErrors
from ROOT import TStyle, TCanvas, TPad
from ROOT import TLegend, TLatex, TText, TColor

#from DMPD.Heppy.tools.samples import *
from utils import *
from hvtXs import HVT

#from thdmXs import THDM

# Combine output
# 0 - Observed Limit
# 1 - Expected  2.5%
# 2 - Expected 16.0%
# 3 - Expected 50.0%
# 4 - Expected 84.0%
# 5 - Expected 97.5%
# 6 - Significance
# 7 - p-value
# 8 - Best fit r
# 9 - Best fit r down
#10 - Best fit r up

import optparse
usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage)
parser.add_option("-y", "--year", action="store", type="string", dest="year",default="run2c")
#parser.add_option("-M", "--isMC", action="store_true", default=False, dest="isMC")
parser.add_option("-c", "--category", action="store", type="string", dest="category", default="")
parser.add_option("-B", "--blind", action="store_true", default=False, dest="blind")
parser.add_option("-b", "--btagging", action="store", type="string", dest="btagging", default="medium")
parser.add_option("-C", "--compare", action="store_true", dest="compare", default=False)
(options, args) = parser.parse_args()
gStyle.SetOptStat(0)

gROOT.SetBatch(True)

luminosities = {'2016':35920., '2017':41530., '2018':59740., 'run2':137190.}

#HTOBB       = 0.5824#0.577
ZPTOBB      = 1.
LUMI        = 35867
MAXIMUM     = {'XVHsl' : 4500., 'XWHsl' : 4500., 'XZHsl' : 3500., 'bb':100}
BTAGGING    = options.btagging
YEAR        = options.year
ISMC        = True
CATEGORY    = options.category

if YEAR not in ['2016', '2017', '2018', 'run2', 'run2c']:
    print "unknown year:", YEAR
    sys.exit()

if BTAGGING not in ['tight', 'medium', 'loose', 'semimedium']:
    print "unknown btagging requirement:", BTAGGING
    sys.exit()

if CATEGORY not in ['', 'bb', 'bq', 'mumu']:
    print "unknown btagging category"
    sys.exit()

if YEAR=='run2c':
    YEAR='run2'
    SY=True
    print "Plotting the result from combine on separate years for run2..."
else:
    SY=False

LUMI        = luminosities[YEAR]

SIGNALS = range(1600, 8000+1, 100)

theoryLabel = {'B3' : "HVT model B (g_{V}=3)", 'A1' : "HVT model A (g_{V}=1)", 'T1' : "2HDM Type-I", 'T2' : "2HDM Type-II"}
theoryLineColor = {'B3' : 629, 'A1' : 616-3, 'T1' : 880-4, 'T2' : 602}
theoryFillColor = {'B3' : 625, 'A1' : 616-7, 'T1' : 880-9, 'T2' : 856}
theoryFillStyle = {'B3' : 3002, 'A1' : 3013, 'T1' : 3002, 'T2' : 3013}


def fillValues(filename):
    val = {}
    mass = []
    for i, s in enumerate(SIGNALS):
        try:
            file = open(filename % s, 'r')
            if file==None:
                print "Signal", filename % s, "does not exist"
                continue
            val[s] = file.read().splitlines()
            if len(val[s]) <= 1:
                #signals.remove(s)
                print "Signal", filename % s, "has no values"
                continue
            for i, f in enumerate(val[s]): val[s][i] = float(val[s][i])
            if 'fullCls' in filename: val[1:5]=sorted(val[1:5])
            if not s in mass: mass.append(s)
        except:
            print "File", filename % s, "does not exist"
            pass
    return mass, val


def limit():
    method = ''
    channel = "bb"
    particleP = "Z'"
    particle = channel
    multF = ZPTOBB
    THEORY = ['A1', 'B3']
    
    suffix = "_"+BTAGGING
    if ISMC: suffix += "_MC"
    if SY: suffix += "_comb"
    #if method=="cls": suffix="_CLs"

    if SY:
        filename = "./combine/limits/MANtag_study/" + BTAGGING + "/combined_run2/"+ YEAR + "_M%d.txt"
    else:
        filename = "./combine/limits/MANtag_study/" + BTAGGING + "/"+ YEAR + "_M%d.txt"
    if CATEGORY!="": 
        filename = filename.replace(BTAGGING + "/", BTAGGING + "/single_category/"+CATEGORY+"_")
        suffix += "_"+CATEGORY
    if ISMC: filename = filename.replace(".txt", "_MC.txt")
    mass, val = fillValues(filename)

    #print "mass =",mass
    #print "val =", val

    Obs0s = TGraph()
    Exp0s = TGraph()
    Exp1s = TGraphAsymmErrors()
    Exp2s = TGraphAsymmErrors()
    Sign = TGraph()
    pVal = TGraph()
    Best = TGraphAsymmErrors()
    Theory = {}

    for i, m in enumerate(mass):
        if not m in val:
            print "Key Error:", m, "not in value map"
            continue

        n = Exp0s.GetN()
        Obs0s.SetPoint(n, m, val[m][0]*multF)
        Exp0s.SetPoint(n, m, val[m][3]*multF)
        Exp1s.SetPoint(n, m, val[m][3]*multF)
        Exp1s.SetPointError(n, 0., 0., val[m][3]*multF-val[m][2]*multF, val[m][4]*multF-val[m][3]*multF)
        Exp2s.SetPoint(n, m, val[m][3]*multF)
        Exp2s.SetPointError(n, 0., 0., val[m][3]*multF-val[m][1]*multF, val[m][5]*multF-val[m][3]*multF)
        if len(val[m]) > 6: Sign.SetPoint(n, m, val[m][6])
        if len(val[m]) > 7: pVal.SetPoint(n, m, val[m][7])
        if len(val[m]) > 8: Best.SetPoint(n, m, val[m][8])
        if len(val[m]) > 10: Best.SetPointError(n, 0., 0., abs(val[m][9]), val[m][10])


    for t in THEORY:
        Theory[t] = TGraphAsymmErrors()
        addXZH = True
        for m in sorted(HVT[t]['W']['XS'].keys()):
            if m < mass[0] or m > mass[-1]: continue
            if m>4500: continue ## for now because I don't have the higher mass xs FIXME
            XsZ, XsZ_Up, XsZ_Down = 0., 0., 0.
            if addXZH:
                XsZ = 1000.*HVT[t]['Z']['XS'][m]*0.12 #temporary BR value set to 0.12 FIXME
                XsZ_Up = XsZ*(1.+math.hypot(HVT[t]['Z']['QCD'][m][0]-1., HVT[t]['Z']['PDF'][m][0]-1.))
                XsZ_Down = XsZ*(1.-math.hypot(1.-HVT[t]['Z']['QCD'][m][0], 1.-HVT[t]['Z']['PDF'][m][0]))

            n = Theory[t].GetN()
            Theory[t].SetPoint(n, m, XsZ)
            Theory[t].SetPointError(n, 0., 0., (XsZ-XsZ_Down), (XsZ_Up-XsZ))

            Theory[t].SetLineColor(theoryLineColor[t])
            Theory[t].SetFillColor(theoryFillColor[t])
            Theory[t].SetFillStyle(theoryFillStyle[t])
            Theory[t].SetLineWidth(2)
            #Theory[t].SetLineStyle(7)


    Exp2s.SetLineWidth(2)
    Exp2s.SetLineStyle(1)
    Obs0s.SetLineWidth(3)
    Obs0s.SetMarkerStyle(0)
    Obs0s.SetLineColor(1)
    Exp0s.SetLineStyle(2)
    Exp0s.SetLineWidth(3)
    Exp1s.SetFillColor(417) #kGreen+1
    Exp1s.SetLineColor(417) #kGreen+1
    Exp2s.SetFillColor(800) #kOrange
    Exp2s.SetLineColor(800) #kOrange
    Exp2s.GetXaxis().SetTitle("m_{"+particleP+"} (GeV)")
    Exp2s.GetXaxis().SetTitleSize(Exp2s.GetXaxis().GetTitleSize()*1.25)
    Exp2s.GetXaxis().SetNoExponent(True)
    Exp2s.GetXaxis().SetMoreLogLabels(True)
    Exp2s.GetYaxis().SetTitle("#sigma("+particleP+") #bf{#it{#Beta}}("+particleP+" #rightarrow "+particle+") (fb)")
    Exp2s.GetYaxis().SetTitleOffset(1.5)
    Exp2s.GetYaxis().SetNoExponent(True)
    Exp2s.GetYaxis().SetMoreLogLabels()

    Sign.SetLineWidth(2)
    Sign.SetLineColor(629)
    Sign.GetXaxis().SetTitle("m_{"+particleP+"} (GeV)")
    Sign.GetXaxis().SetTitleSize(Sign.GetXaxis().GetTitleSize()*1.1)
    Sign.GetYaxis().SetTitle("Significance")

    pVal.SetLineWidth(2)
    pVal.SetLineColor(629)
    pVal.GetXaxis().SetTitle("m_{"+particleP+"} (GeV)")
    pVal.GetXaxis().SetTitleSize(pVal.GetXaxis().GetTitleSize()*1.1)
    pVal.GetYaxis().SetTitle("local p-Value")

    Best.SetLineWidth(2)
    Best.SetLineColor(629)
    Best.SetFillColor(629)
    Best.SetFillStyle(3003)
    Best.GetXaxis().SetTitle("m_{"+particleP+"} (GeV)")
    Best.GetXaxis().SetTitleSize(Best.GetXaxis().GetTitleSize()*1.1)
    Best.GetYaxis().SetTitle("Best Fit (pb)")



    c1 = TCanvas("c1", "Exclusion Limits", 800, 600)
    c1.cd()
    #SetPad(c1.GetPad(0))
    c1.GetPad(0).SetTopMargin(0.06)
    c1.GetPad(0).SetRightMargin(0.05)
    c1.GetPad(0).SetLeftMargin(0.12)
    c1.GetPad(0).SetTicks(1, 1)
    #c1.GetPad(0).SetGridx()
    #c1.GetPad(0).SetGridy()
    c1.GetPad(0).SetLogy()
    Exp2s.Draw("A3")
    Exp1s.Draw("SAME, 3")
    for t in THEORY:
        Theory[t].Draw("SAME, L3")
        Theory[t].Draw("SAME, L3X0Y0")
    Exp0s.Draw("SAME, L")
    if not options.blind: Obs0s.Draw("SAME, L")
    #setHistStyle(Exp2s)
    Exp2s.GetXaxis().SetTitleSize(0.050)
    Exp2s.GetYaxis().SetTitleSize(0.050)
    Exp2s.GetXaxis().SetLabelSize(0.045)
    Exp2s.GetYaxis().SetLabelSize(0.045)
    Exp2s.GetXaxis().SetTitleOffset(0.90)
    Exp2s.GetYaxis().SetTitleOffset(1.25)
    Exp2s.GetYaxis().SetMoreLogLabels(True)
    Exp2s.GetYaxis().SetNoExponent(True)
    Exp2s.GetYaxis().SetRangeUser(0.1, 5.e3)
    #else: Exp2s.GetYaxis().SetRangeUser(0.1, 1.e2)
    #Exp2s.GetXaxis().SetRangeUser(mass[0], min(mass[-1], MAXIMUM[channel] if channel in MAXIMUM else 1.e6))
    Exp2s.GetXaxis().SetRangeUser(SIGNALS[0], SIGNALS[-1])
    #drawAnalysis(channel)
    drawAnalysis("")
    #drawRegion(channel, True)
    drawRegion("", True)
    #drawCMS(LUMI, "Simulation Preliminary") #Preliminary
    drawCMS(LUMI, "Work in Progress", suppressCMS=True)

    # legend
    top = 0.9
    nitems = 4 + len(THEORY)

    leg = TLegend(0.55, top-nitems*0.3/5., 0.98, top)
    #leg = TLegend(0.45, top-nitems*0.3/5., 0.98, top)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0) #1001
    leg.SetFillColor(0)
    leg.SetHeader("95% CL upper limits")
    leg.AddEntry(Obs0s, "Observed", "l")
    leg.AddEntry(Exp0s, "Expected", "l")
    leg.AddEntry(Exp1s, "#pm 1 std. deviation", "f")
    leg.AddEntry(Exp2s, "#pm 2 std. deviation", "f")
    for t in THEORY: leg.AddEntry(Theory[t], theoryLabel[t], "fl")
    leg.Draw()
    latex = TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.045)
    latex.SetTextFont(42)
    #latex.DrawLatex(0.66, leg.GetY1()-0.045, particleP+" #rightarrow "+particle+"h")

    leg2 = TLegend(0.12, 0.225-2*0.25/5., 0.65, 0.225)
    leg2.SetBorderSize(0)
    leg2.SetFillStyle(0) #1001
    leg2.SetFillColor(0)
    c1.GetPad(0).RedrawAxis()

    leg2.Draw()
    if not options.blind: Obs0s.Draw("SAME, L")
    c1.GetPad(0).Update()

    if not gROOT.IsBatch(): raw_input("Press Enter to continue...")

    c1.Print("combine/plotsLimit/ExclusionLimits/MANtag_study/"+YEAR+suffix+".png")
    c1.Print("combine/plotsLimit/ExclusionLimits/MANtag_study/"+YEAR+suffix+".pdf")
    if 'ah' in channel or 'sl' in channel:
        c1.Print("combine/plotsLimit/ExclusionLimits/MANtag_study/"+YEAR+suffix+".C")
        c1.Print("combine/plotsLimit/ExclusionLimits/MANtag_study/"+YEAR+suffix+".root")

    for t in THEORY:
        print "Model", t, ":",
        for m in range(mass[0], mass[-1], 1):
            if not (Theory[t].Eval(m) > Obs0s.Eval(m)) == (Theory[t].Eval(m+1) > Obs0s.Eval(m+1)): print m,
        print ""

    return

def compare_limits():
    method = ''
    channel = "bb"
    particleP = "Z'"
    particle = channel
    multF = ZPTOBB
    THEORY = ['A1', 'B3']
    
    #filename1 = "./combine/limits/MANtag_study/loose/run2_M%d_MC.txt"
    #filename2 = "./combine/limits/medium/run2_M%d_MC.txt"
    #output_suffix = ""
    filename1 = "./combine/limits/MANtag_study/loose/single_category/bb_run2_M%d_MC.txt"
    filename2 = "./combine/limits/medium/single_category/bb_run2_M%d_MC.txt"
    output_suffix = "_bb_loose"
    mass1, val1 = fillValues(filename1)
    mass2, val2 = fillValues(filename2)

    Exp_MANtag = TGraph()
    Exp_DeepJet = TGraph()
    Theory = {}

    for i, m in enumerate(mass1):
        if not m in val1:
            print "Key Error:", m, "not in value map"
            continue
        n1 = Exp_MANtag.GetN()
        Exp_MANtag.SetPoint(n1, m, val1[m][3]*multF)

    for i, m in enumerate(mass2):
        if not m in val2:
            print "Key Error:", m, "not in value map"
            continue
        n2 = Exp_DeepJet.GetN()
        Exp_DeepJet.SetPoint(n2, m, val2[m][3]*multF)


    for t in THEORY:
        Theory[t] = TGraphAsymmErrors()
        addXZH = True
        for m in sorted(HVT[t]['W']['XS'].keys()):
            if m < mass2[0] or m > mass2[-1]: continue
            if m>4500: continue ## for now because I don't have the higher mass xs FIXME
            XsZ, XsZ_Up, XsZ_Down = 0., 0., 0.
            if addXZH:
                XsZ = 1000.*HVT[t]['Z']['XS'][m]*0.12 #temporary BR value set to 0.12 FIXME
                XsZ_Up = XsZ*(1.+math.hypot(HVT[t]['Z']['QCD'][m][0]-1., HVT[t]['Z']['PDF'][m][0]-1.))
                XsZ_Down = XsZ*(1.-math.hypot(1.-HVT[t]['Z']['QCD'][m][0], 1.-HVT[t]['Z']['PDF'][m][0]))

            n = Theory[t].GetN()
            Theory[t].SetPoint(n, m, XsZ)
            Theory[t].SetPointError(n, 0., 0., (XsZ-XsZ_Down), (XsZ_Up-XsZ))

            Theory[t].SetLineColor(theoryLineColor[t])
            Theory[t].SetFillColor(theoryFillColor[t])
            Theory[t].SetFillStyle(theoryFillStyle[t])
            Theory[t].SetLineWidth(2)
            #Theory[t].SetLineStyle(7)


    Exp_MANtag.SetLineStyle(2)
    Exp_MANtag.SetLineWidth(3)
    Exp_MANtag.SetLineColor(418)
    Exp_DeepJet.SetLineStyle(2)
    Exp_DeepJet.SetLineWidth(3)
    Exp_DeepJet.SetLineColor(801)

    c1 = TCanvas("c1", "Exclusion Limits", 800, 600)
    c1.cd()
    #SetPad(c1.GetPad(0))
    c1.GetPad(0).SetTopMargin(0.06)
    c1.GetPad(0).SetRightMargin(0.05)
    c1.GetPad(0).SetLeftMargin(0.12)
    c1.GetPad(0).SetTicks(1, 1)
    #c1.GetPad(0).SetGridx()
    #c1.GetPad(0).SetGridy()
    c1.GetPad(0).SetLogy()
    Exp_MANtag.Draw("AL")
    Exp_DeepJet.Draw("SAME, L")
    for t in THEORY:
        Theory[t].Draw("SAME, L3")
        Theory[t].Draw("SAME, L3X0Y0")
    Exp_MANtag.GetXaxis().SetTitleSize(0.050)
    Exp_MANtag.GetYaxis().SetTitleSize(0.050)
    Exp_MANtag.GetXaxis().SetLabelSize(0.045)
    Exp_MANtag.GetYaxis().SetLabelSize(0.045)
    Exp_MANtag.GetXaxis().SetTitleOffset(0.90)
    Exp_MANtag.GetYaxis().SetTitle("#sigma(Z') #bf{#it{#Beta}}(Z' #rightarrow b#bar{b}) (fb)")
    Exp_MANtag.GetYaxis().SetTitleOffset(1.25)
    Exp_MANtag.GetYaxis().SetMoreLogLabels(True)
    Exp_MANtag.GetYaxis().SetNoExponent(True)
    Exp_MANtag.GetXaxis().SetTitle("m_{Z'} (GeV)")
    Exp_MANtag.GetYaxis().SetRangeUser(0.1, 5.e3)
    Exp_MANtag.GetXaxis().SetRangeUser(SIGNALS[0], SIGNALS[-1])
    drawAnalysis("")
    drawRegion("", True)
    #drawCMS(LUMI, "", suppressCMS=True)
    drawCMS(LUMI, "2 b tag", suppressCMS=True)    


    # legend
    top = 0.9
    nitems = 4 + len(THEORY)

    leg = TLegend(0.55, top-nitems*0.3/5., 0.9, top)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0) #1001
    leg.SetFillColor(0)
    leg.SetHeader("95% CL upper limits")
    leg.AddEntry(Exp_MANtag, "Expected MANtag", "l")
    leg.AddEntry(Exp_DeepJet, "Expected DeepJet", "l")
    for t in THEORY: leg.AddEntry(Theory[t], theoryLabel[t], "fl")
    leg.Draw()
    latex = TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.045)
    latex.SetTextFont(42)
    #latex.DrawLatex(0.66, leg.GetY1()-0.045, particleP+" #rightarrow "+particle+"h")

    leg2 = TLegend(0.12, 0.225-2*0.25/5., 0.65, 0.225)
    leg2.SetBorderSize(0)
    leg2.SetFillStyle(0) #1001
    leg2.SetFillColor(0)
    c1.GetPad(0).RedrawAxis()

    leg2.Draw()
    c1.GetPad(0).Update()

    if not gROOT.IsBatch(): raw_input("Press Enter to continue...")

    c1.Print("combine/plotsLimit/ExclusionLimits/MANtag_study/compare_run2_MC"+output_suffix+".png")
    c1.Print("combine/plotsLimit/ExclusionLimits/MANtag_study/compare_run2_MC"+output_suffix+".pdf")

    return
   
    

if __name__ == "__main__":
    if options.compare:
        compare_limits()
    else:
        limit()
