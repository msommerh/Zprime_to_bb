#! /usr/bin/env python

###
### Main macro for producing ntuples.
###

# Author: Manuel Sommerhalder (September 2019)
# Inspiration:
#       https://github.com/IzaakWN/NanoTreeProducer
import global_paths
import sys
for n, i in enumerate(sys.path):
        if i == global_paths.MAINDIR+'CMSSW_10_3_3/lib/slc6_amd64_gcc700':
                sys.path[n] = global_paths.CMSSWDIR+'lib/slc6_amd64_gcc700'
        if i == global_paths.MAINDIR+'CMSSW_10_3_3/python':
                sys.path[n] = global_paths.CMSSWDIR+'python'

from postprocessors import modulepath
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import *
from argparse import ArgumentParser
from math import ceil

import multiprocessing

def Run(outdir, subsample, branchsel, modules, postfix, json, isMC):
    if isMC:
        p = PostProcessor(outdir, subsample, None, branchsel, noOut=False, modules=modules, provenance=False, postfix=postfix.replace('.root', '_'+str(n)+'.root'))#, compression=0)
    else:
        p = PostProcessor(outdir, subsample, None, branchsel, noOut=False, modules=modules, provenance=False, jsonInput=json, postfix=postfix.replace('.root', '_'+str(n)+'.root'))#, compression=0)
    p.run()

parser = ArgumentParser()
parser.add_argument('-t', '--title',  dest='title',   action='store', type=str, default='test')
parser.add_argument('-i', '--infiles',  dest='infiles',   action='store', type=str, default='filelists/default.txt')
parser.add_argument('-o', '--outdir',   dest='outdir',    action='store', type=str, default='test_outfiles')
parser.add_argument('-n', '--nFiles',  dest='nFiles',   action='store', type=int, default=10)
parser.add_argument('-y', '--year',  dest='year',   action='store', type=int, default=2016)
parser.add_argument('-MC', '--isMC',   dest='isMC',  action='store_true', default=False)
parser.add_argument('-r', '--resubmit',  dest='resubmit',   action='store', type=int, default=-1)
parser.add_argument('-mp', '--multiprocessing',  dest='multiprocessing',   action='store_true', default=False)
args = parser.parse_args()

year = args.year
if args.multiprocessing:
    print "Multiprocessing enabled"
else:
    print "Multiprocessing not enabled"
outdir    = args.outdir
#postfix   = outdir+"/"+args.title+'_flatTuple.root'
postfix   = '_recal'
nFiles    = args.nFiles
branchsel = "%s/keep_and_drop.txt"%modulepath
#branchsel = None
json = global_paths.MAINDIR+"json/"
if year == 2016:
        json += "Cert_271036-284044_13TeV_PromptReco_Collisions16_JSON.txt"   
elif year == 2017:
        json += "Cert_294927-306462_13TeV_PromptReco_Collisions17_JSON.txt"
elif year == 2018:
        json += "Cert_314472-325175_13TeV_PromptReco_Collisions18_JSON.txt"
else:
        print "Invalid year!! Aborting postprocessing!!"
        sys.exit()
infiles = []
filelist = open(args.infiles, 'r').readlines()
for entry in filelist:
        if not entry.startswith("#"): 
                filepath = entry.replace('\n','')
                #filepath = filepath.replace('cms-xrd-global.cern.ch', 'xrootd-cms.infn.it')
                filepath = filepath.replace('cms-xrd-global.cern.ch', 'cmsxrootd.fnal.gov')
                infiles.append(filepath)

print ">>> %-10s = %s"%('output file',postfix)
print ">>> %-10s = %s"%('infiles',infiles)
print ">>> %-10s = %s"%('year',str(year))

run_letter = args.infiles[-5]
print "run_letter =", run_letter
if run_letter not in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
    print "invalid run letter"
    sys.exit()

from modules.ModuleDijetMass import DijetMassProducer as Producer
from modules.ModuleRecal import createJMECorrector

JEC_module = createJMECorrector(isMC=args.isMC, dataYear=year, runPeriod=run_letter, jesUncert="Total", redojec=True, jetType = "AK4PFchs", noGroom=False)

jobs = []
for n in range(int(ceil(float(len(infiles))/nFiles))):
        if args.resubmit != -1 and n != args.resubmit: continue
        sys.stderr.write("working on file nr "+str(n)+"\n")
        subsample = infiles[n*nFiles:(n+1)*nFiles]
        mjj_module = lambda: Producer(postfix.replace('.root', '_'+str(n)+'.root'), isMC=args.isMC, year=year)
       
        #RunProcess = lambda : Run(subsample, branchsel, mjj_module, postfix, json, args.isMC)
        RunProcess = lambda : Run(outdir, subsample, branchsel, [JEC_module()], postfix, json, args.isMC) 
        #RunProcess = lambda : Run(subsample, branchsel, [JEC_module(), mjj_module()], postfix, json, args.isMC)
        
        if args.multiprocessing:                     
            p = multiprocessing.Process(target=RunProcess)
            jobs.append(p)
            p.start()        
        else:
            RunProcess()

