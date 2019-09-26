#! /usr/bin/env python
# Author: Manuel Sommerhalder (September 2019)
# Inspiration:
#	https://github.com/IzaakWN/NanoTreeProducer
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

parser = ArgumentParser()
parser.add_argument('-t', '--title',  dest='title',   action='store', type=str, default='test')
parser.add_argument('-i', '--infiles',  dest='infiles',   action='store', type=str, default='filelists/default.txt')
parser.add_argument('-o', '--outdir',   dest='outdir',    action='store', type=str, default='test_outfiles')
parser.add_argument('-n', '--nFiles',  dest='nFiles',   action='store', type=int, default=10)
parser.add_argument('-y', '--year',  dest='year',   action='store', type=int, default=2016)
args = parser.parse_args()

year = args.year
if year == 0: year = "QCD"
outdir    = args.outdir
postfix   = outdir+"/"+args.title+'_flatTuple.root'
nFiles 	  = args.nFiles
branchsel = "%s/keep_and_drop.txt"%modulepath
infiles = []
filelist = open(args.infiles, 'r').readlines()
for entry in filelist:
	if not entry.startswith("#"): 
		filepath_ = entry.replace('\n','')
		filepath = filepath_.replace('cms-xrd-global.cern.ch', 'xrootd-cms.infn.it')
		infiles.append(filepath)

print ">>> %-10s = %s"%('output file',postfix)
print ">>> %-10s = %s"%('infiles',infiles)
print ">>> %-10s = %s"%('year',str(year))

from modules.ModuleZprimetobb import ZprimetobbProducer

for n in range(int(ceil(float(len(infiles))/nFiles))):

	subsample = infiles[n*nFiles:(n+1)*nFiles]
	module2run = lambda: ZprimetobbProducer(postfix.replace('.root', '_'+str(n)+'.root'), isMC=True, year=year)

	p = PostProcessor('.', subsample, None, branchsel, noOut=True, modules=[module2run()], provenance=False, postfix=postfix.replace('.root', '_'+str(n)+'.root'), compression=0)
	p.run()
