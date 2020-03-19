###
### Module to be used by postprocessors/Zprime_to_bb.py.
###

from ROOT import TFile, TTree, TLorentzVector, TObject, TH1, TH1D, TF1, TH1F
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from TreeProducerCommon import TreeProducerCommon
import ROOT
#from PileupWeightTool import PileupWeightTool
import math

class TreeProducerDijetMass(TreeProducerCommon):
    """Class to create a custom output file & tree; as well as create and contain branches."""
    
    def __init__(self, name, isMC=False, year=2016):
        
        print 'TreeProducerDijetMass is called', name
        self.name       = name
        self.outputfile = TFile(name, 'RECREATE')
        self.tree       = TTree('tree','tree')
        self.year       = year

        self.events = TH1F('Events', 'Events', 1,0,1)
 
        self.addBranch('njets'          , int)
        self.addBranch('jid_1'          , int)
        self.addBranch('jid_2'          , int)
       
        self.addBranch('jj_mass'        , float)
        self.addBranch('jj_mass_lepcorr', float)
        self.addBranch('jj_mass_metcorr', float)
        self.addBranch('jj_mass_widejet', float)
        self.addBranch('jj_deltaEta_widejet', float)
        self.addBranch('jj_deltaEta'    , float)
        self.addBranch('nelectrons'         , int)
        self.addBranch('nmuons'         , int)
        self.addBranch('fatjetmass_1'     , float)
        self.addBranch('fatjetmass_2'     , float)

        self.addBranch('HLT_AK8PFJet500'                , int) 
        self.addBranch('HLT_PFJet500'                   , int)
        self.addBranch('HLT_CaloJet500_NoJetID'         , int)
        self.addBranch('HLT_PFHT900'                    , int)
        self.addBranch('HLT_AK8PFJet550'                , int) 
        self.addBranch('HLT_PFJet550'                   , int)
        self.addBranch('HLT_CaloJet550_NoJetID'         , int)
        self.addBranch('HLT_PFHT1050'                   , int)

        self.addBranch('isMC'                           , int)

    def endJob(self):
        self.outputfile.Write()
        self.outputfile.Close()


