from ROOT import TFile, TObject, TH1, TH1D, TF1, TLorentzVector
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

LUMI = 1.   # ----> plug in the right number or stick with 1 and multiply with right luminosity in analysis later

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
	  print "--> Returning 1. for test purposes."
          return 1.

class WeightProducer(Module):
    def __init__(self):
        pass
    def beginJob(self):
        pass
    def endJob(self):
        pass
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):

	print "--- beginFile ---"
	
	self.sample = inputFile.GetName().replace(".root","")
	self.sample = self.sample.replace("root://xrootd-cms.infn.it/", "")
	self.sample = self.sample.replace("root://cms-xrd-global.cern.ch/", "")
	self.sample = self.sample[1:].replace("/", "_")
	print "namne of file:", self.sample

	# number of events
	self.runTree = inputFile.Get('Runs')
	self.genH = TH1D("genH_%s" % self.sample, "", 1, 0, 0)
	self.genH.Sumw2()
	self.runTree.Draw("genEventCount>>genH_%s" % self.sample, "", "goff")
	self.genEv = self.genH.GetMean()*self.genH.GetEntries()

	# Cross section
	self.XS = getXsec(self.sample)

	self.Leq = LUMI*self.XS/self.genEv if self.genEv > 0 else 0.
	print self.sample, ": Leq =", self.Leq

        self.out = wrappedOutputTree
        self.out.branch("eventweightlumi",  "F");

	print "--- end of beginFile ---"
	
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""

	# Initialize
        eventweightlumi = 1.

	# Weights
        #eventweightlumi = self.Leq * event.lheweight * event.btagweight #event.puweight
	eventweightlumi = self.Leq * event.genWeight

	# Fill the branches
	self.out.fillBranch("eventweightlumi", eventweightlumi) 

	return True	

#        electrons = Collection(event, "Electron")
#        muons = Collection(event, "Muon")
#        jets = Collection(event, "Jet")
#        eventSum = TLorentzVector()
#        for lep in muons :
#            eventSum += lep.p4()
#        for lep in electrons :
#            eventSum += lep.p4()
#        for j in filter(self.jetSel,jets):
#            eventSum += j.p4()
#        self.out.fillBranch("EventMass",eventSum.M())
#        return True


# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

WeightConstr = lambda : WeightProducer()

