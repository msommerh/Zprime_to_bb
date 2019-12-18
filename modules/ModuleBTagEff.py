import ROOT
from ROOT import TFile, TTree, TLorentzVector, TObject, TH1, TH1D, TF1, TH1F
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

from TreeProducerCommon import TreeProducerCommon
from BTaggingTool import BTagWeightTool, BTagWPs

class TreeProducerBTagEff(TreeProducerCommon):
    """Class to create a custom output file & tree; as well as create and contain branches."""

    def __init__(self, name):

        print 'TreeProducerBTagEff is called', name
        self.name       = name
        self.outputfile = TFile(name, 'RECREATE')
        print "done with initializing the TreeProducer"

    def endJob(self):
        self.outputfile.Write()
        self.outputfile.Close()

class bTagEffProducer(Module):

    def __init__(self, name, isMC=False, year='2016', **kwargs):
       
        self.isMC       = isMC
        print "isMC =", self.isMC
        self.year       = year
 
        self.out = TreeProducerBTagEff(name)
        if self.isMC:
            print "initializing BTagWeightTool"
            self.btagToolAK4_deep = BTagWeightTool('DeepJet','AK4','medium',sigma='central',channel='bb',year=int(self.year))
            #self.btagToolAK4_deep_up = BTagWeightTool('DeepJet','AK4','medium',sigma='up',channel='bb',year=int(self.year))
            #self.btagToolAK4_deep_down = BTagWeightTool('DeepJet','AK4','medium',sigma='down',channel='bb',year=int(self.year))
            print "BTagWeightTool initialized"

        self.lumi       = 1.
        if self.year == '2016':
                self.lumi = 35920.
                self.btagLoose = 0.0614
                self.btagMedium = 0.3093
                self.btagTight = 0.7221
        elif self.year == '2017':
                self.lumi = 41530.
                self.btagLoose = 0.0521
                self.btagMedium = 0.3033
                self.btagTight = 0.7489
        elif self.year == '2018':
                self.lumi = 59740.
                self.btagLoose = 0.0494
                self.btagMedium = 0.2770
                self.btagTight = 0.7264
        else:
                print "Unknown year!!!! Abort module!!!"
                import sys
                sys.exit()


    def beginJob(self):
        print "--- beginJob ---"
        pass

    def endJob(self):
        if self.isMC:
            self.btagToolAK4_deep.setDirectory(self.out.outputfile,'AK4btag_deep')
        self.out.outputfile.Write()
        self.out.outputfile.Close()

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        print "--- beginFile ---"

        self.sample = inputFile.GetName().replace(".root","")
        self.sample = self.sample.replace("root://xrootd-cms.infn.it/", "")
        self.sample = self.sample.replace("root://cms-xrd-global.cern.ch/", "")
        self.sample = self.sample[1:].replace("/", "_")

        print "--- end of beginFile ---"
        pass

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):     
        print "--- endFile ---"
        pass
        
    def fillBranches(self,event):
        pass

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
           
        ## Event filter preselection
        passedMETFilters = False
        try:
                if event.Flag_goodVertices and event.Flag_globalSuperTightHalo2016Filter and event.Flag_BadPFMuonFilter and event.Flag_EcalDeadCellTriggerPrimitiveFilter and event.Flag_HBHENoiseFilter and event.Flag_HBHENoiseIsoFilter and (self.isMC or event.Flag_eeBadScFilter) and event.Flag_ecalBadCalibFilter:
                        passedMETFilters = True
        except:
                passedMETFilters = False

        if not passedMETFilters: return False
 
        if event.nJet < 2: return False

        jetIds = [ ]
        for ijet in range(event.nJet):
            if event.Jet_pt[ijet] < 30: continue
            if abs(event.Jet_eta[ijet]) > 2.5: continue
            jetIds.append(ijet)

        if len(jetIds)<2: return False

        self.btagToolAK4_deep.fillEfficiencies(event,jetIds)

        return True
