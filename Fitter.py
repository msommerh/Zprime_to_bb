#! /usr/bin/env python

import numpy as np
from ROOT import TFile, TTree, TH1D, TCanvas, TLegend
from root_numpy import root2array, fill_hist
import json
import multiprocessing
import optparse
usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage)
parser.add_option("-p", "--produce", action="store_true", default=False, dest="produce")
parser.add_option("-c", "--compare", action="store_true", default=False, dest="compare")
parser.add_option("-M", "--isMC", action="store_true", default=False, dest="isMC")
parser.add_option('-y', '--year', action='store', type='string', dest='year',default='2017')
(options, args) = parser.parse_args()

def extract_jj_mass(filename):
    f = TFile.Open(filename)
    hist = f.Get("jj_mass")
    hist.SetDirectory(0)
    hist.SetStats(False)
    f.Close()
    return hist



def produce(sample_title, LHE_weight=False, PU_weight=False):

    ## initialize histograms
    
    jpt1 = TH1D("jet_pT_1", "jet_pT_1", 200, 0, 4500)
    jpt2 = TH1D("jet_pT_2", "jet_pT_2", 200, 0, 4500)
    jpt = TH1D("jet_pT", "jet_pT", 200, 0, 4500)
    jmass_1 = TH1D("jmass_1", "jmass_1", 200, 0, 700)
    jmass_2 = TH1D("jmass_2", "jmass_2", 200, 0, 700)
    jmass = TH1D("jmass", "jmass", 200, 0, 700)
    jj_mass = TH1D("jj_mass", "jj_mass", 200, 0, 10000)
    
    
    ## open flatTuples and fill histograms
     
    isMC = False
    if 'MC' in sample_title:
        isMC = True
    data_set_file = "samples_{}.json".format(sample_title)
    if isMC:
        sample_dir = "/eos/user/m/msommerh/Zprime_to_bb_analysis/weighted/"
    else:
        sample_dir = "/eos/user/m/msommerh/Zprime_to_bb_analysis/"
 
    file_list = []
    with open(data_set_file, 'r') as json_file:
        data_sets = json.load(json_file)
    for title in data_sets.keys():
    	file_list.append(sample_dir+title+"/"+title+"_flatTuple_*.root")
    print "file_list =", file_list
    
    for sample in file_list:
    
    	print "opening files:", sample

	weight_string = ''
    
    	if isMC: 
    	    variables = root2array(sample, treename='tree', branches=['jpt_1', 'jpt_2', 'jmass_1', 'jmass_2', 'jj_mass', 'eventWeightLumi', 'GenWeight', 'PSWeight', 'PUWeight', 'LHEWeight_originalXWGTUP', 'LHEReweightingWeight', 'LHEScaleWeight', 'HLT_AK8PFJet550', 'HLT_PFJet550', 'HLT_CaloJet550_NoJetID', 'HLT_PFHT1050'])
    	    weights = variables['eventWeightLumi']
	    if LHE_weight: 
                weights = np.multiply(weights, variables['LHEWeight_originalXWGTUP'])
                weight_string += 'LHEWeighted_'
	    if PU_weight: 
                weights = np.multiply(weights,variables['PUWeight'])
                weight_string += 'PUWeighted_'

    	else:
            variables = root2array(sample, treename='tree', branches=['jpt_1', 'jpt_2', 'jmass_1', 'jmass_2', 'jj_mass', 'HLT_AK8PFJet550', 'HLT_PFJet550', 'HLT_CaloJet550_NoJetID', 'HLT_PFHT1050'])
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

    out_file_name = "merged_files/merged_trig_{}.root".format(weight_string+sample_title)
    out_file = TFile(out_file_name, "RECREATE")
    jpt1   .Write()	 	
    jpt2   .Write() 	
    jpt    .Write() 	
    jmass_1.Write() 	
    jmass_2.Write() 	
    jmass  .Write() 	
    jj_mass.Write()  	
    out_file.Close()

	
def compare(year):

    hist1 = extract_jj_mass("merged_files/merged_trig_data_{}.root".format(year))
    hist2 = extract_jj_mass("merged_files/merged_trig_MC_QCD_{}.root".format(year))
    hist3 = extract_jj_mass("merged_files/merged_trig_LHEWeighted_MC_QCD_{}.root".format(year)) 
    hist4 = extract_jj_mass("merged_files/merged_trig_PUWeighted_MC_QCD_{}.root".format(year)) 
    hist5 = extract_jj_mass("merged_files/merged_trig_LHEWeighted_PUWeighted_MC_QCD_{}.root".format(year)) 
    hist1.SetLineColor(1) 
    hist2.SetLineColor(2)
    hist3.SetLineColor(4)
    hist4.SetLineColor(6)
    hist5.SetLineColor(7)
 
    outfile = TFile("compare_MC_to_data_{}_new_weights.root".format(year), "RECREATE")
    c = TCanvas("canvas", "canvas", 600, 600)
    hist2.Draw()
    hist1.Draw("SAME")
    hist3.Draw("SAME")
    hist4.Draw("SAME")
    hist5.Draw("SAME")
    l = TLegend(0.7,0.8,0.9,0.9)
    l.AddEntry(hist1, "data")
    l.AddEntry(hist2, "MC") 
    l.AddEntry(hist3, "MC_LHE")
    l.AddEntry(hist4, "MC_PU")
    l.AddEntry(hist5, "MC_LHE_PU")
    l.Draw()

    outfile.cd() 
    c.Write()
    c.SaveAs("compare_MC_to_data_{}_new_weights.png".format(year))
    outfile.Close()

if __name__ == '__main__':

    if options.produce:
   
	if options.isMC: 
            sample_title = "MC_QCD_"+options.year
        else:
            sample_title = "data_"+options.year   
    
        jobs = []
        module = lambda : produce(sample_title, LHE_weight=False, PU_weight=False)
	p = multiprocessing.Process(target=module)
        jobs.append(p)
        p.start()
	module = lambda : produce(sample_title, LHE_weight=True, PU_weight=False)
	p = multiprocessing.Process(target=module)
        jobs.append(p)
        p.start()
	module = lambda : produce(sample_title, LHE_weight=False, PU_weight=True)
	p = multiprocessing.Process(target=module)
        jobs.append(p)
        p.start()
	module = lambda : produce(sample_title, LHE_weight=True, PU_weight=True)
	p = multiprocessing.Process(target=module)
        jobs.append(p)
        p.start()

    if options.compare:
 
       compare(options.year) 
