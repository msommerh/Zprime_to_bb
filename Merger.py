#! /usr/bin/env python

import numpy as np
import os
from ROOT import TFile, TTree, TH1D, TCanvas, TLegend, gROOT
from root_numpy import root2array, fill_hist
import json
import multiprocessing
import optparse
usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage)
parser.add_option("-p", "--produce", action="store_true", default=False, dest="produce")
parser.add_option("-S", "--signal", action="store_true", default=False, dest="signal")
parser.add_option("-c", "--compare", action="store_true", default=False, dest="compare")
parser.add_option("-C", "--SigvsBkg", action="store_true", default=False, dest="SigvsBkg")
parser.add_option('-y', '--year', action='store', type='string', dest='year',default='2017')
parser.add_option('-s', '--single_process', action='store', type='int', dest='single_process',default=0)
(options, args) = parser.parse_args()

gROOT.SetBatch(True)
masspoints = [600, 800, 1000, 1200, 1400, 1600, 1800, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 7000, 8000]

def extract_jj_mass(filename):
    f = TFile.Open(filename)
    hist = f.Get("jj_mass")
    hist.SetDirectory(0)
    hist.SetStats(False)
    f.Close()
    return hist

def extract_btag(filename): 
    f = TFile.Open(filename)
    hist = f.Get("jdeepFlavour")
    hist.SetDirectory(0)
    hist.SetStats(False)
    f.Close()
    return hist

def compare_jj_masses(output_file, title1, title2, directory1, directory2, trigger1='2017', trigger2='2017'):
    branches=['jj_mass']
    if trigger1=='2016':
        branches1 = branches+['HLT_AK8PFJet500', 'HLT_PFJet500', 'HLT_CaloJet500_NoJetID', 'HLT_PFHT900']
    else:
        branches1 = branches+['HLT_AK8PFJet550', 'HLT_PFJet550', 'HLT_CaloJet550_NoJetID', 'HLT_PFHT1050']
    if trigger2=='2016':
        branches2 = branches+['HLT_AK8PFJet500', 'HLT_PFJet500', 'HLT_CaloJet500_NoJetID', 'HLT_PFHT900']
    else:
        branches2 = branches+['HLT_AK8PFJet550', 'HLT_PFJet550', 'HLT_CaloJet550_NoJetID', 'HLT_PFHT1050']

    jj_mass1 = TH1D("jj_mass1", "jj_mass1", 200, 0, 10000) 
    jj_mass2 = TH1D("jj_mass2", "jj_mass2", 200, 0, 10000) 
    var1 = root2array(directory1+"/*flatTuple_*.root", treename='tree', branches=branches1)
    var2 = root2array(directory2+"/*flatTuple_*.root", treename='tree', branches=branches2)
    
    if trigger1=='2016':
        trig11 = np.multiply(var1['HLT_AK8PFJet500'], var1['HLT_PFJet500'])
        trig12 = np.multiply(var1['HLT_CaloJet500_NoJetID'], var1['HLT_PFHT900'])
    else:
        trig11 = np.multiply(var1['HLT_AK8PFJet550'], var1['HLT_PFJet550'])
        trig12 = np.multiply(var1['HLT_CaloJet550_NoJetID'], var1['HLT_PFHT1050'])
    if trigger2=='2016':
        trig21 = np.multiply(var2['HLT_AK8PFJet500'], var2['HLT_PFJet500'])
        trig22 = np.multiply(var2['HLT_CaloJet500_NoJetID'], var2['HLT_PFHT900'])
    else:
        trig21 = np.multiply(var2['HLT_AK8PFJet550'], var2['HLT_PFJet550'])
        trig22 = np.multiply(var2['HLT_CaloJet550_NoJetID'], var2['HLT_PFHT1050'])
    trig1 = np.multiply(trig11, trig12)
    trig2 = np.multiply(trig21, trig22)
    
    fill_hist(jj_mass1, var1['jj_mass'], weights=trig1)
    fill_hist(jj_mass2, var2['jj_mass'], weights=trig2)

    out_file = TFile(output_file, "RECREATE")
    jj_mass1.Write()
    jj_mass2.Write()

    jj_mass1.SetLineColor(2)
    jj_mass1.SetTitle(title1)
    jj_mass1.GetXaxis().SetTitle("m_{jj} (GeV)")
    jj_mass1.GetYaxis().SetTitle("(a.u.)")
    jj_mass2.SetLineColor(4)
    jj_mass2.SetTitle(title2)
    jj_mass2.GetXaxis().SetTitle("m_{jj} (GeV)")
    jj_mass2.GetYaxis().SetTitle("(a.u.)")

    canvas = TCanvas("canvas", "canvas", 600, 600)
    canvas.cd()
    jj_mass1.DrawNormalized()
    jj_mass2.DrawNormalized("SAME")
    l = TLegend(0.7,0.8,0.9,0.9)
    l.AddEntry(jj_mass1, title1)
    l.AddEntry(jj_mass2, title2) 
    l.Draw()

    out_file.cd() 
    canvas.Write()
    out_file.Close()
    print "saved plots as "+output_file


