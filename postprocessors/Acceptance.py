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
    p = PostProcessor('.', subsample, None, '', noOut=True, modules=[module2run()], provenance=False, postfix=postfix, compression=0)
    p.run()

parser = ArgumentParser()
#parser.add_argument('-t', '--title',  dest='title',   action='store', type=str, default='test')
#parser.add_argument('-i', '--infiles',  dest='infiles',   action='store', type=str, default='filelists/default.txt')
#parser.add_argument('-o', '--outdir',   dest='outdir',    action='store', type=str, default='test_outfiles')
#parser.add_argument('-n', '--nFiles',  dest='nFiles',   action='store', type=int, default=10)
parser.add_argument('-y', '--year',  dest='year',   action='store', type=int, default=2016)
parser.add_argument('-M', '--mass',  dest='mass',   action='store', type=str, default='all')
#parser.add_argument('-MC', '--isMC',   dest='isMC',  action='store_true', default=False)
#parser.add_argument('-r', '--resubmit',  dest='resubmit',   action='store', type=int, default=-1)
parser.add_argument('-mp', '--multiprocessing',  dest='multiprocessing',   action='store_true', default=False)
args = parser.parse_args()

mass_points = [1800, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 7000, 8000]
#mass_points = [5000, 5500, 6000, 7000, 8000]

year = args.year
mass = args.mass
if args.multiprocessing:
    print "Multiprocessing enabled"
else:
    print "Multiprocessing not enabled"
#outdir    = args.outdir
outdir    = '/afs/cern.ch/work/m/msommerh/public/Zprime_to_bb_Analysis/acceptance'

jobs = []

if mass!='all': mass_points = [mass]

for m in mass_points:
    title     = 'MC_signal_{}_M{}'.format(year, m)
    postfix   = outdir+"/"+title+'_acceptanceHist.root'
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
    
    from modules.ModuleAcceptance import AcceptanceProducer
    
    module2run = lambda: AcceptanceProducer(postfix, isMC=True, year=year)
    
    RunProcess = lambda : Run(infiles, module2run, postfix)
    
    if args.multiprocessing:
        p = multiprocessing.Process(target=RunProcess)
        jobs.append(p)
        p.start()        
    else:
        RunProcess()

