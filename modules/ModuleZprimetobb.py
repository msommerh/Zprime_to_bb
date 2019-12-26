###
### Module to be used by postprocessors/Zprime_to_bb.py.
###

from ROOT import TFile, TTree, TLorentzVector, TObject, TH1, TH1D, TF1, TH1F
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from TreeProducerCommon import TreeProducerCommon
#from PileupWeightTool import PileupWeightTool
import math

class TreeProducerZprimetobb(TreeProducerCommon):
    """Class to create a custom output file & tree; as well as create and contain branches."""
    
    def __init__(self, name, isMC=False, year=2016):
        
        print 'TreeProducerZprimetobb is called', name
        self.name       = name
        self.outputfile = TFile(name, 'RECREATE')
        self.tree       = TTree('tree','tree')
        self.year       = year

        self.events = TH1F('Events', 'Events', 1,0,1)
        self.pileup = TH1F('pileup', 'pileup', 100,0,100)  ## necessary?
        self.original = TH1F('Original', 'Original',1,0,1) ## necessary?
 
        self.addBranch('njets'          , int)
        self.addBranch('jpt_1'          , float)
        self.addBranch('jeta_1'         , float)
        self.addBranch('jphi_1'         , float)
        self.addBranch('jmass_1'        , float)
        #self.addBranch('jCSV_1'         , float)
        #self.addBranch('jdeepCSV_1'     , float)
        self.addBranch('jdeepFlavour_1' , float)
        self.addBranch('jchf_1'         , float)
        self.addBranch('jnhf_1'         , float)
        self.addBranch('jcef_1'         , float)
        self.addBranch('jnef_1'         , float)
        self.addBranch('jmuf_1'         , float)
        self.addBranch('jmuonpt_1'      , float)
        self.addBranch('jptRel_1'       , float)
        self.addBranch('jnelectrons_1'  , int)
        self.addBranch('jnmuons_1'      , int)
        self.addBranch('jflavour_1'     , int)
        self.addBranch('jmask_1'        , bool)
        self.addBranch('jid_1'          , int)
        self.addBranch('jbtag_WP_1'     , int)
        
        self.addBranch('jpt_2'          , float)
        self.addBranch('jeta_2'         , float)
        self.addBranch('jphi_2'         , float)
        self.addBranch('jmass_2'        , float)
        #self.addBranch('jCSV_2'         , float)
        #self.addBranch('jdeepCSV_2'     , float)
        self.addBranch('jdeepFlavour_2' , float)
        self.addBranch('jchf_2'         , float)
        self.addBranch('jnhf_2'         , float)
        self.addBranch('jcef_2'         , float)
        self.addBranch('jnef_2'         , float)
        self.addBranch('jmuf_2'         , float)
        self.addBranch('jmuonpt_2'      , float)
        self.addBranch('jptRel_2'       , float)
        self.addBranch('jnelectrons_2'  , int)
        self.addBranch('jnmuons_2'      , int)
        self.addBranch('jflavour_2'     , int)
        self.addBranch('jmask_2'        , bool)
        self.addBranch('jid_2'          , int)
        self.addBranch('jbtag_WP_2'     , int)
       
        self.addBranch('jsorted'        , int)
        self.addBranch('jj_mass'        , float)
        self.addBranch('jj_mass_lepcorr', float)
        self.addBranch('jj_mass_metcorr', float)
        self.addBranch('jj_mass_widejet', float)
        self.addBranch('jj_deltaEta_widejet', float)
        self.addBranch('jj_deltaEta'    , float)
        self.addBranch('jj_deltaPhi'    , float)
        self.addBranch('nelectrons'     , int)
        self.addBranch('nmuons'         , int)
        self.addBranch('nbtagLoose'     , int)
        self.addBranch('nbtagMedium'    , int)
        self.addBranch('nbtagTight'     , int)
        self.addBranch('ptBalance'      , float)
        self.addBranch('HT'             , float)
        self.addBranch('MET'            , float)
        self.addBranch('fatjetmass_1'   , float)
        self.addBranch('fatjetmass_2'   , float)
