#! /usr/bin/env python

import global_paths
from argparse import ArgumentParser
from ROOT import ROOT, gROOT, gStyle, gRandom, TSystemDirectory
from ROOT import TFile, TChain, TTree, TCut, TF1, TH1D, TH1F, TH2F, THStack
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
        BIAS_DIR += "combined_run2_signal{}/"
        ## individual plots stored in run2c_masspoints    
    
    ## extract pulls
    pulls = TGraph()
    for m in range(1600, 8001, 100):
        print
        print
        print "m = "+str(m)
        for pull0 in [1,3,5,8,10,15,20,50]:
                print
                print "r = "+str(pull0)
                print "--------------------"
                #try:
                tfile = TFile.Open(BIAS_DIR.format(pull0)+"fitDiagnostics_M{mass}.root".format(mass=m), "READ")
                tree = tfile.Get("tree_fit_sb")
                
                ## the method proposed in the documemtation
                #hist = TH1D("hist", "hist", 20, -5, 5)
                #tree.Project("hist", "(r-1)/(0.5*(rHiErr+rLoErr))")
                #fit_func = TF1("gaussfit","gaus" , -5., 5.)
                #hist.Fit(fit_func, "E")
                #pulls.SetPoint(pulls.GetN(), m, fit_func.GetParameter(1)) ## get mean of gaussian fit
                
                ## Alberto's method
                #pull0=PULL0[m]
                #pull0=10.
                hist = TH1D("s_pulls", ";%s/#sigma_{r};Number of toys" % ("(r - "+str(pull0)+")"), 25, -5, +5) #
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
                    print "r = {} (+{}, -{})".format(tree.r, tree.rHiErr, tree.rLoErr)
                    #pull = (tree.r-pull0)/(0.5*(abs(tree.rHiErr)+abs(tree.rLoErr))) ## documentation approach
                    #pull = (tree.r-pull0)/abs(tree.rHiErr) if tree.r-pull0 < 0. else (tree.r-pull0)/abs(tree.rLoErr)  ## Alberto's sign convention
                    pull = (tree.r-pull0)/abs(tree.rHiErr) if tree.r-pull0 > 0. else (tree.r-pull0)/abs(tree.rLoErr) ## my own approach
                    #pull = (tree.r-pull0)/abs(tree.rHiErr) if tree.r < 0. else (tree.r-pull0)/abs(tree.rLoErr)  ## Alberto's sign convention but depending directly on the sign of r
                    #pull = (tree.r-pull0)/abs(tree.rHiErr) if tree.r > 0. else (tree.r-pull0)/abs(tree.rLoErr) ## my own approach with an rErr dependence on r, not r-1
                    hist.Fill(pull)

                ### individual pltos for checking the fit quality
                c1 = TCanvas("c1", "Pulls", 600, 600)
                c1.cd()
                c1.GetPad(0).SetTopMargin(0.06)
                c1.GetPad(0).SetRightMargin(0.05)
                c1.GetPad(0).SetBottomMargin(0.15)
                c1.GetPad(0).SetTicks(1, 1)

                #print "@ m= {}: \t mean = {}".format(m, hist.GetMean())
                #pulls.SetPoint(pulls.GetN(), m, hist.GetMean()) ## get actual mean of histogram
                fit_func = TF1("gaussfit","gaus" , -3., 3.)
                ##fit_func.SetParameter(1, hist.GetMean())
                fit_func.SetParameter(1, 0.)
                ##fit_func.SetParLimits(1, -0.8, 0.8)
                fit_func.SetParameter(2, 1.)
                ##fit_func.SetParameter(0, 45.)
                ##fit_func.SetParLimits(0, 30., 100.)
                hist.Fit(fit_func, "E")

                hist.Draw()
                c1.Print("plots/bias/r_comparison/bias_fit_".format(m)+str(m)+"_r"+str(pull0)+".png")

                pulls.SetPoint(pulls.GetN(), m, fit_func.GetParameter(1)) ## get fitted gaussian mean
                hist.Delete()
                c1.Delete()
                tfile.Close()
        #except:
        #    print "something went wrong in m =", m

    ### draw pulls
    #c = TCanvas("canvas", "canvas", 800, 600)
    #pulls.SetTitle(";m_{X} (GeV);#Deltar/#sigma_{r}")
    #pulls.SetMarkerStyle(2)
    #pulls.SetMarkerColor(2)
    #pulls.SetLineColor(2)
    #pulls.SetLineWidth(2)
    #pulls.GetYaxis().SetNdivisions(1020)
    #pulls.Draw("APL")
    #zeroline = TGraph()
    #zeroline.SetPoint(zeroline.GetN(), 1000, 0)
    #zeroline.SetPoint(zeroline.GetN(), 8600, 0)
    #zeroline.SetMarkerStyle(7)
    #zeroline.SetMarkerSize(0)
    #zeroline.SetLineStyle(15)
    #zeroline.SetLineColor(1)
    #zeroline.Draw("PL")
    #c.SetGrid()
    #c.Print("plots/bias/bias_study_"+args.year+".png")
    #c.Print("plots/bias/bias_study_"+args.year+".pdf")

if __name__ == "__main__":
    main()
