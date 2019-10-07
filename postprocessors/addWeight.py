#! /usr/bin/env python

import os, multiprocessing, math
import numpy as np
from array import array
from ROOT import TFile, TH1, TF1, TLorentzVector
import ROOT

import optparse
usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)
parser.add_option('-y', '--year', action='store', type='string', dest='year',default='2017')
parser.add_option('-f', '--filter', action='store', type='string', dest='filter', default='')
parser.add_option('-s', '--single', action='store_true', dest='single', default=False)
parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False)

(options, args) = parser.parse_args()

filterset   = options.filter
singlecore  = options.single
verboseout  = options.verbose
year        = options.year
isMC	    = True #only reweight MC anyway


if year=='2016':
    LUMI=35920.
elif year=='2017':
    LUMI=41530.
elif year=='2018':
    LUMI=59740.



##############################

def getXsec(sample):
  print "Xsec("+sample+")"
  if sample.find( "QCD_Pt_170to300_"                     ) !=-1 : return 117276.;
  elif sample.find( "QCD_Pt_300to470_"                     ) !=-1 : return 7823.;
  elif sample.find( "QCD_Pt_470to600_"                     ) !=-1 : return 648.2;
  elif sample.find( "QCD_Pt_600to800_"                     ) !=-1 : return 186.9;
  elif sample.find( "QCD_Pt_800to1000_"                    ) !=-1 : return 32.293;
  elif sample.find( "QCD_Pt_1000to1400_"                   ) !=-1 : return 9.4183;
  elif sample.find( "QCD_Pt_1400to1800_"                   ) !=-1 : return 0.84265;
  elif sample.find( "QCD_Pt_1800to2400_"                   ) !=-1 : return 0.114943;
  elif sample.find( "QCD_Pt_2400to3200_"                   ) !=-1 : return 0.006830;
  elif sample.find( "QCD_Pt_3200toInf_"                    ) !=-1 : return 0.000165445;
  elif sample.find( "QCD_HT100to200"                       ) !=-1 : return 27990000;
  elif sample.find( "QCD_HT200to300"                       ) !=-1 : return 1712000.;
  elif sample.find( "QCD_HT300to500"                       ) !=-1 : return 347700.;
  elif sample.find( "QCD_HT500to700"                       ) !=-1 : return 32100.;
  elif sample.find( "QCD_HT700to1000"                      ) !=-1 : return 6831.;
  elif sample.find( "QCD_HT1000to1500"                     ) !=-1 : return 1207.;
  elif sample.find( "QCD_HT1500to2000"                     ) !=-1 : return 119.9;
  elif sample.find( "QCD_HT2000toInf"                      ) !=-1 : return 25.24;
  elif sample.find( "QCD_Pt-15to7000" ) !=-1 or sample.find( "QCD_Pt_15to7000" ) !=-1: return  2.022100000e+09;
  elif sample.find("SingleMuon")!=-1  or sample.find("SingleElectron") !=-1 or sample.find("JetHT") !=-1 or sample.find("data") !=-1 : return 1.
  else:
          print "Cross section not defined for this sample!!"
          print "--> Returning 1. for test purposes."
          return 1.