#        self.addBranch('MET_over_SumEt' , float)
#        self.addBranch('jjetsId_1'      , int)
#        self.addBranch('jjetsId_2'      , int)

        self.addBranch('HLT_AK8PFJet500'                , int) 
        self.addBranch('HLT_PFJet500'                   , int)
        self.addBranch('HLT_CaloJet500_NoJetID'         , int)
        self.addBranch('HLT_PFHT900'                    , int)
        self.addBranch('HLT_AK8PFJet550'                , int) 
        self.addBranch('HLT_PFJet550'                   , int)
        self.addBranch('HLT_CaloJet550_NoJetID'         , int)
        self.addBranch('HLT_PFHT1050'                   , int)
        self.addBranch('HLT_DoublePFJets128MaxDeta1p6_DoubleCaloBTagDeepCSV_p71' , int)
        self.addBranch('HLT_DoublePFJets116MaxDeta1p6_DoubleCaloBTagDeepCSV_p71' , int)
        self.addBranch('HLT_DoublePFJets40_CaloBTagDeepCSV_p71'                  , int)
        self.addBranch('HLT_DoublePFJets100_CaloBTagDeepCSV_p71'                  , int)
        self.addBranch('HLT_DoublePFJets200_CaloBTagDeepCSV_p71'                 , int)
        self.addBranch('HLT_DoublePFJets350_CaloBTagDeepCSV_p71'                 , int)

        self.addBranch('btagWeight_DeepCSVB'            , float)
        self.addBranch('LHEWeight_originalXWGTUP'       , float)
        self.addBranch('LHEReweightingWeight'           , float)
        self.addBranch('LHEScaleWeight'                 , float)
        self.addBranch('PSWeight'                       , float)
        #self.addBranch('genWeight'                     , float)
        self.addBranch('GenWeight'                      , float) #new weight that is either -1. or +1.
        self.addBranch('PUWeight'                       , float)
        #self.addBranch('eventweightlumi'               , float)
        self.addBranch('isMC'                           , int)

        if 'signal' in self.name.lower():
            self.addBranch('BTagAK4Weight_deepJet'       , float)
            self.addBranch('BTagAK4Weight_deepJet_up'    , float)
            self.addBranch('BTagAK4Weight_deepJet_down'  , float)

    def endJob(self):
        self.outputfile.Write()
        self.outputfile.Close()


class ZprimetobbProducer(Module):
    """Simple module to test postprocessing."""
    
    def __init__(self, name, isMC=False, year=2016, **kwargs):
        self.name = name
        self.isMC       = isMC     
        print "isMC =", self.isMC 
        self.year       = year
        self.out  = TreeProducerZprimetobb(name, isMC=self.isMC, year=self.year)
