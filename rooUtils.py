#! /usr/bin/env python

import os, sys, getopt, multiprocessing
import copy, math, pickle
from array import array
from ROOT import gROOT, gSystem, gStyle, gRandom
from ROOT import TObject, TMath, TFile, TChain, TTree, TCut, TH1F, TH2F, THStack, TF1, TGraph, TGaxis
from ROOT import TStyle, TCanvas, TPad, TLegend, TLatex, TText
from ROOT import RooFit, RooPlot

#from selections import selection
#from xsections import xsection
#from samples import sample
from utils import *




#def getCut(channel):
#    nElec = channel.count('e')
#    nMuon = channel.count('m')
#    nLept = nElec + nMuon
#    nBtag = channel.count('b')
#    isAH = 'hp' in channel or 'lp' in channel or nBtag > 2
#
#    if isAH: catName = "isVtoQQ"
#    elif nLept == 0: catName = "isZtoNN"
#    elif nLept == 1: catName = "isWtoEN" if nElec > 0 else "isWtoMN"
#    elif nLept == 2: catName = "isZtoEE" if nElec > 0 else "isZtoMM"
#    else: exit(1)
#
#    topVeto = btagCut = VmassCut = tau21Cut = ""
#    if not isAH and nLept < 2: topVeto = "isTveto"
#    if nBtag == 2: btagCut = "(H_csv1>0.460 && H_csv2>0.460)"
#    elif nBtag == 1: btagCut = "((H_csv1>0.460 && H_csv2<=0.460) || (H_csv1<=0.460 && H_csv2>0.460))"
#
#    if isAH:
#        VtauLowCut = 0. if 'hp' in channel else 0.40
#        VtauHighCut = 0.40 if 'hp' in channel else 0.75
#        tau21Cut = "%s>%f && %s<%f" % ("V_tau21", VtauLowCut, "V_tau21", VtauHighCut)
#
#        VmassLowCut = LOWMAX if 'W' in channel else LOWINT
#        VmassHighCut =  LOWINT if 'W' in channel else SIGMIN
#        VmassCut = "%s>%d && %s<%d" % ("V_mass", VmassLowCut, "V_mass", VmassHighCut)
#
#    cut = catName
#    if len(topVeto) > 0: cut += " && " + topVeto
#    if len(btagCut) > 0: cut += " && " + btagCut
#    if len(tau21Cut) > 0: cut += " && " + tau21Cut
#    if len(VmassCut) > 0: cut += " && " + VmassCut
#    return cut

def getColor(name, channel):
    color = {1 : [922, 920], 2 : [418, 410], 3 : [602, 590], 4 : [613, 609], 5 : [800, 400], }
    if type(name) is int: return color[int(name)]
    elif type(name) is str:
        name = name.replace('_'+channel, '').replace(channel, '')
        if 'total' in name: return 1
        elif 'Top' in name: return 798
        elif 'VV' in name: return 602
        #elif name in sample.keys(): return sample[name]['linecolor']
        #elif channel.count('e')+channel.count('m')+channel.count('l') == 2: return sample['DYJetsToLL_HT']['linecolor']
        #elif channel.count('e')+channel.count('m')+channel.count('l') == 1: return sample['WJetsToLNu_HT']['linecolor']
        #elif channel.count('e')+channel.count('m')+channel.count('l') == 0: return sample['DYJetsToNuNu_HT']['linecolor']
        elif 'Bkg' in name: return 590
    return 1

