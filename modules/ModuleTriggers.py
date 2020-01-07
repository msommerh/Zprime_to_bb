###
### Module to be used by postprocessors/TriggerEfficiency.py.
###

from ROOT import TFile, TTree, TLorentzVector, TObject, TH1, TH1D, TF1, TH1F
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from TreeProducerCommon import TreeProducerCommon
#from PileupWeightTool import PileupWeightTool
import math

class TreeProducerTriggers(TreeProducerCommon):
    """Class to create a custom output file & tree; as well as create and contain branches."""
    
    def __init__(self, name, isMC=False, year=2016):
        
        print 'TreeProducerTriggers is called', name
        self.name       = name
        self.outputfile = TFile(name, 'RECREATE')
        self.tree       = TTree('tree','tree')
        self.year       = year

        self.addBranch('jj_mass_widejet'                                         , float)
        self.addBranch('jj_deltaEta_widejet'                                     , float)
        self.addBranch('HLT_AK8PFJet500'                                         , int) 
        self.addBranch('HLT_PFJet500'                                            , int)
        self.addBranch('HLT_CaloJet500_NoJetID'                                  , int)
        self.addBranch('HLT_PFHT900'                                             , int)
        self.addBranch('HLT_AK8PFJet550'                                         , int) 
        self.addBranch('HLT_PFJet550'                                            , int)
        self.addBranch('HLT_CaloJet550_NoJetID'                                  , int)
        self.addBranch('HLT_PFHT1050'                                            , int)
        self.addBranch('HLT_DoublePFJets128MaxDeta1p6_DoubleCaloBTagDeepCSV_p71' , int)
        self.addBranch('HLT_DoublePFJets116MaxDeta1p6_DoubleCaloBTagDeepCSV_p71' , int)
        self.addBranch('HLT_DoublePFJets40_CaloBTagDeepCSV_p71'                  , int)
        self.addBranch('HLT_DoublePFJets100_CaloBTagDeepCSV_p71'                 , int)
        self.addBranch('HLT_DoublePFJets200_CaloBTagDeepCSV_p71'                 , int)
        self.addBranch('HLT_DoublePFJets350_CaloBTagDeepCSV_p71'                 , int)

    def endJob(self):
        self.outputfile.Write()
        self.outputfile.Close()


class TriggerProducer(Module):
    """Simple module to test postprocessing."""
    
    def __init__(self, name, isMC=False, year=2016, **kwargs):
        self.name = name
        self.isMC       = isMC     
        print "isMC =", self.isMC 
        self.year       = year
        self.out  = TreeProducerTriggers(name, isMC=self.isMC, year=self.year)