#        if self.isMC: self.puTool = PileupWeightTool(year =year)

        if 'signal' in self.name.lower():
            from BTaggingTool import BTagWeightTool, BTagWPs
            self.btagToolAK4_deepJet = BTagWeightTool('DeepJet','AK4','medium',sigma='central',channel='bb',year=year) 
            self.btagToolAK4_deepJet_up = BTagWeightTool('DeepJet','AK4','medium',sigma='up',channel='bb',year=year)
            self.btagToolAK4_deepJet_down = BTagWeightTool('DeepJet','AK4','medium',sigma='down',channel='bb',year=year)


        self.lumi       = 1.
        if self.year == 2016:
                self.lumi = 35920.
                self.btagLoose =  0.0614
                self.btagMedium = 0.3093
                self.btagTight =  0.7221
        elif self.year == 2017:
                self.lumi = 41530.
                self.btagLoose =  0.0521
                self.btagMedium = 0.3033
                self.btagTight =  0.7489
        elif self.year == 2018:
                self.lumi = 59740.
                self.btagLoose =  0.0494
                self.btagMedium = 0.2770
                self.btagTight =  0.7264
        else:
                print "Unknown year!!!! Abort module!!!"
                import sys
                sys.exit()
    
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
      
        if self.isMC:
                GenWeight = -1. if event.genWeight<0 else 1.
                PUWeight = 1. #self.puTool.getWeight(event.Pileup_nTrueInt)
                if 'signal' in self.name.lower():                                              ## new for a test FIXME FIXME

                    jetIds = [ ]
                    for ijet in range(event.nJet):
                        if event.Jet_pt[ijet] < 30: continue
                        if abs(event.Jet_eta[ijet]) > 2.5: continue
                        jetIds.append(ijet)

                    BTagAK4Weight_deepJet       = self.btagToolAK4_deepJet.getWeight(event,jetIds)  
                    BTagAK4Weight_deepJet_up    = self.btagToolAK4_deepJet_up.getWeight(event,jetIds)
                    BTagAK4Weight_deepJet_down  = self.btagToolAK4_deepJet_down.getWeight(event,jetIds)

                    self.out.events.Fill(0., BTagAK4Weight_deepJet) 
                else:
                    self.out.events.Fill(0., GenWeight)
                try:
                    LHEWeight = event.LHEWeight_originalXWGTUP
                    self.out.original.Fill(0.,LHEWeight)
                except:
                    self.out.original.Fill(0.,-1.)
                self.out.pileup.Fill(event.Pileup_nTrueInt)
 
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
        if event.Jet_pt[0]>event.Jet_pt[1]:
            leading1 = 0
            leading2 = 1
        else:
            leading1 = 1
            leading2 = 0
        for ijet in range(event.nJet)[2:]:
            if event.Jet_pt[ijet] > event.Jet_pt[leading1]: 
                leading2=leading1
                leading1=ijet
            elif event.Jet_pt[ijet] > event.Jet_pt[leading2]: 
                leading2=ijet

        ## Loop over Jets
        jetIds = [ ]
        jetHT = 0.
        jetBTagLoose, jetBTagMedium, jetBTagTight = 0, 0, 0
        for ijet in range(event.nJet):
            if event.Jet_pt[ijet] < 30: continue
            if abs(event.Jet_eta[ijet]) > 2.5: continue
            jetIds.append(ijet)
            jetHT += event.Jet_pt[ijet]
            if event.Jet_btagDeepFlavB[ijet] >= self.btagLoose: jetBTagLoose += 1
            if event.Jet_btagDeepFlavB[ijet] >= self.btagMedium: jetBTagMedium += 1
            if event.Jet_btagDeepFlavB[ijet] >= self.btagTight: jetBTagTight += 1
            

        ## Jet-based event selections
        if len(jetIds)<2: return False
        #if event.Jet_jetId[jetIds[0]] < 2: return False
        #if event.Jet_jetId[jetIds[1]] < 2: return False
        #if event.MET_pt/jetHT > 0.5: return False      

        
        ### evaluate BTag weights   ## put in beginning of analyze in order to get the weight into the normalization
        #if 'signal' in self.name.lower(): 
        #    BTagAK4Weight_deepJet       = self.btagToolAK4_deepJet.getWeight(event,jetIds)  
        #    BTagAK4Weight_deepJet_up    = self.btagToolAK4_deepJet_up.getWeight(event,jetIds)
        #    BTagAK4Weight_deepJet_down  = self.btagToolAK4_deepJet_down.getWeight(event,jetIds)


        ## Compute dijet quantities
        j1_p4 = TLorentzVector()
        j1_p4.SetPtEtaPhiM(event.Jet_pt[jetIds[0]], event.Jet_eta[jetIds[0]], event.Jet_phi[jetIds[0]], event.Jet_mass[jetIds[0]])
        j2_p4 = TLorentzVector()
        j2_p4.SetPtEtaPhiM(event.Jet_pt[jetIds[1]], event.Jet_eta[jetIds[1]], event.Jet_phi[jetIds[1]], event.Jet_mass[jetIds[1]])
        self.out.jj_mass[0]       = (j1_p4+j2_p4).M()
        self.out.jj_deltaEta[0]   = abs(event.Jet_eta[jetIds[0]]-event.Jet_eta[jetIds[1]])
        self.out.jj_deltaPhi[0]   = abs(j1_p4.DeltaPhi(j2_p4)) #abs(event.Jet_phi[jetIds[0]]-event.Jet_phi[jetIds[1]]) this does not account for phi jump from 2pi to 0

        
        ## Dijet-based event selections
        if self.out.jj_mass[0] < 800: return False  # will need to change this when deriving the trigger efficiency
        #if self.out.jj_deltaEta[0]>1.1: return False
        
        j1_p4_lepcorr = j1_p4 * (1. + event.Jet_chEmEF[jetIds[0]]+event.Jet_muEF[jetIds[0]])
        j2_p4_lepcorr = j2_p4 * (1. + event.Jet_chEmEF[jetIds[1]]+event.Jet_muEF[jetIds[1]])
        self.out.jj_mass_lepcorr[0] = (j1_p4_lepcorr+j2_p4_lepcorr).M()
        
        met_p4 = TLorentzVector()
        met_p4.SetPtEtaPhiM(event.MET_pt, 0., event.MET_phi, 0.)
        j1_p4_metcorr = j1_p4 * (1. + event.MET_pt/j1_p4.Pt() * math.cos(j1_p4.DeltaPhi(met_p4)+3.1415))
        j2_p4_metcorr = j2_p4 * (1. + event.MET_pt/j2_p4.Pt() * math.cos(j2_p4.DeltaPhi(met_p4)+3.1415))
        self.out.jj_mass_metcorr[0] = (j1_p4_metcorr+j2_p4_metcorr).M()
        
        wj1_p4 = j1_p4
        wj2_p4 = j2_p4
        for ijet in range(event.nJet):
            if ijet == jetIds[0] or ijet == jetIds[1]: continue
            if event.Jet_pt[ijet] < 30 or abs(event.Jet_eta[ijet]) > 2.5: continue
            j_p4 = TLorentzVector()
            j_p4.SetPtEtaPhiM(event.Jet_pt[ijet], event.Jet_eta[ijet], event.Jet_phi[ijet], event.Jet_mass[ijet])
            if j1_p4.DeltaR(j_p4) < 1.1: wj1_p4 += j_p4
            if j2_p4.DeltaR(j_p4) < 1.1: wj2_p4 += j_p4
        self.out.jj_mass_widejet[0] = (wj1_p4+wj2_p4).M()
        self.out.jj_deltaEta_widejet[0]   = abs(wj1_p4.Eta() - wj2_p4.Eta())
        
        
        fatjetMass = 0.
        if event.nFatJet > 0: fatjetMass = event.FatJet_msoftdrop[0]
        if event.nFatJet > 1: secondaryFatjetMass = event.FatJet_msoftdrop[1]
        
        nIsoElectrons = 0.
        for iel in range(event.nElectron):
            if event.Electron_pt[iel] > 20. and abs(event.Electron_eta[iel]) < 2.5 and event.Electron_cutBased[iel] >= 1: nIsoElectrons += 1

        nIsoMuons = 0.
        for imu in range(event.nMuon):
            if event.Muon_pt[imu] > 20. and abs(event.Muon_eta[imu]) < 2.4 and event.Muon_looseId[imu] and event.Muon_pfIsoId[imu] >= 2: nIsoMuons += 1
        
        ptMuons1, ptMuons2 = 0., 0.
        if event.Jet_muonIdx1[jetIds[0]] >=0 and event.Muon_looseId[event.Jet_muonIdx1[jetIds[0]]]: ptMuons1 += event.Muon_pt[event.Jet_muonIdx1[jetIds[0]]]
        if event.Jet_muonIdx2[jetIds[0]] >=0 and event.Muon_looseId[event.Jet_muonIdx2[jetIds[0]]]: ptMuons1 += event.Muon_pt[event.Jet_muonIdx2[jetIds[0]]]
        if event.Jet_muonIdx1[jetIds[1]] >=0 and event.Muon_looseId[event.Jet_muonIdx1[jetIds[1]]]: ptMuons2 += event.Muon_pt[event.Jet_muonIdx1[jetIds[1]]]
        if event.Jet_muonIdx2[jetIds[1]] >=0 and event.Muon_looseId[event.Jet_muonIdx2[jetIds[1]]]: ptMuons2 += event.Muon_pt[event.Jet_muonIdx2[jetIds[1]]]
        
        ptRel1, ptRel2 = 0., 0.
        if event.Jet_muonIdx1[jetIds[0]] >=0: ptRel1 = event.Muon_jetPtRelv2[event.Jet_muonIdx1[jetIds[0]]]
        if event.Jet_muonIdx1[jetIds[1]] >=0: ptRel2 = event.Muon_jetPtRelv2[event.Jet_muonIdx1[jetIds[1]]]

        ## Fill jet branches
        self.out.njets[0]         = len(jetIds)
        
        self.out.jpt_1[0]       = event.Jet_pt[jetIds[0]]
        self.out.jeta_1[0]      = event.Jet_eta[jetIds[0]]
        self.out.jphi_1[0]      = event.Jet_phi[jetIds[0]]
        self.out.jmass_1[0]     = event.Jet_mass[jetIds[0]]
        #self.out.jCSV_1[0]      = event.Jet_btagCSVV2[jetIds[0]]
        #self.out.jdeepCSV_1[0]  = event.Jet_btagDeepB[jetIds[0]]
        self.out.jdeepFlavour_1[0]  = event.Jet_btagDeepFlavB[jetIds[0]]
        self.out.jchf_1[0] = event.Jet_chHEF[jetIds[0]]
        self.out.jnhf_1[0] = event.Jet_neHEF[jetIds[0]]
        self.out.jcef_1[0] = event.Jet_chEmEF[jetIds[0]]
        self.out.jnef_1[0] = event.Jet_neEmEF[jetIds[0]]
        self.out.jmuf_1[0] = event.Jet_muEF[jetIds[0]]
        self.out.jmuonpt_1[0] = ptMuons1
        self.out.jptRel_1[0] = ptRel1
        self.out.jnelectrons_1[0] = event.Jet_nElectrons[jetIds[0]]
        self.out.jnmuons_1[0] = event.Jet_nMuons[jetIds[0]]
        if self.isMC: 
            self.out.jflavour_1[0] = event.Jet_hadronFlavour[jetIds[0]]
        else:
            self.out.jflavour_1[0] = -1
        self.out.jmask_1[0] = event.Jet_cleanmask[jetIds[0]]
        self.out.jid_1[0] = event.Jet_jetId[jetIds[0]]        

        self.out.jpt_2[0]       = event.Jet_pt[jetIds[1]]
        self.out.jeta_2[0]      = event.Jet_eta[jetIds[1]]
        self.out.jphi_2[0]      = event.Jet_phi[jetIds[1]]
        self.out.jmass_2[0]     = event.Jet_mass[jetIds[1]]
        #self.out.jCSV_2[0]      = event.Jet_btagCSVV2[jetIds[1]]
        #self.out.jdeepCSV_2[0]  = event.Jet_btagDeepB[jetIds[1]]
        self.out.jdeepFlavour_2[0]  = event.Jet_btagDeepFlavB[jetIds[1]]
        self.out.jchf_2[0] = event.Jet_chHEF[jetIds[1]]
        self.out.jnhf_2[0] = event.Jet_neHEF[jetIds[1]]
        self.out.jcef_2[0] = event.Jet_chEmEF[jetIds[1]]
        self.out.jnef_2[0] = event.Jet_neEmEF[jetIds[1]]
        self.out.jmuf_2[0] = event.Jet_muEF[jetIds[1]]
        self.out.jmuonpt_2[0] = ptMuons2
        self.out.jptRel_2[0] = ptRel2
        self.out.jnelectrons_2[0] = event.Jet_nElectrons[jetIds[1]]
        self.out.jnmuons_2[0] = event.Jet_nMuons[jetIds[1]]
        if self.isMC:
            self.out.jflavour_2[0] = event.Jet_hadronFlavour[jetIds[1]]
        else:
            self.out.jflavour_2[0] = -1
        self.out.jmask_2[0] = event.Jet_cleanmask[jetIds[1]]
        self.out.jid_2[0] = event.Jet_jetId[jetIds[1]]        

        self.out.jsorted[0]       = 0
        if leading1==0 and leading2==1: self.out.jsorted[0] = 1

        #self.out.MET_over_SumEt[0] = event.MET_pt/jetHT
        self.out.fatjetmass_1[0] = fatjetMass
        if event.nFatJet > 1: self.out.fatjetmass_2[0] = secondaryFatjetMass
        self.out.ptBalance[0] = (event.Jet_pt[jetIds[0]] - event.Jet_pt[jetIds[1]])/(event.Jet_pt[jetIds[0]] + event.Jet_pt[jetIds[1]])
        self.out.HT[0] = jetHT
        self.out.MET[0] = event.MET_pt
        self.out.nelectrons[0] = nIsoElectrons
        self.out.nmuons[0] = nIsoMuons
        self.out.nbtagLoose[0]         = jetBTagLoose
        self.out.nbtagMedium[0]        = jetBTagMedium
        self.out.nbtagTight[0]         = jetBTagTight

        ## writing the b-tag category directly into the n-tuple. 0:untagged, 1:loose, 2:medium, 3:tight
        self.out.jbtag_WP_1[0]         = 0
        if event.Jet_btagDeepFlavB[jetIds[0]] > self.btagTight:
            self.out.jbtag_WP_1[0]     = 3
        elif event.Jet_btagDeepFlavB[jetIds[0]] > self.btagMedium:
            self.out.jbtag_WP_1[0]     = 2
        elif event.Jet_btagDeepFlavB[jetIds[0]] > self.btagLoose:
            self.out.jbtag_WP_1[0]     = 1
        self.out.jbtag_WP_2[0]         = 0
        if event.Jet_btagDeepFlavB[jetIds[1]] > self.btagTight:
            self.out.jbtag_WP_2[0]     = 3
        elif event.Jet_btagDeepFlavB[jetIds[1]] > self.btagMedium:
            self.out.jbtag_WP_2[0]     = 2
        elif event.Jet_btagDeepFlavB[jetIds[1]] > self.btagLoose:
            self.out.jbtag_WP_2[0]     = 1
        
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
        

        ## add weights
        try:
                self.out.btagWeight_DeepCSVB[0]         = event.btagWeight_DeepCSVB
        except:
                self.out.btagWeight_DeepCSVB[0]         = -100.                         
        try:
                self.out.LHEWeight_originalXWGTUP[0]    = event.LHEWeight_originalXWGTUP
        except:
                self.out.LHEWeight_originalXWGTUP[0]    = -100.         
        try:
                self.out.LHEReweightingWeight[0]        = event.LHEReweightingWeight
        except:
                self.out.LHEReweightingWeight[0]        = -100.      
        try:
                self.out.LHEScaleWeight[0]              = event.LHEScaleWeight
        except:
                self.out.LHEScaleWeight[0]              = -100.      
        try:
                self.out.PSWeight[0]                    = event.PSWeight
        except:
                self.out.PSWeight[0]                    = -100.      
        #try:
        #       self.out.genWeight[0]                   = event.genWeight
        #except:
        #       self.out.genWeight[0]                   = -100.         
        if self.isMC:
                self.out.GenWeight[0]                   = GenWeight
                self.out.PUWeight[0]                    = PUWeight
        else:
                self.out.GenWeight[0]                   = 1.
                self.out.PUWeight[0]                    = 1.
       
        
        if 'signal' in self.name.lower():
            self.out.BTagAK4Weight_deepJet[0]           =  BTagAK4Weight_deepJet        
            self.out.BTagAK4Weight_deepJet_up[0]        =  BTagAK4Weight_deepJet_up  
            self.out.BTagAK4Weight_deepJet_down[0]      =  BTagAK4Weight_deepJet_down
 
        ## event weight lumi
        #eventweightlumi = 1.

        #if self.isMC:
        #       eventweightlumi = self.Leq  #minimalist approach, store the things to be multiplied later separately into nTuple
        #       #eventweightlumi = self.Leq * event.LHEWeight_originalXWGTUP
        #       #eventweightlumi = self.Leq * event.lheweight * event.btagweight #event.puweight
        #self.out.eventweightlumi[0] = eventweightlumi
        self.out.isMC[0] = int(self.isMC)

        self.out.tree.Fill()
        return True
        
