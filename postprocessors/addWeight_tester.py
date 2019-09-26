#!/usr/bin/env python
import os, sys
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from modules.ModuleAddWeight import WeightProducer
from postprocessors import modulepath

module2run = lambda : WeightProducer()

#fnames=["/eos/cms/store/mc/RunIISummer16NanoAODv5/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PUMoriond17_Nano1June2019_102X_mcRun2_asymptotic_v7_ext2-v1/120000/FF69DF6E-2494-F543-95BF-F919B911CD23.root"]
#fnames=["root://xrootd-cms.infn.it//store/mc/RunIIAutumn18NanoAODv5/QCD_HT500to700_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano1June2019_102X_upgrade2018_realistic_v19-v1/70000/F0B8AFDC-7E59-2F45-B49E-911EED69872A.root"]
fnames=["root://xrootd-cms.infn.it//store/mc/RunIIAutumn18NanoAODv5/QCD_HT1500to2000_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/Nano1June2019_102X_upgrade2018_realistic_v19-v1/120000/092443A5-3799-3C46-A61F-27DE16ECBD5D.root"]

branchsel = "%s/keep_and_drop_Zprime_to_bb.txt"%modulepath

p=PostProcessor(".",fnames, None, branchsel, [module2run()], provenance=True)
p.run()

