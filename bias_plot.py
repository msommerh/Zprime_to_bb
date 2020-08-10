#! /usr/bin/env python

import global_paths
from argparse import ArgumentParser
from ROOT import ROOT, gROOT, gStyle, gRandom, TSystemDirectory
from ROOT import TFile, TChain, TTree, TCut, TF1, TH1D, TH1F, TH2F, THStack
from ROOT import TGraph, TGraphErrors, TGraphAsymmErrors, TVirtualFitter, TMultiGraph
from ROOT import TStyle, TCanvas, TPad
from ROOT import TLegend, TLatex, TText, TLine
from utils import *

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-y', '--year',    dest='year', type=str, default='run2c', action='store', choices=['run2', 'run2c'],  help="set year, type run2c for combined submission." )  
    parser.add_argument("-b", "--btagging", action="store", type=str, dest="btagging", default="medium", choices=['tight', 'medium', 'loose', 'semimedium'])

    args = parser.parse_args()

else:
    args = None

PULL0 = {1600: 20.,
         1700: 15.,
         1800: 10.,
         1900: 15.,
         2000: 15.,
         2100: 3.,
         2200: 15.,
         2300: 8.,
         2400: 8.,
         2500: 3.,
         2600: 8.,
         2700: 10.,
         2800: 10.,
         2900: 5.,
         3000: 8.,
         3100: 10.,
         3200: 15.,
         3300: 3.,
         3400: 10.,
         3500: 5.,
         3600: 15.,
         3700: 5.,
         3800: 3.,
         3900: 1.,
         4000: 1.,
         4100: 1.,
         4200: 10.,
         4300: 8.,
         4400: 8.,
         4500: 15.,
         4600: 8.,
         4700: 3.,
         4800: 3.,
         4900: 3.,
         5000: 3.,
         5100: 1.,
         5200: 3.,
         5300: 5.,
         5400: 5.,
         5500: 10.,
         5600: 1.,
         5700: 5.,
         5800: 1.,
         5900: 1.,
         6000: 15.,
         6100: 1.,
         6200: 5.,
         6300: 1.,
         6400: 3.,
         6500: 3.,
         6600: 5.,
         6700: 10.,
         6800: 3.,
         6900: 10.,
         7000: 5.,
         7100: 10.,
         7200: 8.,
         7300: 8.,
         7400: 3.,
         7500: 10.,
         7600: 3.,
         7700: 1.,
         7800: 3.,
         7900: 15.,
         8000: 8.,
        }

