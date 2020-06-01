#! /usr/bin/env python

import global_paths
from argparse import ArgumentParser
from ROOT import ROOT, gROOT, gStyle, gRandom, TSystemDirectory
from ROOT import TFile, TChain, TTree, TCut, TF1, TH1D, TH2F, THStack
from ROOT import TGraph, TGraphErrors, TGraphAsymmErrors, TVirtualFitter, TMultiGraph
from ROOT import TStyle, TCanvas, TPad
from ROOT import TLegend, TLatex, TText, TLine

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-y', '--year',    dest='year', type=str, default='run2c', action='store', choices=['run2', 'run2c'],  help="set year, type run2c for combined submission." )  
    parser.add_argument("-b", "--btagging", action="store", type=str, dest="btagging", default="medium", choices=['tight', 'medium', 'loose', 'semimedium'])

    args = parser.parse_args()

else:
    args = None


def main():
    BIAS_DIR = global_paths.BIASDIR+args.btagging+"/"
    if args.year == 'run2c':
        BIAS_DIR += "combined_run2/"

    ## extract pulls
    pulls = TGraph()
    for m in range(1600,8001,100):
        try:
            tfile = TFile.Open(BIAS_DIR+"fitDiagnostics_M{mass}.root".format(mass=m), "READ")
            tree = tfile.Get("tree_fit_sb")
            hist = TH1D("hist", "hist", 20, -5, -5)
            tree.Project("hist", "(r-1)/(0.5*(rHiErr+rLoErr))")
            #fit_func = TF1("gaussfit","gaus" , -5., 5.)
            #hist.Fit(fit_func, "E")
            #pulls.SetPoint(pulls.GetN(), m, fit_func.GetParameter(0)) ## get mean of gaussian fit
            pulls.SetPoint(pulls.GetN(), m, hist.GetMean()) ## get actual mean of histogram
            tfile.Close()
        except:
            print "something went wrong in m =", m

    ## draw pulls
    c = TCanvas("canvas", "canvas", 800, 600)
    pulls.SetTitle(";m_{X} (GeV);#Deltar/#sigma_{r}")
    pulls.SetMarkerStyle(2)
    pulls.SetMarkerColor(2)
    pulls.SetLineColor(2)
    pulls.SetLineWidth(2)
    pulls.GetYaxis().SetNdivisions(1020)
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
    c.Print("plots/bias/bias_study_"+args.year+".png")
    c.Print("plots/bias/bias_study_"+args.year+".pdf")

if __name__ == "__main__":
    main()
