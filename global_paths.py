#! /usr/bin/env python

###
### Auxiliary file defining all global paths for the analysis to work.
###

## primary work directory where the analysis scripts are located
MAINDIR = "/afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/src/NanoTreeProducer/"

## large enough storage space to hold the unskimmed primary ntuples produced directly from NanoAOD
PRODUCTIONDIR = "/eos/user/m/msommerh/Zprime_to_bb_analysis/"

## also large storage space to hold the unksimmed + weighted ntuples
WEIGHTEDDIR = "/eos/user/m/msommerh/Zprime_to_bb_analysis/weighted/"

## space to store the significantly smaller skimmed ntuples that are used for the main analysis
SKIMMEDDIR = "/afs/cern.ch/work/m/msommerh/public/Zprime_to_bb_Analysis/Skim/"

## location where the combine tool is installed
COMBINEDIR = "/afs/cern.ch/user/m/msommerh/CMSSW_10_2_13/src/HiggsAnalysis/CombinedLimit/"

## location where the HTCondor submission log files (including stderr & stdout) should be located
SUBMISSIONLOGS = "/afs/cern.ch/work/m/msommerh/public/Zprime_to_bb_Analysis/submission_files/"

## CMSSW directory that is used in the ntuple production
CMSSWDIR = "/afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/"

## exact location of GRID certificate to be sent to HTCondor
GRIDCERTIFICATE = "/afs/cern.ch/user/m/msommerh/x509up_msommerh"

if __name__ == "__main__":
    from argparse import ArgumentParser 
    parser = ArgumentParser()
    parser.add_argument('-g', '--get',   dest='get', type=str, default='', action='store', help="Global path to return.")
    args = parser.parse_args()

    if args.get != '':
        cmd = "print "+args.get
        try:
            exec cmd
        except NameError:
            print ''
    