#        if self.isMC: self.puTool = PileupWeightTool(year =year)

    def beginJob(self):
        print "--- beginJob ---"
        pass
        
    def endJob(self):
        print "--- endJob ---"
        self.out.endJob()
        
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):

        self.sample = inputFile.GetName().replace(".root","")
        self.sample = self.sample.replace("root://xrootd-cms.infn.it/", "")
        self.sample = self.sample.replace("root://cms-xrd-global.cern.ch/", "")
        self.sample = self.sample[1:].replace("/", "_")
        pass
        
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
        
    def analyze(self, event):
        """Process event, return True (go to next module) or False (fail, go to next event)."""
      
        ## Event filter preselection
        passedMETFilters = False
        try: 
                if event.Flag_goodVertices and event.Flag_globalSuperTightHalo2016Filter and event.Flag_BadPFMuonFilter and event.Flag_EcalDeadCellTriggerPrimitiveFilter and event.Flag_HBHENoiseFilter and event.Flag_HBHENoiseIsoFilter and (self.isMC or event.Flag_eeBadScFilter) and event.Flag_ecalBadCalibFilter: 
                        passedMETFilters = True 
        except: 
                passedMETFilters = False

        if not passedMETFilters: return False

        ## Muon selection:
    
        if not event.HLT_IsoMu27 or not event.Muon_pt[0]>30 or not event.Muon_tightId[0] or not event.Muon_pfRelIso03_all[0]<0.1: return False
        muon_p4 = TLorentzVector()
        muon_p4.SetPtEtaPhiM(event.Muon_pt[0], event.Muon_eta[0], event.Muon_phi[0], event.Muon_mass[0])

        ## Loop over Jets
        jetIds = [ ]
        for ijet in range(event.nJet):
            if event.Jet_pt[ijet] < 30: continue
            if abs(event.Jet_eta[ijet]) > 2.5: continue
            jetIds.append(ijet)

        ## Jet-based event selections
        if len(jetIds)<2: return False

        ## Compute dijet quantities
        j1_p4 = TLorentzVector()
        j1_p4.SetPtEtaPhiM(event.Jet_pt[jetIds[0]], event.Jet_eta[jetIds[0]], event.Jet_phi[jetIds[0]], event.Jet_mass[jetIds[0]])
        j2_p4 = TLorentzVector()
        j2_p4.SetPtEtaPhiM(event.Jet_pt[jetIds[1]], event.Jet_eta[jetIds[1]], event.Jet_phi[jetIds[1]], event.Jet_mass[jetIds[1]])
        #self.out.jj_mass[0]       = (j1_p4+j2_p4).M()
        #self.out.jj_deltaEta[0]   = abs(event.Jet_eta[jetIds[0]]-event.Jet_eta[jetIds[1]])
        
        wj1_p4 = j1_p4
        wj2_p4 = j2_p4
        for ijet in range(event.nJet):
            if ijet == jetIds[0] or ijet == jetIds[1]: continue
            if event.Jet_pt[ijet] < 30 or abs(event.Jet_eta[ijet]) > 2.5: continue
            j_p4 = TLorentzVector()
            j_p4.SetPtEtaPhiM(event.Jet_pt[ijet], event.Jet_eta[ijet], event.Jet_phi[ijet], event.Jet_mass[ijet])
            if j1_p4.DeltaR(j_p4) < 1.1: wj1_p4 += j_p4
            if j2_p4.DeltaR(j_p4) < 1.1: wj2_p4 += j_p4
    
        if wj1_p4.DeltaR(muon_p4) < 0.4 or wj2_p4.DeltaR(muon_p4) < 0.4: return False

        self.out.jj_mass_widejet[0] = (wj1_p4+wj2_p4).M()
        self.out.jj_deltaEta_widejet[0]   = abs(wj1_p4.Eta() - wj2_p4.Eta())

        if self.out.jj_mass_widejet[0] < 800: return False
        
        #fatjetMass = 0.
        #if event.nFatJet > 0: fatjetMass = event.FatJet_msoftdrop[0]
        #if event.nFatJet > 1: secondaryFatjetMass = event.FatJet_msoftdrop[1]
        
        ## Fill jet branches
        try:
                self.out.HLT_AK8PFJet500[0]             = event.HLT_AK8PFJet500         
        except: 
                self.out.HLT_AK8PFJet500[0]             = -1
        try:
                self.out.HLT_PFJet500[0]                = event.HLT_PFJet500                            
        except:
                self.out.HLT_PFJet500[0]                = -1                            
        try:
                self.out.HLT_CaloJet500_NoJetID[0]      = event.HLT_CaloJet500_NoJetID          
        except:
                self.out.HLT_CaloJet500_NoJetID[0]      = -1    
        try:
                self.out.HLT_PFHT900[0]         = event.HLT_PFHT900             
        except:
                self.out.HLT_PFHT900[0]         = -1                            
        try:
                self.out.HLT_AK8PFJet550[0]             = event.HLT_AK8PFJet550         
        except: 
                self.out.HLT_AK8PFJet550[0]             = -1
        try:
                self.out.HLT_PFJet550[0]                = event.HLT_PFJet550                            
        except:
                self.out.HLT_PFJet550[0]                = -1                            
        try:
                self.out.HLT_CaloJet550_NoJetID[0]      = event.HLT_CaloJet550_NoJetID          
        except:
                self.out.HLT_CaloJet550_NoJetID[0]      = -1    
        try:
                self.out.HLT_PFHT1050[0]                = event.HLT_PFHT1050            
        except:
                self.out.HLT_PFHT1050[0]                = -1                    

        try:
                self.out.HLT_DoublePFJets128MaxDeta1p6_DoubleCaloBTagDeepCSV_p71[0]                = event.HLT_DoublePFJets128MaxDeta1p6_DoubleCaloBTagDeepCSV_p71            
        except:
                self.out.HLT_DoublePFJets128MaxDeta1p6_DoubleCaloBTagDeepCSV_p71[0]                = -1                    
        try:
                self.out.HLT_DoublePFJets116MaxDeta1p6_DoubleCaloBTagDeepCSV_p71[0]                = event.HLT_DoublePFJets116MaxDeta1p6_DoubleCaloBTagDeepCSV_p71            
        except:
                self.out.HLT_DoublePFJets116MaxDeta1p6_DoubleCaloBTagDeepCSV_p71[0]                = -1                    
        
        try:
                self.out.HLT_DoublePFJets40_CaloBTagDeepCSV_p71[0]                = event.HLT_DoublePFJets40_CaloBTagDeepCSV_p71            
        except:
                self.out.HLT_DoublePFJets40_CaloBTagDeepCSV_p71[0]                = -1                    
        try:
                self.out.HLT_DoublePFJets100_CaloBTagDeepCSV_p71[0]                = event.HLT_DoublePFJets100_CaloBTagDeepCSV_p71            
        except:
                self.out.HLT_DoublePFJets100_CaloBTagDeepCSV_p71[0]                = -1                    
        try:
                self.out.HLT_DoublePFJets200_CaloBTagDeepCSV_p71[0]                = event.HLT_DoublePFJets200_CaloBTagDeepCSV_p71            
        except:
                self.out.HLT_DoublePFJets200_CaloBTagDeepCSV_p71[0]                = -1                    
        try:
                self.out.HLT_DoublePFJets350_CaloBTagDeepCSV_p71[0]                = event.HLT_DoublePFJets350_CaloBTagDeepCSV_p71            
        except:
                self.out.HLT_DoublePFJets350_CaloBTagDeepCSV_p71[0]                = -1                    
        
        self.out.tree.Fill()
        return True
        
