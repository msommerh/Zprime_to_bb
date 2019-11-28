#! /usr/bin/env python

import os
from array import array
from ROOT import TFile, TChain, TTree, TH1

#inDir = "/eos/user/z/zucchett/ZBB/"
inDir = "/eos/user/m/msommerh/Zprime_to_bb_analysis/weighted"
#inDir = "/afs/cern.ch/work/m/msommerh/public/Zprime_to_bb_Analysis/MC_signal_weighted"
outDir = "/afs/cern.ch/work/m/msommerh/public/Zprime_to_bb_Analysis/Skim"

blacklist = ["backup"]
cutstring = "jpt_1>550 && (HLT_PFHT1050 || HLT_PFHT900 || HLT_PFJet500 || HLT_PFJet550 || HLT_CaloJet500_NoJetID || HLT_CaloJet550_NoJetID || HLT_AK8PFJet500 || HLT_AK8PFJet550)"


def skim(sample):
    print sample
    fileList = os.listdir(inDir+"/"+sample)
    if len(fileList)==0: return
    print fileList
    chain = TChain("tree")
    for f in fileList:
        chain.Add(inDir+"/"+sample+"/"+f)
        print chain.GetNtrees(), chain.GetEntries(), inDir+"/"+sample+"/"+f
    #return
    
    
    # save to new file
    outFile = TFile(outDir+"/"+sample+".root", "RECREATE")
    outFile.cd()
    # create a new skimmed tree
    tree = chain.CopyTree(cutstring)#GetTree().CloneTree(-1, cutstring)
    tree.Write()
    outFile.Close()

    chain.Reset()


#dirList = [x for x in os.listdir(inDir) if not x in blacklist]
dirList = [x for x in os.listdir(inDir) if not x in blacklist and not 'data' in x] ## veto data, remove later FIXME FIXME FIXME
for d in dirList:
    skim(d)
