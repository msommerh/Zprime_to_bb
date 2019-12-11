from ROOT import TFile, TTree, TLorentzVector, TObject, TH1, TH1D, TF1, TH1F
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from TreeProducerCommon import TreeProducerCommon
#from PileupWeightTool import PileupWeightTool
import math

class TreeProducerAcceptance(TreeProducerCommon):
    """Class to create a custom output file & tree; as well as create and contain branches."""
    
    def __init__(self, name, isMC=False, year=2016):
        
        print 'TreeProducerZprimetobb is called', name
        if not isMC:
            print "only defined for MC samples"
            import sys
            sys.exit()
        self.name       = name
        self.outputfile = TFile(name, 'RECREATE')
        #self.tree       = TTree('tree','tree')
        self.year       = year

        self.passing = TH1F('passing', 'passing', 1,0,1)
        self.all_events = TH1F('all_events', 'all_events',1,0,1)
 
    def endJob(self):
        self.outputfile.Write()
        self.outputfile.Close()


class AcceptanceProducer(Module):
    """Simple module to test postprocessing."""
    
    def __init__(self, name, isMC=False, year=2016, **kwargs):
        self.name = name
        self.isMC       = isMC     
        print "isMC =", self.isMC 
        self.year       = year
        self.out  = TreeProducerAcceptance(name, isMC=self.isMC, year=self.year)

    def beginJob(self):
        print "--- beginJob ---"
        pass
        
    def endJob(self):
        print "--- endJob ---"
        self.out.endJob()
        
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
        
    def analyze(self, event):
        """Process event, return True (go to next module) or False (fail, go to next event)."""
      
        GenWeight = -1. if event.genWeight<0 else 1.
        self.out.all_events.Fill(0.)

        ## loop over genparticles and identify the two bs coming from the Z'
        genB1 = -1
        genB2 = -1
        for i in range(event.nGenPart):
            #print
            #print "particle nr", i
            #print "pdgId =", event.GenPart_pdgId[i]
            #print "GenPart_genPartIdxMother =", event.GenPart_genPartIdxMother[i]
            if abs(event.GenPart_pdgId[i]) == 5 and event.GenPart_genPartIdxMother[i] != -1:
                #print "B found!"
                #print "nGenPart =", event.nGenPart
                #print "GenPart_genPartIdxMother =",event.GenPart_genPartIdxMother[i]
                #print "GenPart_pdgId[event.GenPart_genPartIdxMother[i]] =", event.GenPart_pdgId[event.GenPart_genPartIdxMother[i]]
                if genB1==-1 and abs(event.GenPart_pdgId[event.GenPart_genPartIdxMother[i]])==9000001:
                    genB1=i
                elif genB2==-1 and abs(event.GenPart_pdgId[event.GenPart_genPartIdxMother[i]])==9000001:
                    genB2=i
        #print "---------------------------------" 
        #print "genB1 =", genB1
        #print "genB2 =", genB2
        #print "---------------------------------" 
 
        if genB1!=-1 and genB2!=-1:
            eta1 = abs(event.GenPart_eta[genB1])
            eta2 = abs(event.GenPart_eta[genB2])
            dEta = abs(event.GenPart_eta[genB1]-event.GenPart_eta[genB2]) 

            ##if passing criteria
            if eta1<2.5 and eta2<2.5 and dEta<1.1:
                self.out.passing.Fill(0.)   
 
        #self.out.tree.Fill()
        return True
        
