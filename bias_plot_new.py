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

#PULL2 = {1600: 106., 
#         1700: 77.,
#         1800: 51.,
#         1900: 41.,
#         2000: 35.,
#         2100: 32.,
#         2200: 28.,
#         2300: 26.,
#         2400: 23.,
#         2500: 21.,
PULL2 = {1600: 21., ## for putting some signal load into the datacards
         1700: 15.,
         1800: 10.,
         1900: 8.,
         2000: 7.,
         2100: 16.,
         2200: 14.,
         2300: 13.,
         2400: 12.,
         2500: 11., ##
         2600: 20.,
         2700: 18.,
         2800: 17.,
         2900: 15.,
         3000: 14.,
         3100: 13.,
         3200: 13.,
         3300: 12.,
         3400: 11.,
         3500: 11.,
         3600: 10.,
         3700: 9.,
         3800: 9.,
         3900: 8.,
         4000: 8.,
         4100: 7.,
         4200: 7.,
         4300: 6.,
         4400: 6.,
         4500: 6.,
         4600: 5.,
         4700: 5.,
         4800: 4.,
         4900: 4.,
         5000: 4.,
         5100: 4.,
         5200: 3.,
         5300: 3.,
         5400: 3.,
         5500: 3.,
         5600: 2.,
         5700: 2.,
         5800: 2.,
         5900: 2.,
         6000: 2.,
         6100: 2.,
         6200: 1.,
         6300: 1.,
         6400: 1.,
         6500: 1.,
         6600: 1.,
         6700: 1.,
         6800: 1.,
         6900: 1.,
         7000: 1.,
         7100: 1.,
         7200: 1.,
         7300: 1.,
         7400: 1.,
         7500: 1.,
         7600: 1.,
         7700: 1.,
         7800: 1.,
         7900: 1.,
         8000: 1.,
        }

#PULL5 = {1600: 264.,
#         1700: 192.,
#         1800: 128.,
#         1900: 102.,
#         2000: 88.,
#         2100: 79.,
#         2200: 71.,
#         2300: 64.,
#         2400: 58.,
#         2500: 53.,
#         2600: 49.,
#         2700: 45.,
#         2800: 41.,
#         2900: 38.,
#         3000: 36.,
#         3100: 33.,
#         3200: 31.,
#         3300: 30.,
#         3400: 28.,
#         3500: 26.,
#         3600: 25.,
#         3700: 24.,
#         3800: 23.,
#         3900: 21.,
#         4000: 20.,
PULL5 = {1600: 11., ## for putting some signal load into the datacards
         1700: 16.,
         1800: 8.,
         1900: 6.,
         2000: 8.,
         2100: 8.,
         2200: 7.,
         2300: 8.,
         2400: 3.,
         2500: 4.,
         2600: 7.,
         2700: 5.,
         2800: 6.,
         2900: 2.,
         3000: 6.,
         3100: 3.,
         3200: 1.,
         3300: 3.,
         3400: 4.,
         3500: 2.,
         3600: 5.,
         3700: 4.,
         3800: 1.,
         3900: 3.,
         4000: 2., ##
         4100: 19.,
         4200: 17.,
         4300: 16.,
         4400: 15.,
         4500: 14.,
         4600: 13.,
         4700: 12.,
         4800: 11.,
         4900: 10.,
         5000: 9.,
         5100: 9.,
         5200: 8.,
         5300: 7.,
         5400: 7.,
         5500: 6.,
         5600: 6.,
         5700: 5.,
         5800: 5.,
         5900: 5.,
         6000: 4.,
         6100: 4.,
         6200: 4.,
         6300: 3.,
         6400: 3.,
         6500: 3.,
         6600: 3.,
         6700: 2.,
         6800: 2.,
         6900: 2.,
         7000: 2.,
         7100: 2.,
         7200: 2.,
         7300: 2.,
         7400: 2.,
         7500: 1.,
         7600: 1.,
         7700: 1.,
         7800: 1.,
         7900: 1.,
         8000: 1.,
        }

SIGNAL_STRENGTH = {}
SIGNAL_STRENGTH['0'] = {}
for m in range(1600,8001,100): SIGNAL_STRENGTH['0'][m] = 0.
SIGNAL_STRENGTH['2sigma'] = PULL2
SIGNAL_STRENGTH['5sigma'] = PULL5
COLORS = {'0': 2, '2sigma': 8, '5sigma': 4}
LEGEND = {'0': 'r=0', '2sigma': 'r~2#sigma', '5sigma': 'r~5#sigma'}