#def getCrossSection(signal, channel, m, m2=0):
#    if m==0:
#        try:
#            m = int(signal.split('_M')[1])
#        except:
#            m, m2 = int(signal.split('_MZ')[1].split('_MA')[0]), int(signal.split('_MA')[1])
#    if signal.startswith('X'):
#        fullName = signal[1] + "primeTo" + signal[1] + "hTo" + signal[1] + "hadhbb_narrow_M-%d" % m # it's the same for hadronic and leptonic decays
#    elif signal.startswith('A'):
#        fullName = "GluGluToAToZhToLLBB_M%d" % m
#    elif signal.startswith('BBA'):
#        fullName = "BBAToZhToLLBB_M%d" % m
#    elif 'monoH'in signal:
#        #if m==0 and m2==0: m, m2 = int(signal.split('_MZ')[1].split('_MA')[0]), int(signal.split('_MA')[1])
#        fullName = "ZprimeToA0hToA0chichihbb_2HDM_MZp-%d_MA0-%d" % (m, m2)
#    else:
#        print "Signal", signal, "not recognized"
##    decayMode = ''
##    if 'hp' in channel or 'lp' in channel: decayMode = 'had'
##    elif 'nn' in channel: decayMode = 'inv'
##    else: decayMode = 'lep'
##    fullName = particle + "primeTo" + particle + "hTo" + particle + decayMode + "hbb_narrow_M-%d" % m
#    if not fullName in xsection:
#        print "ERROR: sample", fullName, "not in xsection list"
#        return -1
##    return xsection[fullName]['xsec'] * xsection[fullName]['br'] * 0.5824 # old
##    return xsection[fullName]['xsec'] * xsection[fullName]['br'] # actual
##    return xsection[fullName]['xsec'] * 0.5824 / 0.6991
##    return xsection[fullName]['xsec'] * 0.5824 # semileptonic
#    return xsection[fullName]['xsec']
#    # When using VHah signal, remove 'br'


def getSignal(cat, sig, mass):
    try:
        file = TFile("workspace/"+sig+cat+".root", "READ")
        w = file.Get("VH_2016")
        signal = w.pdf("%s%s_M%d" % (sig, cat, mass))
        norm = w.var("%s%s_M%d_norm" % (sig, cat, mass))
        xs = w.var("%s%s_M%d_xs" % (sig, cat, mass))
        return [signal, norm.getVal(), xs.getVal()]
    except:
        print "WARNING: failed to get signal pdf"
        return [None, 0., 0.]



def setPadStyle(h, r=1.2, isTop=False):
    h.GetXaxis().SetTitleSize(h.GetXaxis().GetTitleSize()*r*r)
    h.GetYaxis().SetTitleSize(h.GetYaxis().GetTitleSize()*r)
    h.GetXaxis().SetLabelSize(h.GetXaxis().GetLabelSize()*r)
    h.GetYaxis().SetLabelSize(h.GetYaxis().GetLabelSize()*r)
    if isTop: h.GetXaxis().SetLabelOffset(0.04)
#    h.GetXaxis().SetTitleOffset(h.GetXaxis().GetTitleOffset()*r)
#    h.GetYaxis().SetTitleOffset(h.GetYaxis().GetTitleOffset())

