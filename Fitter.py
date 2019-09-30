#! /usr/bin/env python

import numpy as np
from ROOT import TFile, TTree, TH1D, TCanvas
from root_numpy import root2array, fill_hist
import json

## initialize histograms

jpt1 = TH1D("jet_pT_1", "jet_pT_1", 100, 0, 200)
jpt2 = TH1D("jet_pT_2", "jet_pT_2", 100, 0, 200)
jpt = TH1D("jet_pT", "jet_pT", 100, 0, 200)
jmass_1 = TH1D("jmass_1", "jmass_1", 100, 0, 35)
jmass_2 = TH1D("jmass_2", "jmass_2", 100, 0, 35)
jmass = TH1D("jmass", "jmass", 100, 0, 35)
jj_mass = TH1D("jj_mass", "jj_mass", 100, 0, 900)


## open flatTuples and fill histograms

sample_title = "MC_QCD_2018"

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

	variables = root2array(sample, treename='tree', branches=['jpt_1', 'jpt_2', 'jmass_1', 'jmass_2', 'jj_mass', 'eventweightlumi', 'genWeight', 'PSWeight', 'LHEWeight_originalXWGTUP', 'LHEReweightingWeight', 'LHEScaleWeight'])

	weights = variables['eventweightlumi'] # not sure yet if I need to multply with the others too
	#weights = np.ones(variables.shape[0])

	fill_hist(jpt1, variables['jpt_1'], weights=weights)
	fill_hist(jpt2, variables['jpt_2'], weights=weights)
	fill_hist(jpt, np.concatenate((variables['jpt_1'], variables['jpt_2'])), weights=np.concatenate((weights,weights)))
	fill_hist(jmass_1, variables['jmass_1'], weights=weights)
	fill_hist(jmass_2, variables['jmass_2'], weights=weights)
	fill_hist(jmass, np.concatenate((variables['jmass_1'], variables['jmass_2'])), weights=np.concatenate((weights, weights)))
	fill_hist(jj_mass, variables['jj_mass'], weights=weights)

## draw histograms

out_file_name = "test_fitting_{}.root".format(sample_title)
out_file = TFile(out_file_name, "RECREATE")
jpt1   .Write()	 	
jpt2   .Write() 	
jpt    .Write() 	
jmass_1.Write() 	
jmass_2.Write() 	
jmass  .Write() 	
jj_mass.Write()  	
out_file.Close()
	

## fit function to histogram