def main():
    gStyle.SetOptStat(0)
    BIAS_DIR = global_paths.BIASDIR+args.btagging+"/"
    if args.year == 'run2c':
        BIAS_DIR += "combined_run2_r{}{}/"
        ## individual plots stored in run2c_masspoints    
    
    ## extract pulls
    pulls = {}
    for signal_strength in ['0', '2sigma', '5sigma']:
        print
        print
        print "--------------------------------------------------"
        print "r = "+signal_strength
        print "--------------------------------------------------"
        pulls[signal_strength] = TGraphErrors()
        for m in range(1600,8001,100):
            if (signal_strength=='2sigma' and m<2600) or (signal_strength=='5sigma' and m<4100): ##FIXME FIXME
                datacard_correction = True
            else:
                datacard_correction = False
            print
            print "m = "+str(m)
            if datacard_correction: print "correcting signal strength in the datacard"
            print
            pull0=int(SIGNAL_STRENGTH[signal_strength][m])

            tree = TChain("tree_fit_sb")
            for seed in ['123456', '234567', '345678', '456789', '567891', '678912', '789123', '891234', '912345', '123459']:
                tree.Add(BIAS_DIR.format(signal_strength, "_lowm" if datacard_correction else "")+"fitDiagnostics_M{mass}_{seed}.root".format(mass=m, seed=seed)) ##FIXME FIXME
 
            hist = TH1D("s_pulls", ";%s/#sigma_{r};Number of toys" % ("#Deltar"), 25, -5, +5) #
            for i in range(tree.GetEntries()):
                if hist.GetEntries() >= 1000: continue
                tree.GetEntry(i)
                #print "r = {} (+{}, -{})".format(tree.r, tree.rHiErr, tree.rLoErr)
                ##if tree.rLoErr < 0.: continue
                if abs(tree.r+1.) < 0.001: continue
                if abs(tree.r-1.) < 0.001: continue
                if abs(tree.r-0.) < 0.001: continue
                if tree.rHiErr==0. or tree.rLoErr==0.: continue
                if abs(tree.r+abs(tree.rHiErr) - round(tree.r+abs(tree.rHiErr))) < 0.0001: continue
                if abs(tree.r-abs(tree.rLoErr) - round(tree.r-abs(tree.rLoErr))) < 0.0001: continue
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
            hist.GetXaxis().SetLimits(-6, 6.)
            hist.GetYaxis().SetLimits(0, 200.)
            hist.SetMinimum(0.)
            hist.SetMaximum(190.)
            c1.SetTopMargin(0.05)

            ##print "@ m= {}: \t mean = {}".format(m, hist.GetMean())
            #pulls[signal_strength].SetPoint(pulls[signal_strength].GetN(), m, hist.GetMean()) ## get actual mean of histogram
            fit_func = TF1("gaussfit","gaus" , -3., 3.)
            hist.Fit(fit_func, "E")

            hist.Draw()

            drawCMS(-1, "Simulation Preliminary", year='run2')
            drawMass("m_{Z'} = "+str(m)+" GeV")
            c1.Print("plots/bias/run2c_masspoints/r"+signal_strength+"/bias_fit_"+str(m)+"_"+args.year+".pdf")
            c1.Print("plots/bias/run2c_masspoints/r"+signal_strength+"/bias_fit_"+str(m)+"_"+args.year+".png")

            n = pulls[signal_strength].GetN()
            pulls[signal_strength].SetPoint(n, m, fit_func.GetParameter(1)) ## get fitted gaussian mean
            pulls[signal_strength].SetPointError(n, 0., fit_func.GetParError(1)) ## set gaussian width as error
            
            fit_func.Delete()
            hist.Delete()
            c1.Delete()
        #except:
        #    print "something went wrong in m =", m

    ## draw pulls
    outfile = TFile("plots/bias/bias_study_new_"+args.year+".root", "RECREATE")

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
        pulls[signal_strength].SetMinimum(-0.7)
        pulls[signal_strength].SetMaximum(0.7)
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
    c.Print("plots/bias/bias_study_new_"+args.year+".png")
    c.Print("plots/bias/bias_study_new_"+args.year+".pdf")
    c.Write()
    outfile.Close()

if __name__ == "__main__":
    main()