def produce(sample_title, LHE_weight=False, PU_weight=False, isSignal=False):

    ## open flatTuples and fill histograms
     
    isMC = False
    if 'MC' in sample_title:
        isMC = True
    data_set_file = "samples_{}.json".format(sample_title)
    if isMC:
        sample_dir = "/eos/user/m/msommerh/Zprime_to_bb_analysis/weighted/"
    else:
        sample_dir = "/eos/user/m/msommerh/Zprime_to_bb_analysis/"

    output_files = []
    file_list = []
    nfiles = [] 
    with open(data_set_file, 'r') as json_file:
        data_sets = json.load(json_file)
    for title in data_sets.keys():
        if isSignal: output_files.append("merged_files/merged_trig_{}.root".format(title))
        j = 0
        while True:
            if title == "data_2018_D":      ## remove later FIXME
                adhoc = "parallel_execution/"
                print "using pararallel execution branch for now"
            else:
                adhoc = ""     
            file_path = sample_dir+adhoc+title+"/"+title+"_flatTuple_{}.root".format(j)  ## remove later FIXME
            #file_path = sample_dir+title+"/"+title+"_flatTuple_{}.root".format(j) 
            if os.path.exists(file_path):
                file_list.append(file_path)
                j += 1
            else:
                print "found {} files for sample:".format(j), title
                nfiles.append(j)
                break
        if j == 0: 
            print '  WARNING: files for sample', title , 'do not exist, continuing'
            return True
    if not isSignal: output_files.append("merged_files/merged_trig_{}.root".format(sample_title))    

    m=0
    for n, output_file in enumerate(output_files):
       
        weight_string = ''
        if LHE_weight: 
             weight_string += 'LHEWeighted_'
        if PU_weight: 
             weight_string += 'PUWeighted_'

        print "working on output file:", output_file if isSignal else output_file.replace(sample_title, weight_string+sample_title)

        ## initialize histograms
        
        jpt1 = TH1D("jet_pT_1", "jet_pT_1", 200, 0, 4500)
        jpt2 = TH1D("jet_pT_2", "jet_pT_2", 200, 0, 4500)
        jpt = TH1D("jet_pT", "jet_pT", 200, 0, 4500)
        jmass_1 = TH1D("jmass_1", "jmass_1", 200, 0, 700)
        jmass_2 = TH1D("jmass_2", "jmass_2", 200, 0, 700)
        jmass = TH1D("jmass", "jmass", 200, 0, 700)
        jdeepFlavour_1 = TH1D("jdeepFlavour_1", "jdeepFlavour_1", 200, 0., 1.)
        jdeepFlavour_2 = TH1D("jdeepFlavour_2", "jdeepFlavour_2", 200, 0., 1.)
        jdeepFlavour = TH1D("jdeepFlavour", "jdeepFlavour", 200, 0., 1.)
        jj_mass = TH1D("jj_mass", "jj_mass", 400, 0, 10000)

        branches = ['jpt_1', 'jpt_2', 'jmass_1', 'jmass_2', 'jj_mass', 'jdeepFlavour_1', 'jdeepFlavour_2']
        selection = "jj_mass>1200 && jpt_1>500 && jj_deltaEta<1.3"
        if '2016' in sample_title:
            selection += " && HLT_AK8PFJet500==1. && HLT_PFJet500==1. && HLT_CaloJet500_NoJetID==1. && HLT_PFHT900==1."
            #branches += ['HLT_AK8PFJet500', 'HLT_PFJet500', 'HLT_CaloJet500_NoJetID', 'HLT_PFHT900']
        else:
            selection += " && HLT_AK8PFJet550==1. && HLT_PFJet550==1. && HLT_CaloJet550_NoJetID==1. && HLT_PFHT1050==1."
            #branches += ['HLT_AK8PFJet550', 'HLT_PFJet550', 'HLT_CaloJet550_NoJetID', 'HLT_PFHT1050']
        weight_branches = ['eventWeightLumi', 'GenWeight', 'PSWeight', 'PUWeight', 'LHEWeight_originalXWGTUP', 'LHEReweightingWeight', 'LHEScaleWeight']
  
        if isSignal:
            sub_list = file_list[m:m+nfiles[n]]
        else:
            sub_list = file_list[:]
     
        for sample in sub_list:
        
            print "opening files:", sample
    
            if isMC and not isSignal: 
                try:
                    variables = root2array(sample, treename='tree', branches=branches+weight_branches, selection=selection)
                    weights = variables['eventWeightLumi']
                except:
                    print "import failed!!"
                    m += nfiles[n]
                    continue
                if LHE_weight: 
                    weights = np.multiply(weights, variables['LHEWeight_originalXWGTUP'])
                if PU_weight: 
                    weights = np.multiply(weights,variables['PUWeight'])
    
            else:
                try:
                    variables = root2array(sample, treename='tree', branches=branches, selection=selection)
                    weights = np.ones(variables.shape[0])
                except:
                    print "import failed!!"
                    m += nfiles[n]
                    continue
           
            #if '2016' in sample_title:
            #    print "using lower trigger requirements for 2016 sample compatibility"
            #    trigger1 = np.multiply(variables['HLT_AK8PFJet500'], variables['HLT_PFJet500'])
            #    trigger2 = np.multiply(variables['HLT_CaloJet500_NoJetID'], variables['HLT_PFHT900'])
            #else:
            #    trigger1 = np.multiply(variables['HLT_AK8PFJet550'], variables['HLT_PFJet550'])
            #    trigger2 = np.multiply(variables['HLT_CaloJet550_NoJetID'], variables['HLT_PFHT1050'])
            #trigger = np.multiply(trigger1, trigger2)
        
            #weights = np.multiply(weights, trigger)
        
            fill_hist(jpt1, variables['jpt_1'], weights=weights)
            fill_hist(jpt2, variables['jpt_2'], weights=weights)
            fill_hist(jpt, np.concatenate((variables['jpt_1'], variables['jpt_2'])), weights=np.concatenate((weights,weights)))
            fill_hist(jmass_1, variables['jmass_1'], weights=weights)
            fill_hist(jmass_2, variables['jmass_2'], weights=weights)
            fill_hist(jmass, np.concatenate((variables['jmass_1'], variables['jmass_2'])), weights=np.concatenate((weights, weights)))
            fill_hist(jdeepFlavour_1, variables['jdeepFlavour_1'], weights=weights)
            fill_hist(jdeepFlavour_2, variables['jdeepFlavour_2'], weights=weights)
            fill_hist(jdeepFlavour, np.concatenate((variables['jdeepFlavour_1'], variables['jdeepFlavour_2'])), weights=np.concatenate((weights, weights)))
            fill_hist(jj_mass, variables['jj_mass'], weights=weights)
        
        ## draw histograms
    
        #out_file_name = "merged_files/merged_trig_{}.root".format(weight_string+sample_title)
        #out_file = TFile(out_file_name, "RECREATE")
        out_file = TFile(output_file if isSignal else output_file.replace(sample_title, weight_string+sample_title), "RECREATE")
        jpt1            .Write()             
        jpt2            .Write()     
        jpt             .Write()     
        jmass_1         .Write()     
        jmass_2         .Write()     
        jmass           .Write()
        jdeepFlavour_1  .Write()
        jdeepFlavour_2  .Write()
        jdeepFlavour    .Write() 
        jj_mass         .Write()     
        out_file.Close()
    
        jpt1            .Delete()
        jpt2            .Delete()
        jpt             .Delete()
        jmass_1         .Delete()
        jmass_2         .Delete()
        jmass           .Delete()
        jdeepFlavour_1  .Delete()
        jdeepFlavour_2  .Delete()
        jdeepFlavour    .Delete() 
        jj_mass.        Delete()   
 
        m += nfiles[n]

