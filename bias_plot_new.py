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
    parser.add_argument("-f", "--function", action="store", type=int, dest="function_index", default=1, choices=[1,2,3])
    args = parser.parse_args()

else:
    args = None

#SIGNAL_STRENGTH = {}
#SIGNAL_STRENGTH['0'] = {}
#for m in range(1600,8001,100): SIGNAL_STRENGTH['0'][m] = 0.
#SIGNAL_STRENGTH['2sigma'] = PULL2
#SIGNAL_STRENGTH['5sigma'] = PULL5
COLORS = {'0': 2, '2sigma': 8, '5sigma': 4}
LEGEND = {'0': 'r=0', '2sigma': 'r~2#sigma', '5sigma': 'r~5#sigma'}
FUNCTION = {1: "+1 parameter", 2: "modified exponential", 3: "ATLAS function"}
SEEDS = ['123456', '234567', '345678', '456789', '567891', '678912', '789123', '891234', '912345', '123459']
#SEEDS = ['123456']

def main():
    gROOT.SetBatch(True)
    gStyle.SetOptStat(0)
    BIAS_DIR = global_paths.BIASDIR+args.btagging+"/"
    if args.year == 'run2c':
        BIAS_DIR += "combined_run2_r{}_{}/"
        ## individual plots stored in run2c_masspoints    
    
    ## extract pulls
    pulls = {}
    for signal_strength in ['0', '2sigma', '5sigma']: 
    #for signal_strength in ['0']:  ##FIXME FIXME FIXME
        print
        print
        print "--------------------------------------------------"
        print "r = "+signal_strength
        print "--------------------------------------------------"
        pulls[signal_strength] = TGraphErrors()
        for m in range(1600,8001,100):
        #for m in range(6000,8001,100): ##FIXME FIXME FIXME
            print
            print "m = "+str(m)
            print
            #pull0=int(SIGNAL_STRENGTH[signal_strength][m])
            pull0 = 0 if signal_strength == '0' else 1

            tree = TChain("tree_fit_sb")
            for seed in SEEDS:
                tree.Add(BIAS_DIR.format(signal_strength, args.function_index)+"fitDiagnostics_M{mass}_{seed}.root".format(mass=m, seed=seed))
 
            hist = TH1D("s_pulls", ";%s/#sigma_{r};Number of toys" % ("#Deltar"), 25, -5, +5) #
            for i in range(tree.GetEntries()):
                if hist.GetEntries() >= 1000: continue
                tree.GetEntry(i)
                #print "r = {} (+{}, -{})".format(tree.r, tree.rHiErr, tree.rLoErr)
                ##if tree.rLoErr < 0.: continue
                #if abs(tree.r+1.) < 0.001: 
                #    print "filtered out"
                #    continue
                #if abs(tree.r-1.) < 0.001: 
                #    print "filtered out"
                #    continue
                #if abs(tree.r-0.) < 0.001: 
                #    print "filtered out"
                #    continue
                if tree.rHiErr==0. or tree.rLoErr==0.: 
                    #print "filtered out"
                    continue
                if abs(tree.r+abs(tree.rHiErr) - round(tree.r+abs(tree.rHiErr))) < 0.0001: 
                    #print "filtered out"
                    continue
                if abs(tree.r-abs(tree.rLoErr) - round(tree.r-abs(tree.rLoErr))) < 0.0001: 
                    #print "filtered out"
                    continue
                #if signal_strength=='0' and m>6000 and abs(tree.r)>3.: 
                #    print "filtered r = {} (+{}, -{})".format(tree.r, tree.rHiErr, tree.rLoErr)
                #    continue
                #print "r = {} (+{}, -{})".format(tree.r, tree.rHiErr, tree.rLoErr)
                pull = (tree.r-pull0)/abs(tree.rHiErr) if tree.r-pull0 > 0. else (tree.r-pull0)/abs(tree.rLoErr) ## my own approach
                hist.Fill(pull)

            ## individual plots for checking the fit quality
            c1 = TCanvas("c1", "Pulls", 600, 600)
            c1.cd()
            hist.GetXaxis().SetTitleSize(0.045)
            hist.GetYaxis().SetTitleSize(0.045)
            hist.GetYaxis().SetTitleOffset(1.1)
            hist.GetXaxis().SetTitleOffset(1.05)
            hist.GetXaxis().SetLimits(-5, 5.)
            hist.GetYaxis().SetLimits(0, 20.*len(SEEDS))
            hist.SetMinimum(0.)
            hist.SetMaximum(19.*len(SEEDS))
            c1.SetTopMargin(0.05)

            ##print "@ m= {}: \t mean = {}".format(m, hist.GetMean())
            #pulls[signal_strength].SetPoint(pulls[signal_strength].GetN(), m, hist.GetMean()) ## get actual mean of histogram
            fit_func = TF1("gaussfit","gaus" , -3., 3.)
            hist.Fit(fit_func, "E")

            hist.Draw()

            drawCMS(-1, "Simulation Preliminary", year='run2')
            drawMass("m_{Z'} = "+str(m)+" GeV")
            c1.Print("plots/bias/run2c_masspoints/r"+signal_strength+"_f"+str(args.function_index)+"/bias_fit_"+str(m)+"_"+args.year+".pdf") ##FIXME FIXME FIXME
            c1.Print("plots/bias/run2c_masspoints/r"+signal_strength+"_f"+str(args.function_index)+"/bias_fit_"+str(m)+"_"+args.year+".png")

            n = pulls[signal_strength].GetN()
            pulls[signal_strength].SetPoint(n, m, fit_func.GetParameter(1)) ## get fitted gaussian mean
            pulls[signal_strength].SetPointError(n, 0., fit_func.GetParError(1)) ## set gaussian width as error
            
            fit_func.Delete()
            hist.Delete()
            c1.Delete()
        #except:
        #    print "something went wrong in m =", m

    #return ##FIXME FIXME FIXME
    ## draw pulls
    outfile = TFile("plots/bias/bias_study_new_function_"+str(args.function_index)+"_"+args.year+".root", "RECREATE")

    c = TCanvas("canvas", "canvas", 800, 600)
    leg = TLegend(0.65, 0.7, 0.95, 0.9)
    leg.SetBorderSize(0)
    leg.SetFillStyle(0) #1001
    leg.SetFillColor(0)
    for i, signal_strength in enumerate(['0', '2sigma', '5sigma']):
        pulls[signal_strength].SetMarkerStyle(2)
        pulls[signal_strength].SetMarkerColor(COLORS[signal_strength])
        pulls[signal_strength].SetLineColor(COLORS[signal_strength])
        pulls[signal_strength].SetLineWidth(2)
        #pulls[signal_strength].SetMinimum(-0.7)
        #pulls[signal_strength].SetMaximum(0.7)
        pulls[signal_strength].SetMinimum(-1.)
        pulls[signal_strength].SetMaximum(1.)
        #pulls[signal_strength].SetMinimum(-8.)
        #pulls[signal_strength].SetMaximum(8.)
        pulls[signal_strength].Draw("APL" if i==0 else "PL")
        leg.AddEntry(pulls[signal_strength], LEGEND[signal_strength])
    zeroline = TGraph()
    zeroline.SetPoint(zeroline.GetN(), 1000, 0)
    zeroline.SetPoint(zeroline.GetN(), 8600, 0)
    zeroline.SetMarkerStyle(7)
    zeroline.SetMarkerSize(0)
    zeroline.SetLineStyle(15)
    zeroline.SetLineColor(1)
    zeroline.Draw("PL")
    c.SetGrid()
    pulls['0'].SetTitle(";m_{Z'} (GeV);mean #Deltar/#sigma_{r}")
    pulls['0'].GetXaxis().SetTitleSize(0.045)
    pulls['0'].GetYaxis().SetTitleSize(0.045)
    pulls['0'].GetYaxis().SetTitleOffset(1.1)
    pulls['0'].GetXaxis().SetTitleOffset(1.05)
    pulls['0'].GetXaxis().SetLimits(1350., 8150.)
    c.SetTopMargin(0.05)
    leg.Draw()
    drawCMS(-1, "Simulation Preliminary", year='run2')
    drawAnalysis(FUNCTION[args.function_index])
    c.Print("plots/bias/bias_study_new_function_"+str(args.function_index)+"_"+args.year+".png")
    c.Print("plots/bias/bias_study_new_function_"+str(args.function_index)+"_"+args.year+".pdf")
    c.Write()
    outfile.Close()

if __name__ == "__main__":
    main()