def fixData(hist, useGarwood=False, cutGrass=True, maxPoisson=False):
    if hist==None: return
    varBins = ((hist.GetX()[1] - hist.GetX()[0]) != (hist.GetX()[hist.GetN()-1] - hist.GetX()[hist.GetN()-2])) #hist.GetXaxis().IsVariableBinSize()
    avgwidth = (hist.GetX()[hist.GetN()-1]+hist.GetErrorXhigh(hist.GetN()-1) - (hist.GetX()[0]-hist.GetErrorXlow(0))) / hist.GetN()
    alpha = 1 - 0.6827

    for i in list(reversed(range(0, hist.GetN()))):
        #print "bin", i, "x:", hist.GetX()[i], "y:", hist.GetY()[i]
        width = hist.GetErrorXlow(i) + hist.GetErrorXhigh(i)
        # X error bars to 0 - do not move this, otherwise the first bin will disappear, thanks Wouter and Rene!
        if not varBins:
            hist.SetPointEXlow(i, 0)
            hist.SetPointEXhigh(i, 0)
        # Garwood confidence intervals
        if(useGarwood):
            N = hist.GetY()[i]
            r = width / avgwidth
            #print i, width, avgwidth, r
            if varBins: N = hist.GetY()[i] / r
            N = max(N, 0.) # Avoid unphysical bins
            L = ROOT.Math.gamma_quantile(alpha/2, N, 1.) if N>0 else 0.
            U = ROOT.Math.gamma_quantile_c(alpha/2, N+1, 1)
            #print i, hist.GetErrorYlow(i), hist.GetErrorYhigh(i), N-L, U-N
            # maximum between Poisson and Sumw2 error bars
            EL = N-L if not maxPoisson else max(N-L, hist.GetErrorYlow(i))
            EU = U-N if not maxPoisson else max(U-N, hist.GetErrorYhigh(i))
            hist.SetPointEYlow(i, EL)
            hist.SetPointEYhigh(i, EU)
        # Cut grass
        if cutGrass and hist.GetY()[i] > 0.: cutGrass = False
        # Treatment for 0 bins
        if abs(hist.GetY()[i])<=1.e-6:
            if cutGrass: hist.SetPointError(i, hist.GetErrorXlow(i), hist.GetErrorXhigh(i), 1.e-6, 1.e-6, )
            if (hist.GetX()[i]>65 and hist.GetX()[i]<135 and hist.GetY()[i]==0): hist.SetPointError(i, hist.GetErrorXlow(i), hist.GetErrorXhigh(i), 1.e-6, 1.e-6, )
            hist.SetPoint(i, hist.GetX()[i], -1.e-4)
        # X error bars
        #if hist.GetErrorXlow(i)<1.e-4:
        #    binwidth = hist.GetX()[1]-hist.GetX()[0]
        #    hist.SetPointEXlow(i, binwidth/2.)
        #    hist.SetPointEXhigh(i, binwidth/2.)


def likelihoodScan(model, dataset, par = []):

    nll = model.createNLL(dataset, RooFit.Range("X_reasonable_range"), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.SumW2Error(False)) #RooFit.NumCPU(10)

    #gROOT.SetBatch(False)
    nv = (len(par)-1) / 2 + 1
    nh = len(par) / 2 + 1

    c_scan = TCanvas("c_scan", "Likelihood scan", 800*nh, 600*nv)
    c_scan.Divide(nh, nv)
    frame = {}
    for i, p in enumerate(par):
        c_scan.cd(i+1)
        frame[i] = p.frame()
        nll.plotOn(frame[i], RooFit.ShiftToZero(), RooFit.PrintEvalErrors(-1), RooFit.EvalErrorValue(nll.getVal()+10))
        frame[i].GetXaxis().SetRangeUser(p.getMin()*0.75, p.getMax()*1.5)
        frame[i].GetYaxis().SetRangeUser(0, 9)
        lmin = drawLine(p.getMin(), 0, p.getMin(), 9)
        lmax = drawLine(p.getMax(), 0, p.getMax(), 9)
        #c_scan.GetPad(i).SetLogx()
        #c_scan.GetPad(i).SetLogy()
        frame[i].Draw()
    c_scan.Print("Scan.pdf")
    #raw_input("Press Enter to continue...")
    #if options.bash: gROOT.SetBatch(True)
    
def reGenerate(dataset, pdf, variable):
    from ROOT import RooFit, RooArgSet
    # step 1: preliminary fit
    fr = pdf.fitTo(dataset, RooFit.SumW2Error(True), RooFit.Range("X_reasonable_range"), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Save(1), RooFit.PrintLevel(-1))
    # step 2: generate new dataset
    nev = dataset.sumEntries()
    nev = max(nev, 1000)
    dataset2 = pdf.generate(RooArgSet(variable), nev)
    #step 3: refit
    fr2 = pdf.fitTo(dataset2, RooFit.SumW2Error(False), RooFit.Range("X_reasonable_range"), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.Save(1), RooFit.PrintLevel(-1))
    return pdf, fr2