def main():
    gStyle.SetOptStat(0)
    BIAS_DIR = global_paths.BIASDIR+args.btagging+"/"
    if args.year == 'run2c':
        BIAS_DIR += "combined_run2/"
        #BIAS_DIR += "combined_run2_signal{}/"
        ## individual plots stored in run2c_masspoints    
    
    ## extract pulls
    pulls = TGraphErrors()
    for m in range(1600,8001,100):
        #try:
            pull0=int(PULL0[m])
            #pull0=10.

            #tfile = TFile.Open(BIAS_DIR+"fitDiagnostics_M{mass}.root".format(mass=m), "READ")
            #tfile = TFile.Open(BIAS_DIR.format(pull0)+"fitDiagnostics_M{mass}.root".format(mass=m), "READ")
            #tree = tfile.Get("tree_fit_sb")
            tree = TChain("tree_fit_sb")
            for seed in ['123456', '234567', '345678', '456789', '567891', '678912', '789123', '891234', '912345', '123459']:
                tree.Add(BIAS_DIR+"fitDiagnostics_M{mass}_{seed}.root".format(mass=m, seed=seed))
 
            ## the method proposed in the documemtation
            #hist = TH1D("hist", "hist", 20, -5, 5)
            #tree.Project("hist", "(r-1)/(0.5*(rHiErr+rLoErr))")
            #fit_func = TF1("gaussfit","gaus" , -5., 5.)
            #hist.Fit(fit_func, "E")
            #pulls.SetPoint(pulls.GetN(), m, fit_func.GetParameter(1)) ## get mean of gaussian fit
            
            ## Alberto's method
            #hist = TH1D("s_pulls", ";%s/#sigma_{r};Number of toys" % ("(r - "+str(pull0)+")"), 25, -5, +5) #
            hist = TH1D("s_pulls", ";%s/#sigma_{r};Number of toys" % ("#Deltar"), 25, -5, +5) #
            for i in range(tree.GetEntries()):
                if hist.GetEntries() >= 1000: continue
                tree.GetEntry(i)
                #print "r = {} (+{}, -{})".format(tree.r, tree.rHiErr, tree.rLoErr)
                ##if tree.rLoErr < 0.: continue
                if abs(tree.r+1.) < 0.001: continue
                if abs(tree.r-1.) < 0.001: continue
                if abs(tree.r-0.) < 0.001: continue
                #if abs(tree.rLoErr)>8.: continue # trying to skip these values FIXME
                if tree.rHiErr==0. or tree.rLoErr==0.: continue
                #print "r = {} (+{}, -{})".format(tree.r, tree.rHiErr, tree.rLoErr)
                #pull = (tree.r-pull0)/(0.5*(abs(tree.rHiErr)+abs(tree.rLoErr))) ## documentation approach
                #pull = (tree.r-pull0)/abs(tree.rHiErr) if tree.r-pull0 < 0. else (tree.r-pull0)/abs(tree.rLoErr)  ## Alberto's sign convention
                pull = (tree.r-pull0)/abs(tree.rHiErr) if tree.r-pull0 > 0. else (tree.r-pull0)/abs(tree.rLoErr) ## my own approach
                #pull = (tree.r-pull0)/abs(tree.rHiErr) if tree.r < 0. else (tree.r-pull0)/abs(tree.rLoErr)  ## Alberto's sign convention but depending directly on the sign of r
                #pull = (tree.r-pull0)/abs(tree.rHiErr) if tree.r > 0. else (tree.r-pull0)/abs(tree.rLoErr) ## my own approach with an rErr dependence on r, not r-1
                hist.Fill(pull)

            ## individual plots for checking the fit quality
            c1 = TCanvas("c1", "Pulls", 600, 600)
            c1.cd()
            #c1.GetPad(0).SetTopMargin(0.06)
            #c1.GetPad(0).SetRightMargin(0.05)
            #c1.GetPad(0).SetBottomMargin(0.15)
            #c1.GetPad(0).SetTicks(1, 1)
            hist.GetXaxis().SetTitleSize(0.045)
            hist.GetYaxis().SetTitleSize(0.045)
            hist.GetYaxis().SetTitleOffset(1.1)
            hist.GetXaxis().SetTitleOffset(1.05)
            hist.GetXaxis().SetLimits(-5, 5.)
            hist.GetYaxis().SetLimits(0, 200.)
            hist.SetMinimum(0.)
            hist.SetMaximum(190.)
            c1.SetTopMargin(0.05)

            ##print "@ m= {}: \t mean = {}".format(m, hist.GetMean())
            #pulls.SetPoint(pulls.GetN(), m, hist.GetMean()) ## get actual mean of histogram
            fit_func = TF1("gaussfit","gaus" , -3., 3.)
            ###fit_func.SetParameter(1, hist.GetMean())
            #fit_func.SetParameter(1, 0.)
            ###fit_func.SetParLimits(1, -0.8, 0.8)
            #fit_func.SetParameter(2, 1.)
            ###fit_func.SetParameter(0, 45.)
            ###fit_func.SetParLimits(0, 30., 100.)
            hist.Fit(fit_func, "E")

            hist.Draw()

            drawCMS(-1, "Simulation Preliminary", year='run2')
            drawMass("m_{Z'} = "+str(m)+" GeV")
            c1.Print("plots/bias/run2c_masspoints/bias_fit_"+str(m)+"_"+args.year+".pdf")
            c1.Print("plots/bias/run2c_masspoints/bias_fit_"+str(m)+"_"+args.year+".png")

            n = pulls.GetN()
            pulls.SetPoint(n, m, fit_func.GetParameter(1)) ## get fitted gaussian mean
            pulls.SetPointError(n, 0., fit_func.GetParError(1)) ## set gaussian width as error

            hist.Delete()
            c1.Delete()
            #tfile.Close()
        #except:
        #    print "something went wrong in m =", m

    ## draw pulls
    c = TCanvas("canvas", "canvas", 800, 600)
    pulls.SetTitle(";m_{Z'} (GeV);mean #Deltar/#sigma_{r}")
    pulls.SetMarkerStyle(2)
    pulls.SetMarkerColor(2)
    pulls.SetLineColor(2)
    pulls.SetLineWidth(2)
    #pulls.GetYaxis().SetNdivisions(1020)
    pulls.SetMinimum(-0.5)
    pulls.SetMaximum(0.5)
    pulls.Draw("APL")
    zeroline = TGraph()
    zeroline.SetPoint(zeroline.GetN(), 1000, 0)
    zeroline.SetPoint(zeroline.GetN(), 8600, 0)
    zeroline.SetMarkerStyle(7)
    zeroline.SetMarkerSize(0)
    zeroline.SetLineStyle(15)
    zeroline.SetLineColor(1)
    zeroline.Draw("PL")
    c.SetGrid()
    pulls.GetXaxis().SetTitleSize(0.045)
    pulls.GetYaxis().SetTitleSize(0.045)
    pulls.GetYaxis().SetTitleOffset(1.1)
    pulls.GetXaxis().SetTitleOffset(1.05)
    pulls.GetXaxis().SetLimits(1350., 8150.)
    c.SetTopMargin(0.05)
    drawCMS(-1, "Simulation Preliminary", year='run2')
    c.Print("plots/bias/bias_study_"+args.year+".png")
    c.Print("plots/bias/bias_study_"+args.year+".pdf")

if __name__ == "__main__":
    main()