class DijetMassProducer(Module):
    """Simple module to test postprocessing."""
    
    def __init__(self, name, isMC=False, year=2016, **kwargs):
        self.name = name
        self.isMC       = isMC     
        print "isMC =", self.isMC 
        self.year       = year
        self.out  = TreeProducerDijetMass(name, isMC=self.isMC, year=self.year)

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
      
        ## Event filter preselection
        passedMETFilters = False
        try: 
                if event.Flag_goodVertices and event.Flag_globalSuperTightHalo2016Filter and event.Flag_BadPFMuonFilter and event.Flag_EcalDeadCellTriggerPrimitiveFilter and event.Flag_HBHENoiseFilter and event.Flag_HBHENoiseIsoFilter and (self.isMC or event.Flag_eeBadScFilter) and event.Flag_ecalBadCalibFilter: 
                        passedMETFilters = True 
        except: 
                passedMETFilters = False

        if not passedMETFilters: return False

        ## jet order check 
        if event.nJet < 2: return False
        if event.Jet_pt_nom[0]>event.Jet_pt_nom[1]:
            leading1 = 0
            leading2 = 1
        else:
            leading1 = 1
            leading2 = 0
        for ijet in range(event.nJet)[2:]:
            if event.Jet_pt_nom[ijet] > event.Jet_pt_nom[leading1]: 
                leading2=leading1
                leading1=ijet
            elif event.Jet_pt_nom[ijet] > event.Jet_pt_nom[leading2]: 
                leading2=ijet

        ## Loop over Jets
        jetIds = [ ]
        jetHT = 0.
        for ijet in range(event.nJet):
            if event.Jet_pt_nom[ijet] < 30: continue
            if abs(event.Jet_eta[ijet]) > 2.5: continue
            if event.Jet_jetId[ijet]<6: continue                                                    
            jetIds.append(ijet)
            jetHT += event.Jet_pt_nom[ijet]

        ## Jet-based event selections
        if len(jetIds)<2: return False
        
        ## Compute dijet quantities
        j1_p4 = TLorentzVector()
        j1_p4.SetPtEtaPhiM(event.Jet_pt_nom[jetIds[0]], event.Jet_eta[jetIds[0]], event.Jet_phi[jetIds[0]], event.Jet_mass_nom[jetIds[0]])
        j2_p4 = TLorentzVector()
        j2_p4.SetPtEtaPhiM(event.Jet_pt_nom[jetIds[1]], event.Jet_eta[jetIds[1]], event.Jet_phi[jetIds[1]], event.Jet_mass_nom[jetIds[1]])
        self.out.jj_mass[0]       = (j1_p4+j2_p4).M()
        self.out.jj_deltaEta[0]   = abs(event.Jet_eta[jetIds[0]]-event.Jet_eta[jetIds[1]])
        
        ## Dijet-based event selections
        if self.out.jj_mass[0] < 800: return False  # will need to change this when deriving the trigger efficiency
        
        j1_p4_lepcorr = j1_p4 * (1. + event.Jet_chEmEF[jetIds[0]]+event.Jet_muEF[jetIds[0]])
        j2_p4_lepcorr = j2_p4 * (1. + event.Jet_chEmEF[jetIds[1]]+event.Jet_muEF[jetIds[1]])
        self.out.jj_mass_lepcorr[0] = (j1_p4_lepcorr+j2_p4_lepcorr).M()
        
        met_p4 = TLorentzVector()
        met_p4.SetPtEtaPhiM(event.MET_pt_nom, 0., event.MET_phi, 0.)
        j1_p4_metcorr = j1_p4 * (1. + event.MET_pt_nom/j1_p4.Pt() * math.cos(j1_p4.DeltaPhi(met_p4)+3.1415))
        j2_p4_metcorr = j2_p4 * (1. + event.MET_pt_nom/j2_p4.Pt() * math.cos(j2_p4.DeltaPhi(met_p4)+3.1415))
        self.out.jj_mass_metcorr[0] = (j1_p4_metcorr+j2_p4_metcorr).M()
        
        wj1_p4 = j1_p4
        wj2_p4 = j2_p4
        for ijet in range(event.nJet):
            if ijet == jetIds[0] or ijet == jetIds[1]: continue
            if event.Jet_pt_nom[ijet] < 30 or abs(event.Jet_eta[ijet]) > 2.5: continue
            if event.Jet_jetId[ijet]<6: continue                                                    
            j_p4 = TLorentzVector()
            j_p4.SetPtEtaPhiM(event.Jet_pt_nom[ijet], event.Jet_eta[ijet], event.Jet_phi[ijet], event.Jet_mass_nom[ijet])
            if j1_p4.DeltaR(j_p4) < 1.1: wj1_p4 += j_p4
            if j2_p4.DeltaR(j_p4) < 1.1: wj2_p4 += j_p4
        self.out.jj_mass_widejet[0] = (wj1_p4+wj2_p4).M()
        self.out.jj_deltaEta_widejet[0]   = abs(wj1_p4.Eta() - wj2_p4.Eta())
        
        nIsoElectrons = 0.
        for iel in range(event.nElectron):
            if event.Electron_pt[iel] > 50. and abs(event.Electron_eta[iel]) < 2.5 and event.Electron_cutBased[iel] >= 2: nIsoElectrons += 1

        nIsoMuons = 0.
        for imu in range(event.nMuon):
            if event.Muon_pt[imu] > 50. and abs(event.Muon_eta[imu]) < 2.4 and event.Muon_highPtId[imu]>=2 and event.Muon_tkRelIso[imu]<0.1: nIsoMuons += 1
       
        nLooseMuons1, nLooseMuons2 = 0, 0 
        ptMuons1, ptMuons2 = 0., 0.
        if event.Jet_muonIdx1[jetIds[0]] >=0 and event.Muon_looseId[event.Jet_muonIdx1[jetIds[0]]]:
            nLooseMuons1 += 1 
            ptMuons1 += event.Muon_pt[event.Jet_muonIdx1[jetIds[0]]]
        if event.Jet_muonIdx2[jetIds[0]] >=0 and event.Muon_looseId[event.Jet_muonIdx2[jetIds[0]]]:
            nLooseMuons1 += 1  
            ptMuons1 += event.Muon_pt[event.Jet_muonIdx2[jetIds[0]]]
        if event.Jet_muonIdx1[jetIds[1]] >=0 and event.Muon_looseId[event.Jet_muonIdx1[jetIds[1]]]: 
            nLooseMuons2 += 1  
            ptMuons2 += event.Muon_pt[event.Jet_muonIdx1[jetIds[1]]]
        if event.Jet_muonIdx2[jetIds[1]] >=0 and event.Muon_looseId[event.Jet_muonIdx2[jetIds[1]]]: 
            nLooseMuons2 += 1  
            ptMuons2 += event.Muon_pt[event.Jet_muonIdx2[jetIds[1]]]
        
        ptRel1, ptRel2 = 0., 0.
        if event.Jet_muonIdx1[jetIds[0]] >=0: ptRel1 = event.Muon_jetPtRelv2[event.Jet_muonIdx1[jetIds[0]]]
        if event.Jet_muonIdx1[jetIds[1]] >=0: ptRel2 = event.Muon_jetPtRelv2[event.Jet_muonIdx1[jetIds[1]]]

        ## Fill jet branches
        self.out.njets[0]       = len(jetIds)
        self.out.jid_1[0] = event.Jet_jetId[jetIds[0]]        
        self.out.jid_2[0] = event.Jet_jetId[jetIds[1]]        
        #self.out.MET_over_SumEt[0] = event.MET_pt/jetHT
        if event.nFatJet >= 1 and event.FatJet_pt[0] > 200.:
            self.out.fatjetmass_1[0] = event.FatJet_msoftdrop[0]
        if event.nFatJet >= 2 and event.FatJet_pt[1] > 200.:
            self.out.fatjetmass_2[0] = event.FatJet_msoftdrop[1]
        self.out.nelectrons[0] = nIsoElectrons
        self.out.nmuons[0] = nIsoMuons

        ## fill trigger branches (different years have different triggers 500<->550, 900<->1050)
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

        self.out.isMC[0] = int(self.isMC)

        self.out.tree.Fill()
        return True
        
