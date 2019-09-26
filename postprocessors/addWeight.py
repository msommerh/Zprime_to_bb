#! /usr/bin/env python

import os, multiprocessing, math
from array import array
from ROOT import TFile, TObject, TH1, TH1D, TF1, TLorentzVector

import optparse
usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)
parser.add_option('-i', '--input', action='store', type='string', dest='origin', default='/scratch/zucchett/Ntuple/WSF/')
parser.add_option('-f', '--filter', action='store', type='string', dest='filter', default='')
parser.add_option('-s', '--single', action='store_true', dest='single', default=False)
parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False)

(options, args) = parser.parse_args()

origin      = options.origin
filterset   = options.filter
singlecore  = options.single
verboseout  = options.verbose

#LUMI = 59970.
LUMI = 1.   # ----> plug in the right number or stick with 1 and multiply with right luminosity in analysis later

if not os.path.exists(origin):
    print 'Origin directory', origin, 'does not exist, aborting...'
    exit()


##############################

def getXsec(sample):
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
	  return 0

#def getLumi(sample):
#  return 59970.

def processFile(sample_name, verbose=False):
    sample = sample_name.replace(".root", "")
    
    treeFile_name = origin + '/' + sample + '.root'
    
    # Open file   ----> plug in the already open file from the module
    treeFile = TFile(treeFile_name, 'UPDATE')
    treeFile.cd()

    # number of events
    runTree = treeFile.Get('Runs')

    genH = TH1D("genH_%s" % sample, "", 1, 0, 0)
    genH.Sumw2()
    runTree.Draw("genEventCount>>genH_%s" % sample, "", "goff")
    genEv = genH.GetMean()*genH.GetEntries()
    
    # Cross section
    XS = getXsec(sample)
    
    Leq = LUMI*XS/genEv if genEv > 0 else 0.

    print sample, ": Leq =", Leq
    
    # Variables declaration
    eventweightlumi = array('f', [1.0])  # global event weight with lumi
    
    # Looping over file content
    # Tree
    tree = treeFile.Get('Events')
    nev = tree.GetEntriesFast()
    
    # New branches
    eventweightlumiBranch = tree.Branch('eventweightlumi', eventweightlumi, 'eventweightlumi/F')

    # looping over events
    for event in range(0, tree.GetEntries()):
        if verbose and (event%10000==0 or event==nev-1): print ' = TTree:', tree.GetName(), 'events:', nev, '\t', int(100*float(event+1)/float(nev)), '%\r',
        #print '.',#*int(20*float(event)/float(nev)),#printProgressBar(event, nev)
        tree.GetEntry(event)
        # Initialize
        eventweightlumi[0] = 1.
        
        # Weights
        eventweightlumi[0] = Leq * tree.lheweight * tree.btagweight #tree.puweight
            
        # Fill the branches
        eventweightlumiBranch.Fill()

    tree.Write("", TObject.kOverwrite)
    if verbose: print ' '
        
    treeFile.Close() 


#jobs = []
#for d in os.listdir(origin):
#    if not '.root' in d: continue
#    if len(filterset)>0 and not filterset in d: continue
#    
#    if singlecore:
#        print " -", d
#        processFile(d, verboseout)
#    else:
#        p = multiprocessing.Process(target=processFile, args=(d,verboseout,))
#        jobs.append(p)
#        p.start()
#    #exit()
#    
#print '\nDone.'