def processFile(sample, origin, target, verbose=False):

    if not os.path.exists(origin):
        print 'Origin directory', origin, 'does not exist, aborting...'
        exit()
    if not os.path.exists(target):
        print 'Target directory', target,'does not exist, creating it now'
        os.makedirs(target)

    ## Unweighted input
    #ref_file_name = origin + '/' + sample_name
    #if not os.path.exists(ref_file_name):
    #    print '  WARNING: file', ref_file_name, 'does not exist, continuing'
    #    return True

    # first loop over all files to get nGenEvents
    totalEntries = 0.
    file_list = []
    j = 0
    while True:
        if os.path.exists(origin + "/" + sample + "_flatTuple_{}.root".format(j)):
            file_list.append(origin + "/" + sample + "_flatTuple_{}.root".format(j))
            j += 1
        else:
            print "found {} files for sample:".format(j), sample
            break
    if j == 0: 
        print '  WARNING: files for sample', sample , 'do not exist, continuing'
        return True
    for infile_name in file_list:
	infile = TFile(infile_name, 'READ')
	evtHist = infile.Get('Events')
	try:
            nEvents = evtHist.GetBinContent(1)
            totalEntries += nEvents
            print "sample:",sample,"nEvents:", nEvents
        except:
            print '  ERROR: nEvents not found in file', sample
            exit(1)
	infile.Close()
    print "totalEntries =", totalEntries

    # Cross section
    XS = getXsec(sample.replace(year+'_',''))

    Leq = LUMI*XS/totalEntries if totalEntries > 0 else 0.
    print sample, ": Leq =", (Leq if isMC else "Data")


    # Open old files now to plug in weights
    for ref_file_name in file_list:
        print "working on file:", ref_file_name

        # Weighted output
        new_file_name = ref_file_name.replace(origin, target)

        new_file = TFile(new_file_name, 'RECREATE')
        new_file.cd()

        ref_file = TFile(ref_file_name, 'READ')

        # Variables declaration
        eventWeightLumi = array('f', [1.0])# global event weight with lumi
        # Looping over file content
        for key in ref_file.GetListOfKeys():
            obj = key.ReadObj()
            # Histograms
            if obj.IsA().InheritsFrom('TH1'):
                if verbose: print ' + TH1:', obj.GetName()
                new_file.cd()
                obj.Write()
            # Tree
            elif obj.IsA().InheritsFrom('TTree'):
                nev = obj.GetEntriesFast()
                new_file.cd()
                new_tree = obj.CopyTree("")
                # New branches
                eventWeightLumiBranch = new_tree.Branch('eventWeightLumi', eventWeightLumi, 'eventWeightLumi/F')

                # looping over events
                for event in range(0, obj.GetEntries()):
                    if verbose and (event%10000==0 or event==nev-1): print ' = TTree:', obj.GetName(), 'events:', nev, '\t', int(100*float(event+1)/float(nev)), '%\r',
                    obj.GetEntry(event)
                    # Initialize
                    eventWeightLumi[0] = 1.
	
                    # Weights
                    if isMC:
                        eventWeightLumi[0] = obj.GenWeight * Leq

                    # Fill the branches
                    eventWeightLumiBranch.Fill()
                new_file.cd()
                new_tree.Write()
                if verbose: print ' '

            # Directories
            elif obj.IsFolder():
                subdir = obj.GetName()
                if verbose: print ' \ Directory', subdir, ':'
                new_file.mkdir(subdir)
                new_file.cd(subdir)
                for subkey in ref_file.GetDirectory(subdir).GetListOfKeys():
                    subobj = subkey.ReadObj()
                    if subobj.IsA().InheritsFrom('TH1'):
                        if verbose: print '   + TH1:', subobj.GetName()
                        new_file.cd(subdir)
                        subobj.Write()
                new_file.cd('..')
        new_file.Close()
	ref_file.Close()


HT_bins = ['50to100', '100to200', '200to300', '300to500', '500to700', '700to1000', '1000to1500', '1500to2000', '2000toInf']

#sample_name = 'test'
#sample_names = [sample_name] ## for testing

sample_names = []
for HT_bin in HT_bins[2:]:  ##only part of HT_bins selected FIXME FIXME
    sample_names.append("MC_QCD_{}_HT{}".format(year, HT_bin))

jobs = []
for d in sample_names:
    origin = '/eos/user/m/msommerh/Zprime_to_bb_analysis/'+d
    target = '/eos/user/m/msommerh/Zprime_to_bb_analysis/weighted/'+d
    #origin = 'test_outfiles'
    #target = 'test_outfiles/weighted'

    print "working on",origin
    print "output will be stored in", target

    if singlecore:
        print " -", d
        processFile(d, origin, target, verboseout)
    else:
        p = multiprocessing.Process(target=processFile, args=(d, origin, target, verboseout,))
        jobs.append(p)
        p.start()