def compare(year):

    hist1 = extract_jj_mass("merged_files/merged_trig_data_{}.root".format(year))
    hist2 = extract_jj_mass("merged_files/merged_trig_MC_QCD_{}.root".format(year))
    #hist3 = extract_jj_mass("merged_files/merged_trig_LHEWeighted_MC_QCD_{}.root".format(year)) 
    hist4 = extract_jj_mass("merged_files/merged_trig_PUWeighted_MC_QCD_{}.root".format(year)) 
    #hist5 = extract_jj_mass("merged_files/merged_trig_LHEWeighted_PUWeighted_MC_QCD_{}.root".format(year)) 
    hist1.SetLineColor(1) 
    hist2.SetLineColor(2)
    #hist3.SetLineColor(4)
    hist4.SetLineColor(6)
    #hist5.SetLineColor(7)
 
    outfile = TFile("compare_MC_to_data_{}_new_weights.root".format(year), "RECREATE")
    c = TCanvas("canvas", "canvas", 600, 600)
    hist2.GetXaxis().SetTitle("m_{jj}")
    hist2.GetYaxis().SetTitle("nEvents")   
    hist2.SetTitle("MC_vs_data_"+year)
    hist2.Draw()
    hist1.Draw("SAME")
    #hist3.Draw("SAME")
    hist4.Draw("SAME")
    #hist5.Draw("SAME")
    l = TLegend(0.7,0.8,0.9,0.9)
    l.AddEntry(hist1, "data")
    l.AddEntry(hist2, "MC") 
    #l.AddEntry(hist3, "MC_LHE")
    l.AddEntry(hist4, "MC_PU")
    #l.AddEntry(hist5, "MC_LHE_PU")
    l.Draw()

    outfile.cd() 
    c.Write()
    c.SaveAs("compare_MC_to_data_{}_new_weights.png".format(year))
    outfile.Close()
    print "saved canvas in compare_MC_to_data_{}_new_weights.root".format(year)

