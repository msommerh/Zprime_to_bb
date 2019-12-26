#! /usr/bin/env python

###
### Macro for skimming the weighted ntuples heavily to a compact size.
###

import global_paths
import os
from array import array
from ROOT import TFile, TChain, TTree, TH1
from aliases import triggers

inDir = global_paths.WEIGHTEDDIR[:-1]
outDir = global_paths.SKIMMEDDIR[:-1]

blacklist = ["backup"]
cutstring = "jpt_1>550 && "+triggers

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


dirList = [x for x in os.listdir(inDir) if not x in blacklist]
for d in dirList:
    skim(d)
