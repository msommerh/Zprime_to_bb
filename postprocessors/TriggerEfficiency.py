#! /usr/bin/env python

###
### Macro needed to find the acceptance from generated objects by directly running on NanoAOD.
###

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

def Run(subsample, module2run, postfix):
    p = PostProcessor('.', subsample, None, '', noOut=True, modules=[module2run()], provenance=False, postfix=postfix, compression=0)
    p.run()

parser = ArgumentParser()
parser.add_argument('-y', '--year',  dest='year',   action='store', type=int, default=2016)
parser.add_argument('-mp', '--multiprocessing',  dest='multiprocessing',   action='store_true', default=False)
args = parser.parse_args()

year = args.year

if args.multiprocessing:
    print "Multiprocessing enabled"
else:
    print "Multiprocessing not enabled"
outdir    = '/afs/cern.ch/work/m/msommerh/public/Zprime_to_bb_Analysis/trigger' ## FIXME INSERT GLOBALPATH FIXME

jobs = []

data_2016_letters = ["B", "C", "D", "E", "F", "G", "H"]
data_2017_letters = ["B", "C", "D", "E", "F"]
data_2018_letters = ["A", "B", "C", "D"]

sample_names = []
if year==2016:
    letters = data_2016_letters
elif year==2017:
    letters = data_2017_letters
elif year==2018:
    letters = data_2018_letters
else:
    print "unknown year"
    sys.exit()
for letter in letters:
    sample_names.append("SingleMuon_{}_{}".format(year, letter))

jobs = []
for title in sample_names:
    postfix   = outdir+"/"+title+'_triggers.root'
    filelist_file = 'filelists/{}.txt'.format(title)
    infiles = []
    filelist = open(filelist_file, 'r').readlines()
    for entry in filelist:
            if not entry.startswith("#"): 
                    filepath = entry.replace('\n','')
                    #filepath = filepath.replace('cms-xrd-global.cern.ch', 'xrootd-cms.infn.it')
                    infiles.append(filepath)
    
    print ">>> %-10s = %s"%('output file',postfix)
    print ">>> %-10s = %s"%('infiles',infiles)
    print ">>> %-10s = %s"%('year',year)
    
    from modules.ModuleTriggers import TriggerProducer
    
    module2run = lambda: TriggerProducer(postfix, isMC=True, year=year)
    RunProcess = lambda : Run(infiles, module2run, postfix)
    
    if args.multiprocessing:
        p = multiprocessing.Process(target=RunProcess)
        jobs.append(p)
        p.start()        
    else:
        RunProcess()