def SigvsBkg(year):

    outfile = TFile("compare_Sig_to_Bkg_{}.root".format(year), "RECREATE")

    bkg_hist_b = extract_btag("merged_files/merged_trig_MC_QCD_{}.root".format(year))
    bkg_hist_b.SetLineColor(2) 
    bkg_hist_b.SetTitle("MC_Sig_vs_Bkg_"+year)  
    bkg_hist_b.GetXaxis().SetTitle("deepFlavour")
    bkg_hist_b.GetYaxis().SetTitle("(a.u.)")
    bkg_hist_m = extract_jj_mass("merged_files/merged_trig_MC_QCD_{}.root".format(year))
    bkg_hist_m.SetLineColor(2) 
    bkg_hist_m.SetTitle("MC_Sig_vs_Bkg_"+year)  
    bkg_hist_m.GetXaxis().SetTitle("m_{jj}")
    bkg_hist_m.GetYaxis().SetTitle("(a.u.)")

    signal_hists_b = []
    signal_hists_m = []
    canvases_b = []
    canvases_m = []
    for i, m in enumerate(masspoints):
        m_title="MC_Sig_vs_Bkg_{}_M{}".format(year,m)
        signal_hists_b.append(extract_btag("merged_files/merged_trig_MC_signal_{}_M{}.root".format(year, m)))
        signal_hists_b[i].SetLineColor(4)
        signal_hists_b[i].SetTitle(m_title)
        signal_hists_b[i].GetXaxis().SetTitle("deepFlavour")
        signal_hists_b[i].GetYaxis().SetTitle("(a.u.)")
        bkg_hist_b.SetTitle(m_title)  
        signal_hists_m.append(extract_jj_mass("merged_files/merged_trig_MC_signal_{}_M{}.root".format(year, m)))
        signal_hists_m[i].SetLineColor(4)
        signal_hists_m[i].SetTitle(m_title)
        signal_hists_m[i].GetXaxis().SetTitle("m_{jj}")
        signal_hists_m[i].GetYaxis().SetTitle("(a.u.)")
        bkg_hist_m.SetTitle(m_title)
       
        canvases_b.append(TCanvas("btag_M"+str(m), "btag_M"+str(m), 600, 600))
        canvases_b[i].cd()
        bkg_hist_b.DrawNormalized()
        signal_hists_b[i].DrawNormalized("SAME")
        if i==0:
            l = TLegend(0.7,0.8,0.9,0.9)
            l.AddEntry(signal_hists_b[i], "MC_signal")
            l.AddEntry(bkg_hist_b, "MC_bkg") 
        l.Draw()
        canvases_m.append(TCanvas("m_jj_M"+str(m), "m_jj_M"+str(m), 600, 600))
        canvases_m[i].cd()
        bkg_hist_m.DrawNormalized()
        signal_hists_m[i].DrawNormalized("SAME")
        l.Draw()

        outfile.cd() 
        canvases_b[i].Write()
        canvases_m[i].Write()

    outfile.Close()
    print "saved as compare_Sig_to_Bkg_{}.root".format(year)

