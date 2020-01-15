#! /usr/bin/env python

from ROOT import TH1F, TFile, TCanvas, TLegend
from root_numpy import root2array, fill_hist
from array import array
from argparse import ArgumentParser
from samples import sample
from aliases import alias, dijet_bins
import global_paths
import sys

#NTUPLEDIR   = global_paths.SKIMMEDDIR
NTUPLEDIR   = "/afs/cern.ch/work/m/msommerh/public/Zprime_to_bb_Analysis/Skim_test/"
#selection='jj_deltaEta_widejet<1.1'
#selection=alias['preselection']
selection=None

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-y', '--year',    dest='year', type=str, default='2018', action='store', help="set year." )
    parser.add_argument('-l', '--log',    dest='log', default=False, action='store_true', help="set logy" )
    args = parser.parse_args()


    binning = array('d', dijet_bins)

    f1 = TFile("Tylers_mjj_spectra/JetHT_run{}_red_cert_scan_all.root".format(args.year), "READ")
    tot_hist0 = f1.Get("Mjj")
    tot_hist1 = tot_hist0.Rebin(len(dijet_bins)-1, "mini", binning)

    tot_hist2 = TH1F("nano", ";M_{jj} (GeV);Events", len(dijet_bins)-1, binning)
 
    data_list = [x for x in sample['data_obs']['files'] if args.year in x]
    for ss in data_list:
        arr = root2array(NTUPLEDIR + ss + ".root", 'tree', branches='jj_mass_widejet', selection=selection)
        print "file:", NTUPLEDIR + ss + ".root"
        print "n entries:", len(arr)
        print
        fill_hist(tot_hist2, arr)
        arr=None        

    c1 = TCanvas('c1', 'c1', 600, 600)
    if args.log: c1.SetLogy() 

    tot_hist1.SetLineColor(2)
    tot_hist2.SetLineColor(4)

    leg = TLegend(0.65, 0.7, 0.9, 0.9)
    leg.AddEntry(tot_hist1, "MiniAOD")
    leg.AddEntry(tot_hist2, "NanoAOD")  
    
    tot_hist2.Draw()
    tot_hist1.Draw("SAME") 
    leg.Draw()

    c1.Print("plots/m_jj_comparison/{}.png".format(args.year))  
 
