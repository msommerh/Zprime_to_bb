#! /usr/bin/env python
# Author: Manuel Sommerhalder (September 2019)
# Inspiration:
#       https://github.com/IzaakWN/NanoTreeProducer
import sys
for n, i in enumerate(sys.path):
        if i == '/afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/src/NanoTreeProducer/CMSSW_10_3_3/lib/slc6_amd64_gcc700':
                sys.path[n] = '/afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/lib/slc6_amd64_gcc700'
        if i == '/afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/src/NanoTreeProducer/CMSSW_10_3_3/python':
                sys.path[n] = '/afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/python'
from postprocessors import modulepath
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import *
from argparse import ArgumentParser
from math import ceil

import multiprocessing

def Run(subsample, module2run, postfix):
    p = PostProcessor('.', subsample, None, "%s/keep_and_drop.txt"%modulepath, noOut=True, modules=[module2run()], provenance=False, postfix=postfix, compression=0)
    p.run()

parser = ArgumentParser()
parser.add_argument('-o', '--obj',  dest='obj', action='store',  nargs='+', type=str)
parser.add_argument('-mp', '--multiprocessing',  dest='multiprocessing',   action='store_true', default=False)
args = parser.parse_args()

mass_points = [1800, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 7000, 8000]
#mass_points = [5000, 5500, 6000, 7000, 8000]

if args.multiprocessing:
    print "Multiprocessing enabled"
else:
    print "Multiprocessing not enabled"
#outdir    = args.outdir
#outdir    = '/afs/cern.ch/work/m/msommerh/public/Zprime_to_bb_Analysis/objectCounter' ## FIXME
outdir    = '.' ## FIXME

objs = args.obj
print "objects:",objs

jobs = []

samples = []
#for mcType in ["signal", "QCD", "TTbar"]:
for mcType in ["QCD"]:
    data_type="MC_"+mcType
    for year in ['2016','2017','2018']:
        if mcType=="TTbar":
            sample_name = data_type+"_"+year
            sample_name+="_TTToHadronic"
            samples.append(sample_name)
        elif mcType=="QCD":
            #for HT_bin in ['50to100', '100to200', '200to300', '300to500', '500to700', '700to1000', '1000to1500', '1500to2000', '2000toInf']:
            for HT_bin in ['1000to1500', '1500to2000', '2000toInf']:
                sample_name = data_type+"_"+year
                sample_name = sample_name+"_HT"+HT_bin
                samples.append(sample_name)
        elif mcType=="signal":
            for masspoint in ['1800', '2000', '2500', '3000', '3500', '4000', '4500', '5000', '5500', '6000', '7000', '8000']:
                sample_name = data_type+"_"+year
                sample_name = sample_name+"_M"+masspoint
                samples.append(sample_name)

print "samples =", samples

for sample in samples:
    title     = sample
    postfix   = outdir+"/"+title+'_objectCounter.root'
    filelist_file = 'filelists/{}.txt'.format(title)
    infiles = []
    filelist = open(filelist_file, 'r').readlines()
    for entry in filelist:
            if not entry.startswith("#"): 
                    filepath = entry.replace('\n','')
                    infiles.append(filepath)
    
    print ">>> %-10s = %s"%('sample',sample)
    print ">>> %-10s = %s"%('output file',postfix)
    print ">>> %-10s = %s"%('infiles',infiles)
    
    from modules.ModuleObjectCounter import ObjectCounterProducer
    
    module2run = lambda: ObjectCounterProducer(postfix, objs)
    
    RunProcess = lambda : Run(infiles, module2run, postfix)
    
    if args.multiprocessing:
        p = multiprocessing.Process(target=RunProcess)
        jobs.append(p)
        p.start()        
    else:
        RunProcess()