if __name__ == '__main__':

    if options.produce:

        if options.signal:
            produce("MC_signal_"+options.year, LHE_weight=False, PU_weight=False, isSignal=True)
   
        elif options.single_process != 0:
            print "producing a single file"
            if options.single_process == 1:
                print "MC_QCD_"+options.year+", LHE_weight=False, PU_weight=False"
                produce("MC_QCD_"+options.year, LHE_weight=False, PU_weight=False)
            elif options.single_process == 2:
                print "MC_QCD_"+options.year+", LHE_weight=True, PU_weight=False"
                produce("MC_QCD_"+options.year, LHE_weight=True, PU_weight=False)
            elif options.single_process == 3:
                print "MC_QCD_"+options.year+", LHE_weight=False, PU_weight=True"
                produce("MC_QCD_"+options.year, LHE_weight=False, PU_weight=True)
            elif options.single_process == 4:
                print "MC_QCD_"+options.year+", LHE_weight=True, PU_weight=True"
                produce("MC_QCD_"+options.year, LHE_weight=True, PU_weight=True)
            elif options.single_process == 5:
                print "data_"+options.year+", LHE_weight=False, PU_weight=False"                                    
                produce("data_"+options.year, LHE_weight=False, PU_weight=False)
            else:
                print "unknown process flag"

        else:
            print "producing all files at once"
            jobs = []
            sample_title = "MC_QCD_"+options.year
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
            sample_title = "data_"+options.year
            module = lambda : produce(sample_title, LHE_weight=False, PU_weight=False)
            p = multiprocessing.Process(target=module)
            jobs.append(p)
            p.start()

    if options.compare:
 
        compare(options.year)

    if options.SigvsBkg: 
        SigvsBkg(options.year)
