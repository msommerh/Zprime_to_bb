#! /usr/bin/env python

import numpy as np
from ROOT import TFile, TTree, TH1D, TCanvas, TLegend
from root_numpy import root2array, fill_hist
import json

import optparse
usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage)
parser.add_option("-p", "--produce", action="store_true", default=False, dest="produce")
parser.add_option("-c", "--compare", action="store_true", default=False, dest="compare")
(options, args) = parser.parse_args()

def extract_jj_mass(filename):
    f = TFile.Open(filename)
    hist = f.Get("jj_mass")
    hist.SetDirectory(0)
    hist.SetStats(False)
    f.Close()
    return hist

if options.produce:

    ## initialize histograms
    
    jpt1 = TH1D("jet_pT_1", "jet_pT_1", 200, 0, 4500)
    jpt2 = TH1D("jet_pT_2", "jet_pT_2", 200, 0, 4500)
    jpt = TH1D("jet_pT", "jet_pT", 200, 0, 4500)
    jmass_1 = TH1D("jmass_1", "jmass_1", 200, 0, 700)
    jmass_2 = TH1D("jmass_2", "jmass_2", 200, 0, 700)
    jmass = TH1D("jmass", "jmass", 200, 0, 700)
    jj_mass = TH1D("jj_mass", "jj_mass", 200, 0, 10000)
    
    
    ## open flatTuples and fill histograms
    
    sample_title = "data_2017"
    
    isMC = False
    if 'MC' in sample_title:
        isMC = True
    data_set_file = "samples_{}.json".format(sample_title)
    sample_dir = "/eos/user/m/msommerh/Zprime_to_bb_analysis/"
    
    file_list = []
    with open(data_set_file, 'r') as json_file:
        data_sets = json.load(json_file)
    for title in data_sets.keys():
    	file_list.append(sample_dir+title+"/"+title+"_flatTuple_*.root")
    print "file_list =", file_list
    
    for sample in file_list:
    
    	##only for test purposes, these samples are not fully computed yet:
    	#if sample == u'/eos/user/m/msommerh/Zprime_to_bb_analysis/MC_QCD_2018_HT100to200/MC_QCD_2018_HT100to200_flatTuple_*.root': continue
    	#if sample == u'/eos/user/m/msommerh/Zprime_to_bb_analysis/MC_QCD_2018_HT500to700/MC_QCD_2018_HT500to700_flatTuple_*.root': continue
    
    	print "opening files:", sample
    
    	variables = root2array(sample, treename='tree', branches=['jpt_1', 'jpt_2', 'jmass_1', 'jmass_2', 'jj_mass', 'eventweightlumi', 'genWeight', 'PSWeight', 'LHEWeight_originalXWGTUP', 'LHEReweightingWeight', 'LHEScaleWeight', 'HLT_AK8PFJet550', 'HLT_PFJet550', 'HLT_CaloJet550_NoJetID', 'HLT_PFHT1050'])
    
    	if isMC:
    	    #weights = variables['eventweightlumi']
    	    weights = np.multiply(variables['eventweightlumi'],variables['LHEWeight_originalXWGTUP']) # not sure yet if I need to multply with the others too
    	else:
    	    weights = np.ones(variables.shape[0])
    	
    	trigger1 = np.multiply(variables['HLT_AK8PFJet550'], variables['HLT_PFJet550'])
    	trigger2 = np.multiply(variables['HLT_CaloJet550_NoJetID'], variables['HLT_PFHT1050'])
    	trigger = np.multiply(trigger1, trigger2)
    
    	weights = np.multiply(weights, trigger)
    
    	fill_hist(jpt1, variables['jpt_1'], weights=weights)
    	fill_hist(jpt2, variables['jpt_2'], weights=weights)
    	fill_hist(jpt, np.concatenate((variables['jpt_1'], variables['jpt_2'])), weights=np.concatenate((weights,weights)))
    	fill_hist(jmass_1, variables['jmass_1'], weights=weights)
    	fill_hist(jmass_2, variables['jmass_2'], weights=weights)
    	fill_hist(jmass, np.concatenate((variables['jmass_1'], variables['jmass_2'])), weights=np.concatenate((weights, weights)))
    	fill_hist(jj_mass, variables['jj_mass'], weights=weights)
    
    ## draw histograms
    
    out_file_name = "test_fitting_trig_{}.root".format(sample_title)
    out_file = TFile(out_file_name, "RECREATE")
    jpt1   .Write()	 	
    jpt2   .Write() 	
    jpt    .Write() 	
    jmass_1.Write() 	
    jmass_2.Write() 	
    jmass  .Write() 	
    jj_mass.Write()  	
    out_file.Close()

	
if options.compare:

    hist1 = extract_jj_mass("test_fitting_trig_data_2017.root")
    hist2 = extract_jj_mass("test_fitting_trig_noLHE_MC_QCD_2017.root")
    hist3 = extract_jj_mass("test_fitting_trig_MC_QCD_2017.root") 
    hist1.SetLineColor(1) 
    hist2.SetLineColor(2)
    hist3.SetLineColor(4)
  
    outfile = TFile("compare_MC_to_data_2017.root", "RECREATE")
    c = TCanvas("canvas", "canvas", 600, 600)
    hist2.Draw()
    hist1.Draw("SAME")
    hist3.Draw("SAME")
    l = TLegend(0.7,0.8,0.9,0.9)
    l.AddEntry(hist1, "data")
    l.AddEntry(hist2, "MC_noLHE")
    l.AddEntry(hist3, "MC")
    l.Draw()

    outfile.cd() 
    c.Write()
    c.SaveAs("compare_MC_to_data_2017.png")
    outfile.Close() 
