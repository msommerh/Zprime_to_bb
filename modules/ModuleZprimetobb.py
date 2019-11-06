from ROOT import TFile, TTree, TLorentzVector, TObject, TH1, TH1D, TF1, TH1F
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from TreeProducerCommon import TreeProducerCommon
from PileupWeightTool import PileupWeightTool

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
 
        self.addBranch('njets'          , float)
        self.addBranch('jpt_1'          , float)
        self.addBranch('jeta_1'         , float)
        self.addBranch('jphi_1'         , float)
        self.addBranch('jmass_1'        , float)
        self.addBranch('jdeepCSV_1'     , float)
        self.addBranch('jdeepFlavour_1' , float)
        self.addBranch('jpt_2'          , float)
        self.addBranch('jeta_2'         , float)
        self.addBranch('jphi_2'         , float)
        self.addBranch('jmass_2'        , float)
        self.addBranch('jdeepCSV_2'     , float)
        self.addBranch('jdeepFlavour_2' , float)
        self.addBranch('jsorted'        , int)
        self.addBranch('jj_mass'        , float)
        self.addBranch('jj_deltaEta'    , float)
        self.addBranch('jj_deltaPhi'    , float)
        self.addBranch('MET_over_SumEt' , float)
        self.addBranch('jjetsId_1'      , int)
        self.addBranch('jjetsId_2'      , int)

        self.addBranch('HLT_AK8PFJet500'                , int) 
        self.addBranch('HLT_PFJet500'                   , int)
        self.addBranch('HLT_CaloJet500_NoJetID'         , int)
        self.addBranch('HLT_PFHT900'                    , int)
        self.addBranch('HLT_AK8PFJet550'                , int) 
        self.addBranch('HLT_PFJet550'                   , int)
        self.addBranch('HLT_CaloJet550_NoJetID'         , int)
        self.addBranch('HLT_PFHT1050'                   , int)

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
        if self.isMC: self.puTool = PileupWeightTool(year =year)

        self.lumi       = 1.
        if self.year == 2016:
                self.lumi = 35920.
        elif self.year == 2017:
                self.lumi = 41530.
        elif self.year == 2018:
                self.lumi = 59740.
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
                PUWeight = self.puTool.getWeight(event.Pileup_nTrueInt)
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
        for ijet in range(event.nJet):
            if event.Jet_pt[ijet] < 30: continue
            if abs(event.Jet_eta[ijet]) > 2.5: continue
            jetIds.append(ijet)
            jetHT += event.Jet_pt[ijet]


        ## Jet-based event selections
        if len(jetIds)<2: return False
        if event.Jet_jetId[jetIds[0]] < 2: return False
        if event.Jet_jetId[jetIds[1]] < 2: return False
        #if event.MET_pt/jetHT > 0.5: return False      

        ## Compute dijet quantities
        j1_p4 = TLorentzVector()
        j1_p4.SetPtEtaPhiM(event.Jet_pt[jetIds[0]], event.Jet_eta[jetIds[0]], event.Jet_phi[jetIds[0]], event.Jet_mass[jetIds[0]])
        j2_p4 = TLorentzVector()
        j2_p4.SetPtEtaPhiM(event.Jet_pt[jetIds[1]], event.Jet_eta[jetIds[1]], event.Jet_phi[jetIds[1]], event.Jet_mass[jetIds[1]])
        self.out.jj_mass[0]       = (j1_p4+j2_p4).M()
        self.out.jj_deltaEta[0]   = abs(event.Jet_eta[jetIds[0]]-event.Jet_eta[jetIds[1]])
        self.out.jj_deltaPhi[0]   = abs(event.Jet_phi[jetIds[0]]-event.Jet_phi[jetIds[1]])

        
        ## Dijet-based event selections
        if self.out.jj_mass[0] < 800: return False  # will need to change this when deriving the trigger efficiency
        #if self.out.jj_deltaEta[0]>1.1: return False

 
        ## Fill jet branches
        self.out.njets[0]         = len(jetIds)
        
        self.out.jpt_1[0]       = event.Jet_pt[jetIds[0]]
        self.out.jeta_1[0]      = event.Jet_eta[jetIds[0]]
        self.out.jphi_1[0]      = event.Jet_phi[jetIds[0]]
        self.out.jmass_1[0]      = event.Jet_mass[jetIds[0]]
        self.out.jdeepCSV_1[0]  = event.Jet_btagDeepB[jetIds[0]]
        self.out.jdeepFlavour_1[0]  = event.Jet_btagDeepFlavB[jetIds[0]]
        self.out.jjetsId_1[0] = event.Jet_jetId[jetIds[0]]

        self.out.jpt_2[0]       = event.Jet_pt[jetIds[1]]
        self.out.jeta_2[0]      = event.Jet_eta[jetIds[1]]
        self.out.jphi_2[0]      = event.Jet_phi[jetIds[1]]
        self.out.jmass_2[0]     = event.Jet_mass[jetIds[1]]
        self.out.jdeepCSV_2[0]  = event.Jet_btagDeepB[jetIds[1]]
        self.out.jdeepFlavour_2[0]= event.Jet_btagDeepFlavB[jetIds[1]]
        self.out.jjetsId_2[0] = event.Jet_jetId[jetIds[1]]

        self.out.jsorted[0]       = 0
        if leading1==0 and leading2==1: self.out.jsorted[0] = 1

        self.out.MET_over_SumEt[0] = event.MET_pt/jetHT
        
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
        
