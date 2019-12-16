import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

from TreeProducer import *
from TreeProducerCommon import *
from CorrectionTools.PileupWeightTool import *
from CorrectionTools.BTaggingTool import BTagWeightTool, BTagWPs
from CorrectionTools.MuonSFs import *
from CorrectionTools.ElectronSFs import *
from CorrectionTools.RecoilCorrectionTool import getTTptWeight, getTTPt
from CorrectionTools.DYCorrection import *
import struct
import numpy as np

class LLProducer(Module):

    def __init__(self, name, DataType, filelist, **kwargs):
        
        self.name = name
        self.out = TreeProducer(name)
        self.sample = filelist

        if DataType=='data':
            self.isData = True
            self.isMC = False
        else:
            self.isData = False
            self.isMC = True
        self.year           = kwargs.get('year',     2017 )
        self.tes            = kwargs.get('tes',      1.0  )
        self.ltf            = kwargs.get('ltf',      1.0  )
        self.jtf            = kwargs.get('jtf',      1.0 )
        year                = self.year
        self.filter         = getMETFilters(year,self.isData)
        if not self.isData:
            self.muSFs  = MuonSFs(year=year)
            self.elSFs  = ElectronSFs(year=year)
            self.puTool = PileupWeightTool(year =year)
            self.btagToolAK8 = BTagWeightTool('CSVv2','AK8','loose',sigma='central',channel='ll',year=year)
            self.btagToolAK4 = BTagWeightTool('CSVv2','AK4','loose',sigma='central',channel='ll',year=year)
            self.btagToolAK8_deep = BTagWeightTool('DeepCSV','AK8','loose',sigma='central',channel='ll',year=year)
            self.btagToolAK8_deep_up = BTagWeightTool('DeepCSV','AK8','loose',sigma='up',channel='ll',year=year)
            self.btagToolAK8_deep_down = BTagWeightTool('DeepCSV','AK8','loose',sigma='down',channel='ll',year=year)
            self.btagToolAK4_deep = BTagWeightTool('DeepCSV','AK4','loose',sigma='central',channel='ll',year=year)
            self.btagToolAK4_deep_up = BTagWeightTool('DeepCSV','AK4','loose',sigma='up',channel='ll',year=year)
            self.btagToolAK4_deep_down = BTagWeightTool('DeepCSV','AK4','loose',sigma='down',channel='ll',year=year)
            if 'DYJetsToLL' in self.sample[0]:
                self.DYCorr = DYCorrection('DYJetsToLL')
            elif 'ZJetsToNuNu' in self.sample[0]:
                self.DYCorr = DYCorrection('ZJetsToNuNu')
            elif 'WJetsToLNu' in self.sample[0]:
                self.DYCorr = DYCorrection('WJetsToLNu')
    def beginJob(self):
        pass

    def endJob(self):
        if not self.isData:
            self.btagToolAK8.setDirectory(self.out.outputfile,'AK8btag')
            self.btagToolAK8_deep.setDirectory(self.out.outputfile,'AK8btag_deep')
            self.btagToolAK4.setDirectory(self.out.outputfile,'AK4btag')
            self.btagToolAK4_deep.setDirectory(self.out.outputfile,'AK4btag_deep')
        self.out.outputfile.Write()
        self.out.outputfile.Close()

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass


    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):     
        pass
        
    def fillBranches(self,event):
        self.out.isMC[0]                    = self.isMC
        self.out.is2016[0]                  = self.is2016
        self.out.is2017[0]                  = self.is2017
        self.out.is2018[0]                  = self.is2018
        self.out.EventNumber[0]             = event.event
        self.out.LumiNumber[0]              = event.luminosityBlock
        self.out.RunNumber[0]               = event.run
        self.out.EventWeight[0]             = self.EventWeight
        self.out.TopWeight[0]               = self.TopWeight
        self.out.BTagAK8Weight[0]           = self.BTagAK8Weight
        self.out.BTagAK4Weight[0]           = self.BTagAK4Weight
        self.out.BTagAK8Weight_deep[0]      = self.BTagAK8Weight_deep
        self.out.BTagAK8Weight_deep_up[0]   = self.BTagAK8Weight_deep_up
        self.out.BTagAK8Weight_deep_down[0] = self.BTagAK8Weight_deep_down
        self.out.BTagAK4Weight_deep[0]      = self.BTagAK4Weight_deep
        self.out.BTagAK4Weight_deep_up[0]   = self.BTagAK4Weight_deep_up
        self.out.BTagAK4Weight_deep_down[0] = self.BTagAK4Weight_deep_down
        self.out.BBTagWeight[0]             = self.BBTagWeight
        self.out.GenWeight[0]               = self.GenWeight
        self.out.PUWeight[0]                = self.PUWeight
        self.out.LeptonWeight[0]            = self.LeptonWeight
        self.out.LeptonWeightUp[0]          = self.LeptonWeightUp
        self.out.LeptonWeightDown[0]        = self.LeptonWeightDown
        self.out.TriggerWeight[0]           = self.TriggerWeight
        self.out.TriggerWeightUp[0]         = self.TriggerWeightUp
        self.out.TriggerWeightDown[0]       = self.TriggerWeightDown
        self.out.QCDNLO_Corr[0]             = self.QCDNLO_Corr
        self.out.QCDNNLO_Corr[0]            = self.QCDNNLO_Corr
        self.out.EWKNLO_Corr[0]             = self.EWKNLO_Corr
        self.out.isZtoNN[0]                 = self.isZtoNN
        self.out.isZtoEE[0]                 = self.isZtoEE
        self.out.isZtoMM[0]                 = self.isZtoMM
        self.out.isTtoEM[0]                 = self.isTtoEM
        self.out.isBoosted4B[0]             = self.isBoosted4B
        self.out.isHtobb[0]                 = self.isHtobb
        self.out.isHtobb_ml[0]              = self.isHtobb_ml
        self.out.isMaxBTag_loose[0]         = self.isMaxBTag_loose
        self.out.isMaxBTag_medium[0]        = self.isMaxBTag_medium
        self.out.isMaxBTag_tight[0]         = self.isMaxBTag_tight
        self.out.isVBF[0]                   = self.isVBF
        self.out.nPV[0]                     = event.PV_npvsGood
        self.out.nTaus[0]                   = self.nTaus
        self.out.nElectrons[0]              = self.nElectrons
        self.out.nMuons[0]                  = self.nMuons
        self.out.nJets[0]                   = self.nJetsNoFatJet
        self.out.nFatJets[0]                = self.nFatJets
        self.out.DPhi[0]                    = self.DPhi
        self.out.DEta[0]                    = self.VHDEta
        self.out.MinDPhi[0]                 = self.MinJetMetDPhi
        self.out.MaxBTag[0]                 = self.MaxJetNoFatJetBTag
        self.out.BtagDeepB[0]               = self.BtagDeepB
        self.out.DeepTagMD_H4qvsQCD[0]      = self.DeepTagMD_H4qvsQCD
        self.out.DeepTagMD_HbbvsQCD[0]      = self.DeepTagMD_HbbvsQCD
        self.out.DeepTagMD_ZHbbvsQCD[0]     = self.DeepTagMD_ZHbbvsQCD
        self.out.DeepTagMD_ZbbvsQCD[0]      = self.DeepTagMD_ZbbvsQCD
        self.out.DeepTagMD_bbvsLight[0]     = self.DeepTagMD_bbvsLight
        self.out.DeepTagMD_WvsQCD[0]        = self.DeepTagMD_WvsQCD
        self.out.DeepTagMD_ZvsQCD[0]        = self.DeepTagMD_ZvsQCD
        self.out.Mu1_pt[0]                  = self.Mu1_pt
        self.out.Mu1_eta[0]                 = self.Mu1_eta
        self.out.Mu1_phi[0]                 = self.Mu1_phi
        self.out.Mu1_mass[0]                = self.Mu1_mass
        self.out.Mu1_pfIsoId[0]             = self.Mu1_pfIsoId
        self.out.Mu1_relIso[0]              = self.Mu1_relIso
        self.out.Mu2_pt[0]                  = self.Mu2_pt
        self.out.Mu2_eta[0]                 = self.Mu2_eta
        self.out.Mu2_phi[0]                 = self.Mu2_phi
        self.out.Mu2_mass[0]                = self.Mu2_mass
        self.out.Mu2_pfIsoId[0]             = self.Mu2_pfIsoId
        self.out.Mu2_relIso[0]              = self.Mu2_relIso
        self.out.Ele1_pt[0]                 = self.Ele1_pt
        self.out.Ele1_eta[0]                = self.Ele1_eta
        self.out.Ele1_phi[0]                = self.Ele1_phi
        self.out.Ele1_mass[0]               = self.Ele1_mass
        self.out.Ele2_pt[0]                 = self.Ele2_pt
        self.out.Ele2_eta[0]                = self.Ele2_eta
        self.out.Ele2_phi[0]                = self.Ele2_phi
        self.out.Ele2_mass[0]               = self.Ele2_mass
        self.out.Ele_HEM15_16[0]            = self.Ele_HEM15_16
        self.out.Jet1_VBF_pt[0]             = self.Jet1_VBF_pt
        self.out.Jet1_VBF_eta[0]            = self.Jet1_VBF_eta
        self.out.Jet1_VBF_phi[0]            = self.Jet1_VBF_phi
        self.out.Jet1_VBF_mass[0]           = self.Jet1_VBF_mass
        self.out.Jet2_VBF_pt[0]             = self.Jet2_VBF_pt
        self.out.Jet2_VBF_eta[0]            = self.Jet2_VBF_eta
        self.out.Jet2_VBF_phi[0]            = self.Jet2_VBF_phi
        self.out.Jet2_VBF_mass[0]           = self.Jet2_VBF_mass
        self.out.dijet_VBF_mass[0]          = self.dijet_VBF_mass 
        self.out.deltaR_VBF[0]              = self.deltaR_VBF 
        self.out.deltaR_HVBFjet1[0]         = self.deltaR_HVBFjet1
        self.out.deltaR_HVBFjet2[0]         = self.deltaR_HVBFjet2
        self.out.MET[0]                     = event.PuppiMET_pt
        self.out.MET_chs[0]                 = event.MET_pt
        self.out.HT_HEM15_16[0]             = self.HT_HEM15_16
        self.out.LHEScaleWeight             = self.LHEScaleWeight
        self.out.LHEPdfWeight               = self.LHEPdfWeight
        self.out.LHEWeight_originalXWGTUP[0]= self.LHEWeight_originalXWGTUP
        self.out.PrefireWeight[0]           = self.PrefireWeight
        self.out.PrefireWeightUp[0]         = self.PrefireWeightUp
        self.out.PrefireWeightDown[0]       = self.PrefireWeightDown
        self.out.HT[0]                      = self.HT
        self.out.H_pt[0]                    = self.H_pt
        self.out.H_eta[0]                   = self.H_eta
        self.out.H_phi[0]                   = self.H_phi
        self.out.H_mass[0]                  = self.H_mass
        self.out.H_M[0]                     = self.H_M
        self.out.H_tau21[0]                 = self.H_tau21
        self.out.H_tau41[0]                 = self.H_tau41
        self.out.H_tau42[0]                 = self.H_tau42
        self.out.H_tau31[0]                 = self.H_tau31
        self.out.H_tau32[0]                 = self.H_tau32
        self.out.H_ddt[0]                   = self.H_ddt
        self.out.H_csv1[0]                  = self.H_csv1
        self.out.H_csv2[0]                  = self.H_csv2
        self.out.H_deepcsv1[0]              = self.H_deepcsv1
        self.out.H_deepcsv2[0]              = self.H_deepcsv2
        self.out.H_dbt[0]                   = self.H_dbt
        self.out.H_ntag[0]                  = self.H_ntag
        self.out.H_hadronflavour[0]         = self.H_hadronflavour
        self.out.H_partonflavour[0]         = self.H_partonflavour
        self.out.H_chf[0]                   = self.H_chf
        self.out.H_nhf[0]                   = self.H_nhf
        self.out.V_pt[0]                    = self.V_pt
        self.out.V_eta[0]                   = self.V_eta
        self.out.V_phi[0]                   = self.V_phi
        self.out.V_mass[0]                  = self.V_mass
        self.out.VH_deltaR[0]               = self.VH_deltaR
        self.out.X_pt[0]                    = self.X_pt
        self.out.X_eta[0]                   = self.X_eta
        self.out.X_phi[0]                   = self.X_phi
        self.out.X_mass[0]                  = self.X_mass
        self.out.X_mass_chs[0]              = self.X_mass_chs
        self.out.X_mass_jesUp[0]            = self.X_mass_jesUp
        self.out.X_mass_jesDown[0]          = self.X_mass_jesDown
        self.out.X_mass_jerUp[0]            = self.X_mass_jerUp
        self.out.X_mass_jerDown[0]          = self.X_mass_jerDown
        self.out.X_mass_MET_jesUp[0]        = self.X_mass_MET_jesUp
        self.out.X_mass_MET_jesDown[0]      = self.X_mass_MET_jesDown
        self.out.X_mass_MET_jerUp[0]        = self.X_mass_MET_jerUp
        self.out.X_mass_MET_jerDown[0]      = self.X_mass_MET_jerDown
        self.out.H_mass_jmsUp[0]            = self.H_mass_jmsUp
        self.out.H_mass_jmsDown[0]          = self.H_mass_jmsDown
        self.out.H_mass_jmrUp[0]            = self.H_mass_jmrUp
        self.out.H_mass_jmrDown[0]          = self.H_mass_jmrDown
        self.out.tree.Fill()



    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        #####   set variables     ####
        self.nElectrons            = 0
        self.nMuons                = 0
        self.nTaus                 = 0
        self.nFatJets              = 0
        self.EventWeight           = 1.
        self.TopWeight             = 1.
        self.BTagAK8Weight         = 1.
        self.BTagAK4Weight         = 1.
        self.BTagAK8Weight_deep    = 1.
        self.BTagAK8Weight_deep_up = 1.
        self.BTagAK8Weight_deep_down = 1.
        self.BTagAK4Weight_deep    = 1.
        self.BTagAK4Weight_deep_up = 1.
        self.BTagAK4Weight_deep_down = 1.
        self.BBTagWeight           = 1.
        self.GenWeight             = 1.
        self.PUWeight              = 1.
        self.LeptonWeight          = 1.
        self.LeptonWeightUp        = 1.
        self.LeptonWeightDown      = 1.
        self.TriggerWeight         = 1.
        self.TriggerWeightUp       = 1.
        self.TriggerWeightDown     = 1.
        self.isZtoMM               = False
        self.isZtoEE               = False
        self.isZtoNN               = False
        self.isTtoEM               = False
        self.isBoosted4B           = False
        self.isHtobb               = False
        self.isHtobb_ml            = False
        self.isMaxBTag_loose       = False
        self.isMaxBTag_medium      = False
        self.isMaxBTag_tight       = False
        self.isVBF                 = False
        self.is2016                = False
        self.is2017                = False
        self.is2018                = False
        self.nTaus                 = 0
        self.nJetsNoFatJet         = 0
        self.H_partonflavour       = -1.
        self.H_hadronflavour       = -1.
        self.DPhi                  = -1.
        self.VHDEta                = -1.
        self.MinJetMetDPhi         = 10.
        self.MaxJetNoFatJetBTag    = -1.
        self.BtagDeepB             = -1.
        self.DeepTagMD_H4qvsQCD    = -1.
        self.DeepTagMD_HbbvsQCD    = -1.
        self.DeepTagMD_ZHbbvsQCD   = -1.
        self.DeepTagMD_ZbbvsQCD    = -1.
        self.DeepTagMD_bbvsLight   = -1.
        self.DeepTagMD_WvsQCD      = -1.
        self.DeepTagMD_ZvsQCD      = -1.
        self.Mu1_pt                = -1.
        self.Mu1_eta               = -1.
        self.Mu1_phi               = -1.
        self.Mu1_mass              = -1.
        self.Mu1_pfIsoId           = -1.
        self.Mu1_relIso            = -1.
        self.Mu2_pt                = -1.
        self.Mu2_eta               = -1.
        self.Mu2_phi               = -1.
        self.Mu2_mass              = -1.
        self.Mu2_pfIsoId           = -1.
        self.Mu2_relIso            = -1.
        self.Ele1_pt               = -1.
        self.Ele1_eta              = -1.
        self.Ele1_phi              = -1.
        self.Ele1_mass             = -1.
        self.Ele2_pt               = -1.
        self.Ele2_eta              = -1.
        self.Ele2_phi              = -1.
        self.Ele2_mass             = -1.
        self.Ele_HEM15_16          = -1.
        self.HT_HEM15_16           = -1.
        self.HT                    =  0.
        self.LHEScaleWeight        = -1.
        self.LHEPdfWeight          = -1.
        self.LHEWeight_originalXWGTUP = -1.
        self.PrefireWeight         = 1.
        self.PrefireWeightUp       = 1.
        self.PrefireWeightDown     = 1.
        self.QCDNLO_Corr           = 1.
        self.QCDNNLO_Corr          = 1.
        self.EWKNLO_Corr           = 1.
        self.Jet1_VBF_pt           = -1.
        self.Jet1_VBF_eta          = -1.
        self.Jet1_VBF_phi          = -1.
        self.Jet1_VBF_mass         = -1.
        self.Jet2_VBF_pt           = -1.
        self.Jet2_VBF_eta          = -1.
        self.Jet2_VBF_phi          = -1.
        self.Jet2_VBF_mass         = -1.
        self.dijet_VBF_mass        = -1.
        self.deltaR_VBF            = -1.
        self.deltaR_HVBFjet1       = -1.
        self.deltaR_HVBFjet2       = -1.
        self.H_pt                  = -1.
        self.H_eta                 = -1.
        self.H_phi                 = -1.
        self.H_mass                = -1.
        self.H_M                   = -1.
        self.H_tau21               = -1.
        self.H_tau41               = -1.
        self.H_tau42               = -1.
        self.H_tau31               = -1.
        self.H_tau32               = -1.
        self.H_ddt                 = -1.
        self.H_csv1                = -1.
        self.H_csv2                = -1.
        self.H_deepcsv1            = -1.
        self.H_deepcsv2            = -1.
        self.H_dbt                 = -1.
        self.H_ntag                = -1
        self.H_chf                 = -1.
        self.H_nhf                 = -1.
        self.V_pt                  = -1.
        self.V_eta                 = -1.
        self.V_phi                 = -1.
        self.V_mass                = -1.
        self.VH_deltaR             = -1.
        self.X_pt                  = -1.
        self.X_eta                 = -1.
        self.X_phi                 = -1.
        self.X_mass                = -1.
        self.X_mass_chs            = -1.
        self.X_mass_jesUp          = -1.
        self.X_mass_jesDown        = -1.
        self.X_mass_jerUp          = -1.
        self.X_mass_jerDown        = -1.
        self.X_mass_MET_jesUp      = -1.
        self.X_mass_MET_jesDown    = -1.
        self.X_mass_MET_jerUp      = -1.
        self.X_mass_MET_jerDown    = -1.
        self.H_mass_jmsUp          = -1.
        self.H_mass_jmsDown        = -1.
        self.H_mass_jmrUp          = -1.
        self.H_mass_jmrDown        = -1.

        
        
        eecutflow_list                = []
        mmcutflow_list                = []
        nncutflow_list                = []

        idx_electrons = []
        idx_loose_electrons = []
        idx_muons = []
        idx_loose_muons = []
        idx_fatjet = []
        idx_jet = []
        idx_jet_vbf = []

        electrons_tlv_list = []
        loose_electrons_tlv_list = []
        muons_tlv_list = []
        loose_muons_tlv_list = []
        fatjet_tlv_list = []
        jet_tlv_list = []
        jet_tlv_list_vbf = []
        fatjet_tau21_list = []
        fatjet_tau41_list = []
        fatjet_tau42_list = []
        fatjet_tau31_list = []
        fatjet_tau32_list = []
        fatjet_nbtag_list = []

        V = ROOT.TLorentzVector()
        H = ROOT.TLorentzVector()
        X = ROOT.TLorentzVector()

        V_chs = ROOT.TLorentzVector()
        #########     cuts    #########
        elec1_pt_cut = 55.
        elec2_pt_cut = 20.
        elec_pt_cut = 10.
        elec_eta_cut = 2.5
        muon1_pt_cut = 55.
        muon2_pt_cut = 20.          
        muon_pt_cut = 10.
        muon_eta_cut = 2.4
        tau_pt_cut = 18.
        tau_eta_cut = 2.3
        ak4_pt_cut = 30.
        ak4_eta_cut = 2.4
        fatjet_pt_cut = 200.
        fatjet_eta_cut = 2.4
        met_pt_cut = 250.
        v_pt_cut = 200.
        tau21_lowercut = 0.35
        tau21_uppercut = 0.75
        j_mass_lowercut = 30.
        j_mass_uppercut = 250.
        v_mass_lowercut = 65.
        v_mass_intercut = 85.
        v_mass_uppercut = 105.
        h_mass_lowercut = 105.
        h_mass_uppercut = 135.
        x_mass_lowercut = 750.
        xt_mass_lowercut = 650.
        xjj_mass_lowercut = 950.
        
        #### flag for year #######
        if self.year == 2016:
            self.is2016 = True
        elif self.year == 2017:
            self.is2017 = True
        elif self.year == 2018:
            self.is2018 = True
            
        
        #########     triggers     #########
        if self.year == 2016:
            trigger_SingleMu      = event.HLT_Mu50
            trigger_SingleEle     = event.HLT_Ele115_CaloIdVT_GsfTrkIdT
            trigger_SingleIsoEle  = event.HLT_Ele27_WPTight_Gsf
            trigger_SinglePhoton  = event.HLT_Photon175
            trigger_METMHTNoMu    = any([event.HLT_PFMETNoMu110_PFMHTNoMu110_IDTight,
                                         event.HLT_PFMETNoMu120_PFMHTNoMu120_IDTight,
                                         event.HLT_MonoCentralPFJet80_PFMETNoMu120_PFMHTNoMu120_IDTight])
            trigger_METMHT        = any([event.HLT_PFMET110_PFMHT110_IDTight, 
                                         event.HLT_PFMET120_PFMHT120_IDTight])
            trigger_MET           = any([event.HLT_PFMET170_NotCleaned,
                                         event.HLT_PFMET170_HBHECleaned])
        elif self.year == 2017:
            trigger_SingleMu          = event.HLT_Mu50
            try:
                trigger_SingleEle     = event.HLT_Ele115_CaloIdVT_GsfTrkIdT
            except:
                trigger_SingleEle     = None
            trigger_SingleIsoEle      = event.HLT_Ele35_WPTight_Gsf
            trigger_SinglePhoton      = event.HLT_Photon200
            try:
                trigger_METMHTNoMu    = any([event.HLT_PFMETNoMu110_PFMHTNoMu110_IDTight,
                                             event.HLT_PFMETNoMu120_PFMHTNoMu120_IDTight,
                                             event.HLT_PFMETNoMu130_PFMHTNoMu130_IDTight,
                                             event.HLT_PFMETNoMu140_PFMHTNoMu140_IDTight,
                                             event.HLT_MonoCentralPFJet80_PFMETNoMu120_PFMHTNoMu120_IDTight])
            except:
                trigger_METMHTNoMu    = any([event.HLT_PFMETNoMu110_PFMHTNoMu110_IDTight,
                                             event.HLT_PFMETNoMu120_PFMHTNoMu120_IDTight,
                                             event.HLT_MonoCentralPFJet80_PFMETNoMu120_PFMHTNoMu120_IDTight])
            trigger_METMHT            = any([event.HLT_PFMET110_PFMHT110_IDTight, 
                                             event.HLT_PFMET120_PFMHT120_IDTight,
                                             event.HLT_PFMET130_PFMHT130_IDTight, 
                                             event.HLT_PFMET140_PFMHT140_IDTight,
                                             event.HLT_PFMETTypeOne110_PFMHT110_IDTight,
                                             event.HLT_PFMETTypeOne120_PFMHT120_IDTight,
                                             event.HLT_PFMETTypeOne130_PFMHT130_IDTight,
                                             event.HLT_PFMETTypeOne140_PFMHT140_IDTight])
            try:
                trigger_MET           = any([event.HLT_PFMET200_NotCleaned,
                                             event.HLT_PFMET200_HBHECleaned,
                                             event.HLT_PFMET200_HBHE_BeamHaloCleaned,
                                             event.HLT_PFMET250_HBHECleaned])
            except:
                trigger_MET           = None

        elif self.year == 2018:
            trigger_SingleMu      = event.HLT_Mu50
            trigger_SingleEle     = event.HLT_Ele115_CaloIdVT_GsfTrkIdT
            trigger_SingleIsoEle  = event.HLT_Ele32_WPTight_Gsf
            trigger_SinglePhoton  = event.HLT_Photon200
            trigger_METMHTNoMu    = any([event.HLT_PFMETNoMu110_PFMHTNoMu110_IDTight,
                                         event.HLT_PFMETNoMu120_PFMHTNoMu120_IDTight,
                                         event.HLT_PFMETNoMu130_PFMHTNoMu130_IDTight,
                                         event.HLT_PFMETNoMu140_PFMHTNoMu140_IDTight,
                                         event.HLT_MonoCentralPFJet80_PFMETNoMu120_PFMHTNoMu120_IDTight])
            trigger_METMHT        = any([event.HLT_PFMET110_PFMHT110_IDTight, 
                                         event.HLT_PFMET120_PFMHT120_IDTight,
                                         event.HLT_PFMET130_PFMHT130_IDTight, 
                                         event.HLT_PFMET140_PFMHT140_IDTight,
                                         event.HLT_PFMETTypeOne110_PFMHT110_IDTight,
                                         event.HLT_PFMETTypeOne120_PFMHT120_IDTight,
                                         event.HLT_PFMETTypeOne130_PFMHT130_IDTight,
                                         event.HLT_PFMETTypeOne140_PFMHT140_IDTight])
            trigger_MET           = any([event.HLT_PFMET200_NotCleaned,
                                         event.HLT_PFMET200_HBHECleaned,
                                         event.HLT_PFMET200_HBHE_BeamHaloCleaned,
                                         event.HLT_PFMET250_HBHECleaned])
        ##########     Gen Weight #########
        if self.isMC:
            self.GenWeight = -1. if event.genWeight < 0 else 1.
            self.PUWeight = self.puTool.getWeight(event.Pileup_nTrueInt)
            self.EventWeight *= self.GenWeight
            self.EventWeight *= self.PUWeight
            self.LHEScaleWeight        = event.LHEScaleWeight
            self.LHEPdfWeight          = event.LHEPdfWeight
            self.LHEWeight_originalXWGTUP = event.LHEWeight_originalXWGTUP
            self.out.events.Fill(0.,self.GenWeight)
            self.out.original.Fill(0.,event.LHEWeight_originalXWGTUP)
            if self.year == 2016 or self.year == 2017:
                self.PrefireWeight = event.PrefireWeight
                self.PrefireWeightUp = event.PrefireWeight_Up
                self.PrefireWeightDown = event.PrefireWeight_Down
            
        if self.isData and event.PV_npvs == 0:
            return False
        if not self.isData:
            self.out.pileup.Fill(event.Pileup_nTrueInt)
            if event.Pileup_nTrueInt == 0:
                return False
                
        ###########     electrons ##########
        for ielectron in range(event.nElectron):
            electron_pt = event.Electron_pt[ielectron]
            electron_eta = event.Electron_eta[ielectron]
            electron_phi = event.Electron_phi[ielectron]
            electron_mass = event.Electron_mass[ielectron]
            electron_tlv = ROOT.TLorentzVector()
            electron_tlv.SetPtEtaPhiM(electron_pt, electron_eta,electron_phi, electron_mass)
            if electron_eta > -2.5 and electron_eta < -1.479 and electron_phi > -1.55 and electron_phi < -0.9:
                if self.Ele_HEM15_16 == -1.:
                    self.Ele_HEM15_16 = 0.
                self.Ele_HEM15_16 += electron_pt
            if electron_pt > elec_pt_cut and abs(electron_eta) < elec_eta_cut:
                idx_electrons.append(ielectron)
                electrons_tlv_list.append(electron_tlv)
                if event.Electron_cutBased[ielectron] >= 2:
                    idx_loose_electrons.append(ielectron)
                    loose_electrons_tlv_list.append(electron_tlv)
        self.nElectrons = len(loose_electrons_tlv_list)
        
        ###########     muons     #########
        for imuon in range(event.nMuon):
            muon_pt = event.Muon_pt[imuon]
            muon_eta = event.Muon_eta[imuon]
            muon_phi = event.Muon_phi[imuon]
            muon_mass = event.Muon_mass[imuon]
            muon_tlv = ROOT.TLorentzVector()
            muon_tlv.SetPtEtaPhiM(muon_pt, muon_eta, muon_phi, muon_mass)
            if muon_pt > muon_pt_cut and abs(muon_eta) < muon_eta_cut:
                idx_muons.append(imuon)
                muons_tlv_list.append(muon_tlv)
                if event.Muon_isPFcand[imuon] and struct.unpack('B',event.Muon_pfIsoId[imuon])[0]>=2 and (event.Muon_isGlobal[imuon] or event.Muon_isTracker[imuon]):
                    idx_loose_muons.append(imuon)
                    loose_muons_tlv_list.append(muon_tlv)
        self.nMuons = len(loose_muons_tlv_list)


        ############    taus         #########
        for itau in range(event.nTau):
            tau_pt = event.Tau_pt[itau]
            tau_eta = event.Tau_eta[itau]
            tau_phi = event.Tau_phi[itau]
            tau_mass = event.Tau_mass[itau]
            tau_tlv = ROOT.TLorentzVector()
            tau_tlv.SetPtEtaPhiM(tau_pt, tau_eta, tau_phi, tau_mass)
            if tau_pt > tau_pt_cut and abs(tau_eta) < tau_eta_cut:
                cleanTau = True
                for loose_electrons_tlv in loose_electrons_tlv_list:
                    if loose_electrons_tlv.DeltaR(tau_tlv) < 0.4:
                        cleanTau = False
                for loose_muons_tlv in loose_muons_tlv_list:
                    if loose_muons_tlv.DeltaR(tau_tlv) < 0.4:
                        cleanTau = False
                if cleanTau:
                    self.nTaus += 1

        ###########    FatJet        #########
        for ifatjet in range(event.nFatJet):
            fatjet_pt = event.FatJet_pt[ifatjet]
            fatjet_eta = event.FatJet_eta[ifatjet]
            fatjet_phi = event.FatJet_phi[ifatjet]
            fatjet_mass = event.FatJet_mass[ifatjet]
            fatjet_jetid = event.FatJet_jetId[ifatjet]
            fatjet_tlv = ROOT.TLorentzVector()
            fatjet_tlv.SetPtEtaPhiM(fatjet_pt, fatjet_eta, fatjet_phi, fatjet_mass)
            if fatjet_pt > fatjet_pt_cut and abs(fatjet_eta) < fatjet_eta_cut:
                cleanJet = True
                #for loose_electrons_tlv in loose_electrons_tlv_list:
                #    if loose_electrons_tlv.DeltaR(fatjet_tlv) < 0.8:
                #        cleanJet = False
                #for loose_muons_tlv in loose_muons_tlv_list:
                #    if loose_muons_tlv.DeltaR(fatjet_tlv) < 0.8:
                #        cleanJet = False        
                if cleanJet:
                    if event.FatJet_tau1[ifatjet]==0:
                        fatjet_tau21_list.append(0)
                        fatjet_tau41_list.append(0)
                        fatjet_tau31_list.append(0)
                    else:
                        fatjet_tau21_list.append(event.FatJet_tau2[ifatjet]/event.FatJet_tau1[ifatjet])
                        fatjet_tau41_list.append(event.FatJet_tau4[ifatjet]/event.FatJet_tau1[ifatjet])
                        fatjet_tau31_list.append(event.FatJet_tau3[ifatjet]/event.FatJet_tau1[ifatjet])
                    if event.FatJet_tau2[ifatjet]==0:
                        fatjet_tau42_list.append(0)
                        fatjet_tau32_list.append(0)
                    else:
                        fatjet_tau42_list.append(event.FatJet_tau4[ifatjet]/event.FatJet_tau2[ifatjet])
                        fatjet_tau32_list.append(event.FatJet_tau3[ifatjet]/event.FatJet_tau2[ifatjet])
                    fatjet_tlv_list.append(fatjet_tlv)
                    idx_fatjet.append(ifatjet)
                    fatjet_nbtag = 0
                    for isubjet in [event.FatJet_subJetIdx1[ifatjet], event.FatJet_subJetIdx2[ifatjet]]:
                        if isubjet >= 0 and event.SubJet_btagCSVV2[isubjet] > 0.5426: 
                            fatjet_nbtag += 1
                    fatjet_nbtag_list.append(fatjet_nbtag)
        self.nFatJets = len(fatjet_tlv_list)
    
        ############     MET       ##########
        METx = 0.
        METy = 0.
        MET_tlv = ROOT.TLorentzVector()
        MET_tlv.SetPtEtaPhiE(event.PuppiMET_pt,0.,event.PuppiMET_phi, event.PuppiMET_pt)
  
        ############  TTbar pT reweighting ########
        if self.isMC and 'TT' in self.sample[0]:
            Top1_pt, Top2_pt = getTTPt(event)
            self.TopWeight = getTTptWeight(Top1_pt, Top2_pt)
        ############     ZtoEE    ############
        self.out.eecutflow.Fill(0.,self.EventWeight)
        eecutflow_list.append(self.EventWeight)
        maxZpt = -1.
        Z_pt = -1.
        Z_m = -1.
        goodelectronpair = False
        for i in idx_electrons:
            for j in idx_electrons:
                if i==j or event.Electron_charge[i] == event.Electron_charge[j]:
                    continue
                eli_tlv = ROOT.TLorentzVector()
                eli_tlv.SetPtEtaPhiM(event.Electron_pt[i],event.Electron_eta[i],event.Electron_phi[i],event.Electron_mass[i])
                eli_v = ROOT.TVector3()
                eli_v.SetPtEtaPhi(event.Electron_pt[i],event.Electron_eta[i],event.Electron_phi[i])
                elj_tlv = ROOT.TLorentzVector()
                elj_tlv.SetPtEtaPhiM(event.Electron_pt[j],event.Electron_eta[j],event.Electron_phi[j],event.Electron_mass[j])
                elj_v = ROOT.TVector3()
                elj_v.SetPtEtaPhi(event.Electron_pt[j],event.Electron_eta[j],event.Electron_phi[j])
                diel = eli_tlv + elj_tlv
                Z_pt = diel.Pt()
                Z_m = diel.M()
                if Z_m > 70. and Z_m < 110. and Z_pt > maxZpt:
                    maxZpt = Z_pt
                    if eli_tlv.Pt() > elj_tlv.Pt():
                        el1 = i
                        el2 = j
                        el1_tlv = eli_tlv
                        el2_tlv = elj_tlv
                        el1_v = eli_v
                        el2_v = elj_v
                    else:
                        el1 = j
                        el2 = i
                        el1_tlv = elj_tlv
                        el2_tlv = eli_tlv
                        el1_v = elj_v
                        el2_v = eli_v
                    goodelectronpair = True
    
        
        if goodelectronpair:
            self.out.eecutflow.Fill(1.,self.EventWeight)
            eecutflow_list.append(self.EventWeight)
            if el1_tlv.Pt() > elec1_pt_cut and el2_tlv.Pt() > elec2_pt_cut:
                self.out.eecutflow.Fill(2.,self.EventWeight)
                eecutflow_list.append(self.EventWeight)
                if event.Electron_cutBased[el1] >= 2 and event.Electron_cutBased[el2] >= 2:
                    self.out.eecutflow.Fill(3.,self.EventWeight)
                    eecutflow_list.append(self.EventWeight)
                    if maxZpt > v_pt_cut:
                        self.out.eecutflow.Fill(4.,self.EventWeight)
                        eecutflow_list.append(self.EventWeight)
                        if trigger_SingleEle == None:
                            if not trigger_SingleIsoEle and not trigger_SinglePhoton:
                                print "ZtoEE trigger inconsistency"
                                return False
                        else:
                            if not trigger_SingleEle and not trigger_SingleIsoEle and not trigger_SinglePhoton:
                                print "ZtoEE trigger inconsistency"
                                return False
                        if not self.isMC and ("SinglePhoton" in self.sample[0] and (trigger_SingleEle or trigger_SingleIsoEle)):
                            print "ZtoEE double counting"
                            return False
                        self.out.eecutflow.Fill(5.,self.EventWeight)
                        eecutflow_list.append(self.EventWeight)
                        if self.isMC:
                            eltrig_tlv = el1_tlv
                            #for i in range(event.nTrigObj):
                            #    if event.TrigObj_id[i] ==11:
                            #        trigobj_v = ROOT.TVector3()
                            #        trigobj_v.SetPtEtaPhi(event.TrigObj_pt[i],event.TrigObj_eta[i],event.TrigObj_phi[i])
                            #        if event.TrigObj_filterBits[i]==CHANGE:
                            #            deltaR1 = trigobj_v.DeltaR(el1_v)
                            #            deltaR2 = trigobj_v.DeltaR(el2_v)
                            #            if deltaR2 < deltaR1 and deltaR2 < 0.2:
                            #                eltrig_tlv = el2_tlv
                            #                break
                            self.TriggerWeight = self.elSFs.getTriggerSF(eltrig_tlv.Pt(),eltrig_tlv.Eta())
                            self.TriggerWeightUp = self.elSFs.getTriggerSF(eltrig_tlv.Pt(),eltrig_tlv.Eta())   + self.elSFs.getTriggerSFerror(eltrig_tlv.Pt(),eltrig_tlv.Eta())
                            self.TriggerWeightDown = self.elSFs.getTriggerSF(eltrig_tlv.Pt(),eltrig_tlv.Eta()) - self.elSFs.getTriggerSFerror(eltrig_tlv.Pt(),eltrig_tlv.Eta())
                            self.LeptonWeight = self.elSFs.getIdIsoSF(el1_tlv.Pt(), el1_tlv.Eta())*self.elSFs.getIdIsoSF(el2_tlv.Pt(),el2_tlv.Eta())
                            IdIsoSF1 = self.elSFs.getIdIsoSF(el1_tlv.Pt(), el1_tlv.Eta())
                            IdIsoSF2 = self.elSFs.getIdIsoSF(el2_tlv.Pt(),el2_tlv.Eta())
                            IdIsoSF1error = self.elSFs.getIdIsoSFerror(el1_tlv.Pt(), el1_tlv.Eta())
                            IdIsoSF2error = self.elSFs.getIdIsoSFerror(el2_tlv.Pt(),el2_tlv.Eta())
                            self.LeptonWeight = IdIsoSF1*IdIsoSF2
                            LeptonWeightsigma = np.sqrt((IdIsoSF1error*IdIsoSF2)**2+(IdIsoSF2error*IdIsoSF1)**2)
                            self.LeptonWeightUp = self.LeptonWeight   + LeptonWeightsigma
                            self.LeptonWeightDown = self.LeptonWeight - LeptonWeightsigma
                            if 'DYJetsToLL' in self.sample[0] or 'ZJetsToNuNu' in self.sample[0] or 'WJetsToLNu' in self.sample[0]:
                                GenVpt = getGenVpt(event)
                                self.QCDNLO_Corr = self.DYCorr.getWeightQCDNLO(GenVpt)
                                self.QCDNNLO_Corr = self.DYCorr.getWeightQCDNNLO(GenVpt)
                                self.EWKNLO_Corr = self.DYCorr.getWeightEWKNLO(GenVpt)
                                self.EventWeight *= self.QCDNLO_Corr * self.QCDNNLO_Corr * self.EWKNLO_Corr
                            self.EventWeight *= self.TriggerWeight
                            self.EventWeight *= self.LeptonWeight
                        V = el1_tlv + el2_tlv
                        self.Ele1_pt   = el1_tlv.Pt()
                        self.Ele1_eta  = el1_tlv.Eta()
                        self.Ele1_phi  = el1_tlv.Phi()
                        self.Ele1_mass = el1_tlv.M()
                        self.Ele2_pt   = el2_tlv.Pt()
                        self.Ele2_eta  = el2_tlv.Eta()
                        self.Ele2_phi  = el2_tlv.Phi()
                        self.Ele2_mass = el2_tlv.M()
                        self.isZtoEE = True

          ##########      ZtoMM     #############
        self.out.mmcutflow.Fill(0.,self.EventWeight)
        mmcutflow_list.append(self.EventWeight)
        maxZpt = -1.
        Z_pt = -1.
        Z_m = -1.
        goodmuonpair = False
        for i in idx_muons:
            for j in idx_muons:
                if i==j or event.Muon_charge[i] == event.Muon_charge[j]:
                    continue
                mui_tlv = ROOT.TLorentzVector()
                mui_tlv.SetPtEtaPhiM(event.Muon_pt[i],event.Muon_eta[i],event.Muon_phi[i],event.Muon_mass[i])
                mui_v = ROOT.TVector3()
                mui_v.SetPtEtaPhi(event.Muon_pt[i],event.Muon_eta[i],event.Muon_phi[i])
                muj_tlv = ROOT.TLorentzVector()
                muj_tlv.SetPtEtaPhiM(event.Muon_pt[j],event.Muon_eta[j],event.Muon_phi[j],event.Muon_mass[j]) 
                muj_v = ROOT.TVector3()
                muj_v.SetPtEtaPhi(event.Muon_pt[j],event.Muon_eta[j],event.Muon_phi[j])
                dimu = mui_tlv + muj_tlv
                Z_pt = dimu.Pt()
                Z_m = dimu.M()
                if Z_m > 70. and Z_m < 110. and Z_pt > maxZpt:
                    maxZpt = Z_pt
                    if mui_tlv.Pt() > muj_tlv.Pt():
                        mu1 = i
                        mu2 = j
                        mu1_tlv = mui_tlv
                        mu2_tlv = muj_tlv
                        mu1_v = mui_v
                        mu2_v = muj_v
                    else:
                        mu1 = j
                        mu2 = i
                        mu1_tlv = muj_tlv
                        mu2_tlv = mui_tlv
                        mu1_v = muj_v
                        mu2_v = mui_v
                    goodmuonpair = True
        

        if goodmuonpair:
            self.out.mmcutflow.Fill(1.,self.EventWeight)
            mmcutflow_list.append(self.EventWeight)
            mu1_highPtId = struct.unpack('B',event.Muon_highPtId[mu1])[0]
            mu2_highPtId = struct.unpack('B',event.Muon_highPtId[mu2])[0] 
            if mu1_tlv.Pt() > muon1_pt_cut and mu2_tlv.Pt() > muon2_pt_cut:
                self.out.mmcutflow.Fill(2.,self.EventWeight)
                mmcutflow_list.append(self.EventWeight)
                if (mu1_highPtId >= 2 and mu2_highPtId >= 1) or (mu1_highPtId >= 1 and mu2_highPtId >= 2):
                    self.out.mmcutflow.Fill(3.,self.EventWeight)
                    mmcutflow_list.append(self.EventWeight)
                    if maxZpt > v_pt_cut:
                        self.out.mmcutflow.Fill(4.,self.EventWeight)
                        mmcutflow_list.append(self.EventWeight)
                        if not trigger_SingleMu:
                               print "ZtoMM trigger inconsistency"
                               return False
                        self.out.mmcutflow.Fill(5.,self.EventWeight)
                        mmcutflow_list.append(self.EventWeight)
                        if self.isMC:
                            mutrig_tlv = mu1_tlv
                            #for i in range(event.nTrigObj):
                            #    if event.TrigObj_id[i] ==13:
                            #        trigobj_v = ROOT.TVector3()
                            #        trigobj_v.SetPtEtaPhi(event.TrigObj_pt[i],event.TrigObj_eta[i],event.TrigObj_phi[i])
                            #        deltaR1 = trigobj_v.DeltaR(mu1_v)
                            #        deltaR2 = trigobj_v.DeltaR(mu2_v)
                            #        if event.TrigObj_filterBits[i]==CHANGE:
                            #            if deltaR2 < deltaR1 and deltaR2 < 0.2:
                            #                mutrig_tlv = mu2_tlv
                            #                break

                            self.TriggerWeight = self.muSFs.getTriggerSF(mutrig_tlv.Pt(),mutrig_tlv.Eta())
                            self.TriggerWeightUp = self.muSFs.getTriggerSF(mutrig_tlv.Pt(),mutrig_tlv.Eta())   + self.muSFs.getTriggerSFerror(mutrig_tlv.Pt(),mutrig_tlv.Eta())
                            self.TriggerWeightDown = self.muSFs.getTriggerSF(mutrig_tlv.Pt(),mutrig_tlv.Eta()) - self.muSFs.getTriggerSFerror(mutrig_tlv.Pt(),mutrig_tlv.Eta())
                            IdSF1 = self.muSFs.getIdSF(mu1_tlv.Pt(),mu1_tlv.Eta(),mu1_highPtId)
                            IdSF2 = self.muSFs.getIdSF(mu2_tlv.Pt(),mu2_tlv.Eta(),mu2_highPtId)
                            IdSF1error = self.muSFs.getIdSFerror(mu1_tlv.Pt(),mu1_tlv.Eta(),mu1_highPtId)
                            IdSF2error = self.muSFs.getIdSFerror(mu2_tlv.Pt(),mu2_tlv.Eta(),mu2_highPtId)
                            self.LeptonWeight = IdSF1*IdSF2
                            LeptonWeightsigma = np.sqrt((IdSF1error*IdSF2)**2+(IdSF2error*IdSF1)**2)
                            self.LeptonWeightUp = self.LeptonWeight   + LeptonWeightsigma
                            self.LeptonWeightDown = self.LeptonWeight - LeptonWeightsigma
                            if 'DYJetsToLL' in self.sample[0] or 'ZJetsToNuNu' in self.sample[0] or 'WJetsToLNu' in self.sample[0]:
                                GenVpt = getGenVpt(event)
                                self.QCDNLO_Corr = self.DYCorr.getWeightQCDNLO(GenVpt)
                                self.QCDNNLO_Corr = self.DYCorr.getWeightQCDNNLO(GenVpt)
                                self.EWKNLO_Corr = self.DYCorr.getWeightEWKNLO(GenVpt)
                                self.EventWeight *= self.QCDNLO_Corr * self.QCDNNLO_Corr * self.EWKNLO_Corr
                            self.EventWeight *= self.TriggerWeight
                            self.EventWeight *= self.LeptonWeight
                        if mu1_tlv.DeltaR(mu2_tlv) < 0.3:
                            try:
                                self.Mu1_relIso = ((event.Muon_tkRelIso[mu1]*mu1_tlv.Pt()) - mu2_tlv.Pt())/mu1_tlv.Pt()
                                self.Mu2_relIso = ((event.Muon_tkRelIso[mu2]*mu2_tlv.Pt()) - mu1_tlv.Pt())/mu2_tlv.Pt()
                            except:
                                self.Mu1_relIso = -1.
                                self.Mu2_relIso = -1.
                        else:
                            try:
                                self.Mu1_relIso = event.Muon_tkRelIso[mu1]
                                self.Mu2_relIso = event.Muon_tkRelIso[mu2]
                            except:
                                self.Mu1_relIso = -1.
                                self.Mu2_relIso = -1.
                        V = mu1_tlv + mu2_tlv
                        self.Mu1_pt   = mu1_tlv.Pt()
                        self.Mu1_eta  = mu1_tlv.Eta()
                        self.Mu1_phi  = mu1_tlv.Phi()
                        self.Mu1_mass = mu1_tlv.M()
                        self.Mu1_pfIsoId = struct.unpack('B',event.Muon_pfIsoId[mu1])[0]
                        self.Mu2_pt   = mu2_tlv.Pt()
                        self.Mu2_eta  = mu2_tlv.Eta()
                        self.Mu2_phi  = mu2_tlv.Phi()
                        self.Mu2_mass = mu2_tlv.M()
                        self.Mu2_pfIsoId = struct.unpack('B',event.Muon_pfIsoId[mu2])[0]
                        self.isZtoMM = True

        
        ###########     TtoEM     #########   
        if not self.isZtoMM and not self.isZtoEE and self.nElectrons == 1 and self.nMuons == 1:
            if event.Electron_charge[idx_loose_electrons[0]] != event.Muon_charge[idx_loose_muons[0]]:
                el_tlv = loose_electrons_tlv_list[0]
                mu_tlv = loose_muons_tlv_list[0]
                if mu_tlv.Pt() > 30. and el_tlv.Pt() > 30.: 
                    V = mu_tlv + el_tlv
                    if V.Pt() > 50.:
                        if trigger_SingleEle == None:
                            if not trigger_SingleIsoEle:
                                print "TtoEM trigger inconsistency"
                                return False
                        else:
                            if not trigger_SingleEle and not trigger_SingleIsoEle:
                                print "TtoEM trigger inconsistency"
                                return False
                        if self.isMC:
                            self.TriggerWeight = self.elSFs.getTriggerSF(el_tlv.Pt(),el_tlv.Eta())
                            self.LeptonWeight = self.elSFs.getIdIsoSF(el_tlv.Pt(), el_tlv.Eta())
                            if 'DYJetsToLL' in self.sample[0] or 'ZJetsToNuNu' in self.sample[0] or 'WJetsToLNu' in self.sample[0]:
                                GenVpt = getGenVpt(event)
                                self.QCDNLO_Corr = self.DYCorr.getWeightQCDNLO(GenVpt)
                                self.QCDNNLO_Corr = self.DYCorr.getWeightQCDNNLO(GenVpt)
                                self.EWKNLO_Corr = self.DYCorr.getWeightEWKNLO(GenVpt)
                                self.EventWeight *= self.QCDNLO_Corr * self.QCDNNLO_Corr * self.EWKNLO_Corr
                            self.EventWeight *= self.TriggerWeight
                            self.EventWeight *= self.LeptonWeight
                        self.Mu1_pt   = mu_tlv.Pt()
                        self.Mu1_eta  = mu_tlv.Eta()
                        self.Mu1_phi  = mu_tlv.Phi()
                        self.Mu1_mass = mu_tlv.M()
                        self.Ele1_pt   = el_tlv.Pt()
                        self.Ele1_eta  = el_tlv.Eta()
                        self.Ele1_phi  = el_tlv.Phi()
                        self.Ele1_mass = el_tlv.M()
                        self.isTtoEM = True

        #########   ZtoNN       ##########
        self.out.nncutflow.Fill(0.,self.EventWeight)
        nncutflow_list.append(self.EventWeight)
        if not self.isZtoMM and not self.isZtoEE and not self.isTtoEM:
            if event.PuppiMET_pt > met_pt_cut :
                self.out.nncutflow.Fill(1.,self.EventWeight)
                nncutflow_list.append(self.EventWeight)
                if self.nElectrons == 0 and self.nMuons == 0 and self.nTaus == 0:
                    self.out.nncutflow.Fill(2.,self.EventWeight)
                    nncutflow_list.append(self.EventWeight)
                    V.SetPtEtaPhiE(event.PuppiMET_pt,0.,event.PuppiMET_phi,event.PuppiMET_pt)
                    V_chs.SetPtEtaPhiE(event.MET_pt,0.,event.MET_phi,event.MET_pt)
                    if trigger_MET == None:
                        if not self.isMC and not trigger_METMHT and not trigger_METMHTNoMu:
                            print "ZtoNN Trigger inconsistency"
                            return False
                    else:
                        if not self.isMC and not trigger_MET and not trigger_METMHT and not trigger_METMHTNoMu:
                            print "ZtoNN Trigger inconsistency"
                            return False
                    self.out.nncutflow.Fill(3.,self.EventWeight)
                    nncutflow_list.append(self.EventWeight)
                    if self.filter(event) == False:
                        print "Bad event"
                        return False
                    self.out.nncutflow.Fill(4.,self.EventWeight)
                    nncutflow_list.append(self.EventWeight)
                    if self.isMC:
                        if 'DYJetsToLL' in self.sample[0] or 'ZJetsToNuNu' in self.sample[0] or 'WJetsToLNu' in self.sample[0]:
                            GenVpt = getGenVpt(event)
                            self.QCDNLO_Corr = self.DYCorr.getWeightQCDNLO(GenVpt)
                            self.QCDNNLO_Corr = self.DYCorr.getWeightQCDNNLO(GenVpt)
                            self.EWKNLO_Corr = self.DYCorr.getWeightEWKNLO(GenVpt)
                            self.EventWeight *= self.QCDNLO_Corr * self.QCDNNLO_Corr * self.EWKNLO_Corr
                        self.TriggerWeight = 1.
                    self.isZtoNN = True
        ##########  setting the Higgs and V index     #######
        if len(fatjet_tlv_list) == 0:
            return False            
        fatjet_idx_H = 0
        valid_Higgs = False
        if self.isZtoMM:
            fatjet_maxpt = 0.
            for i,fatjet_tlv in enumerate(fatjet_tlv_list):
                if fatjet_tlv.DeltaR(mu1_tlv)>0.8 and fatjet_tlv.DeltaR(mu2_tlv)>0.8 and fatjet_tlv.Pt()>fatjet_maxpt:
                    fatjet_maxpt=fatjet_tlv.Pt()
                    fatjet_idx_H = i
                    valid_Higgs = True
            if not valid_Higgs:
                return False

        elif self.isZtoEE:
            fatjet_maxpt = 0.
            for i,fatjet_tlv in enumerate(fatjet_tlv_list):
                if fatjet_tlv.DeltaR(el1_tlv)>0.8 and fatjet_tlv.DeltaR(el2_tlv)>0.8 and fatjet_tlv.Pt()>fatjet_maxpt:
                    fatjet_maxpt=fatjet_tlv.Pt()
                    fatjet_idx_H = i
                    valid_Higgs = True
            if not valid_Higgs:
                return False
                    
        elif self.isZtoNN:
            fatjet_maxpt = 0.
            for i,fatjet_tlv in enumerate(fatjet_tlv_list):
                if fatjet_tlv.Pt()>fatjet_maxpt:
                    fatjet_maxpt=fatjet_tlv.Pt()
                    fatjet_idx_H = i

        ############  AK4 Jet       ###########
        for ijet in range(event.nJet):
            jet_pt = event.Jet_pt[ijet]
            jet_eta = event.Jet_eta[ijet]
            jet_phi = event.Jet_phi[ijet]
            jet_mass = event.Jet_mass[ijet]
            jet_tlv = ROOT.TLorentzVector()
            jet_tlv.SetPtEtaPhiM(jet_pt,jet_eta,jet_phi,jet_mass)
            self.HT += jet_pt
            if jet_eta > -2.5 and jet_eta < -1.479 and jet_phi > -1.55 and jet_phi < -0.9:
                if self.HT_HEM15_16 == -1.:
                    self.HT_HEM15_16 = 0.
                self.HT_HEM15_16 += jet_pt
            if jet_pt > ak4_pt_cut and abs(jet_eta) < ak4_eta_cut:
                cleanJet = True
                for loose_electrons_tlv in loose_electrons_tlv_list:
                    if loose_electrons_tlv.DeltaR(jet_tlv) < 0.4:
                        cleanJet = False
                for loose_muons_tlv in loose_muons_tlv_list:
                    if loose_muons_tlv.DeltaR(jet_tlv) < 0.4:
                        cleanJet = False
                if cleanJet and getJetID(self.year,event,ijet):
                    if len(fatjet_tlv_list) > 0 and fatjet_tlv_list[fatjet_idx_H].DeltaR(jet_tlv) > 1.2:
                        jet_tlv_list.append(jet_tlv)
                        idx_jet.append(ijet)

        ############  AK4 Jet check for VBF       ###########
        if self.isZtoMM:
            lep1_tlv = mu1_tlv
            lep2_tlv = mu2_tlv
        if self.isZtoEE:
            lep1_tlv = el1_tlv
            lep2_tlv = el2_tlv
        
        for ijet in range(event.nJet):
            jet_pt = event.Jet_pt[ijet]
            jet_eta = event.Jet_eta[ijet]
            jet_phi = event.Jet_phi[ijet]
            jet_mass = event.Jet_mass[ijet]
            jet_tlv = ROOT.TLorentzVector()
            jet_tlv.SetPtEtaPhiM(jet_pt,jet_eta,jet_phi,jet_mass)
            if abs(jet_eta) < 5.0:
                if len(fatjet_tlv_list) > 0:
                    if fatjet_tlv_list[fatjet_idx_H].DeltaR(jet_tlv) > 1.2:
                        if getJetID(self.year,event,ijet) and event.Jet_puId[ijet]>4:
                            if self.isZtoMM or self.isZtoEE:
                                if jet_tlv.DeltaR(lep1_tlv)>0.4 and jet_tlv.DeltaR(lep2_tlv)>0.4:
                                    jet_tlv_list_vbf.append(jet_tlv)
                                    idx_jet_vbf.append(ijet) 
                            elif self.isZtoNN:
                                jet_tlv_list_vbf.append(jet_tlv)
                                idx_jet_vbf.append(ijet) 

        idx1_vbf = -1
        idx2_vbf = -1
        maxVBFmass = -1.
        for ijet1, jet1_tlv in enumerate(jet_tlv_list_vbf):
            for ijet2, jet2_tlv in enumerate(jet_tlv_list_vbf):
                if ijet1 == ijet2: continue
                eta1 = jet_tlv_list_vbf[ijet1].Eta()
                eta2 = jet_tlv_list_vbf[ijet2].Eta()
                V_VBF = jet_tlv_list_vbf[ijet1]+jet_tlv_list_vbf[ijet2]
                VBFmass = V_VBF.M()
                if abs(eta1-eta2)>4.0 and eta1*eta2<0. and VBFmass>maxVBFmass:
                    idx1_vbf = ijet1
                    idx2_vbf = ijet2
                    maxVBFmass = VBFmass
                   

        self.dijet_VBF_mass = maxVBFmass
        if maxVBFmass > 500.:        
            self.isVBF = True
            self.Jet1_VBF_pt = jet_tlv_list_vbf[idx1_vbf].Pt()
            self.Jet1_VBF_eta = jet_tlv_list_vbf[idx1_vbf].Eta()
            self.Jet1_VBF_phi = jet_tlv_list_vbf[idx1_vbf].Phi()
            self.Jet1_VBF_mass = jet_tlv_list_vbf[idx1_vbf].M()
            self.Jet2_VBF_pt = jet_tlv_list_vbf[idx2_vbf].Pt()
            self.Jet2_VBF_eta = jet_tlv_list_vbf[idx2_vbf].Eta()
            self.Jet2_VBF_phi = jet_tlv_list_vbf[idx2_vbf].Phi()
            self.Jet2_VBF_mass = jet_tlv_list_vbf[idx2_vbf].M()
            self.deltaR_VBF = jet_tlv_list_vbf[idx1_vbf].DeltaR(jet_tlv_list_vbf[idx2_vbf])
            self.deltaR_HVBFjet1 = (fatjet_tlv_list[fatjet_idx_H].DeltaR(jet_tlv_list_vbf[idx1_vbf]))
            self.deltaR_HVBFjet2 = (fatjet_tlv_list[fatjet_idx_H].DeltaR(jet_tlv_list_vbf[idx2_vbf]))

        ##########   Higgs      ########  
        H = fatjet_tlv_list[fatjet_idx_H]

        if self.isMC:
            self.H_mass_jmsUp =  event.FatJet_mass_jmsUp[fatjet_idx_H]
            self.H_mass_jmsDown = event.FatJet_mass_jmsDown[fatjet_idx_H]
            self.H_mass_jmrUp = event.FatJet_mass_jmrUp[fatjet_idx_H]
            self.H_mass_jmrDown = event.FatJet_mass_jmrDown[fatjet_idx_H]
            self.H_pt_jesUp = event.FatJet_pt_jesTotalUp[fatjet_idx_H]
            self.H_pt_jesDown = event.FatJet_pt_jesTotalDown[fatjet_idx_H]
            self.H_pt_jerUp = event.FatJet_pt_jerUp[fatjet_idx_H]
            self.H_pt_jerDown = event.FatJet_pt_jerDown[fatjet_idx_H]
            self.MET_pt_jesUp = event.MET_pt_jesTotalUp
            self.MET_pt_jesDown = event.MET_pt_jesTotalDown
            self.MET_pt_jerUp = event.MET_pt_jerUp
            self.MET_pt_jerDown = event.MET_pt_jerDown
            
    
            H_Eta = H.Eta()
            H_Phi = H.Phi()
            H_M = H.M()
            H_jesUp = fatjet_tlv_list[fatjet_idx_H]
            H_jesDown = fatjet_tlv_list[fatjet_idx_H]
            H_jerUp = fatjet_tlv_list[fatjet_idx_H]
            H_jerDown = fatjet_tlv_list[fatjet_idx_H]
            H_jesUp.SetPtEtaPhiM(self.H_pt_jesUp,H_Eta,H_Phi,H_M)
            H_jesDown.SetPtEtaPhiM(self.H_pt_jesDown,H_Eta,H_Phi,H_M)
            H_jerUp.SetPtEtaPhiM(self.H_pt_jerUp,H_Eta,H_Phi,H_M)
            H_jerDown.SetPtEtaPhiM(self.H_pt_jerDown,H_Eta,H_Phi,H_M)
            MET_jesUp = ROOT.TLorentzVector()
            MET_jesDown = ROOT.TLorentzVector()
            MET_jerUp = ROOT.TLorentzVector()
            MET_jerDown = ROOT.TLorentzVector()
            MET_jesUp.SetPtEtaPhiM(self.MET_pt_jesUp,0.,event.MET_phi,self.MET_pt_jesUp)
            MET_jesDown.SetPtEtaPhiM(self.MET_pt_jesDown,0.,event.MET_phi,self.MET_pt_jesDown)
            MET_jerUp.SetPtEtaPhiM(self.MET_pt_jerUp,0.,event.MET_phi,self.MET_pt_jerUp)
            MET_jerDown.SetPtEtaPhiM(self.MET_pt_jerDown,0.,event.MET_phi,self.MET_pt_jerDown)

        for ifatjet in idx_fatjet:
            if event.FatJet_btagHbb[ifatjet] > 0.3:
                self.isBoosted4B = True

                
        self.nJetsNoFatJet = len(jet_tlv_list)
        
        if self.isZtoNN:
            self.DPhi = abs(MET_tlv.DeltaPhi(H))
        else:
            self.DPhi = abs(V.DeltaPhi(H))
        
        self.VH_deltaR = H.DeltaR(V)
        
        jet_list_temp = []
        for ijet in range(event.nJet):
            jet_pt = event.Jet_pt[ijet]
            jet_eta = event.Jet_eta[ijet]
            jet_phi = event.Jet_phi[ijet]
            jet_mass = event.Jet_mass[ijet]
            jet_tlv = ROOT.TLorentzVector()
            jet_tlv.SetPtEtaPhiM(jet_pt,jet_eta,jet_phi,jet_mass)
            if jet_tlv.DeltaR(H) < 0.8:
                jet_list_temp.append(ijet)
        if len(jet_list_temp) == 1:
            idx = jet_list_temp[0]
            self.H_chf = event.Jet_chHEF[idx]
            self.H_nhf = event.Jet_neHEF[idx]
        elif len(jet_list_temp) == 2:
            idx1 = jet_list_temp[0]
            idx2 = jet_list_temp[1]
            pt1 = event.Jet_pt[idx1]
            pt2 = event.Jet_pt[idx2]
            chf1 = event.Jet_chHEF[idx1]
            chf2 = event.Jet_chHEF[idx2]
            nhf1 = event.Jet_neHEF[idx1]
            nhf2 = event.Jet_neHEF[idx2]
            self.H_chf = (chf1*pt1+chf2*pt2)/(pt1+pt2) 
            self.H_nhf = (nhf1*pt1+nhf2*pt2)/(pt1+pt2)
        elif len(jet_list_temp) == 3:
            idx1 = jet_list_temp[0]
            idx2 = jet_list_temp[1]
            idx3 = jet_list_temp[2]
            pt1 = event.Jet_pt[idx1]
            pt2 = event.Jet_pt[idx2]
            pt3 = event.Jet_pt[idx3]
            chf1 = event.Jet_chHEF[idx1]
            chf2 = event.Jet_chHEF[idx2]
            chf3 = event.Jet_chHEF[idx3]
            nhf1 = event.Jet_neHEF[idx1]
            nhf2 = event.Jet_neHEF[idx2]
            nhf3 = event.Jet_neHEF[idx3]
            self.H_chf = (chf1*pt1+chf2*pt2+chf3*pt3)/(pt1+pt2+pt3) 
            self.H_nhf = (nhf1*pt1+nhf2*pt2+nhf3*pt3)/(pt1+pt2+pt3)



        for jet_tlv in jet_tlv_list:
            if abs(MET_tlv.DeltaPhi(jet_tlv)) < self.MinJetMetDPhi:
                self.MinJetMetDPhi = abs(MET_tlv.DeltaPhi(jet_tlv))


        for ijet in idx_jet:
            if event.Jet_btagDeepB[ijet] > self.MaxJetNoFatJetBTag:
                self.MaxJetNoFatJetBTag = event.Jet_btagDeepB[ijet]

        if not self.isData:
            for igenjet in range(event.nGenJetAK8):
                genjetAK8_tlv = ROOT.TLorentzVector()
                genjetAK8_tlv.SetPtEtaPhiM(event.GenJetAK8_pt[igenjet], event.GenJetAK8_eta[igenjet], event.GenJetAK8_phi[igenjet], event.GenJetAK8_mass[igenjet])
                if H.DeltaR(genjetAK8_tlv) < 0.8:
                    self.H_hadronflavour = struct.unpack('B',event.GenJetAK8_hadronFlavour[igenjet])[0]
                    self.H_partonflavour = event.GenJetAK8_partonFlavour[igenjet]

            self.btagToolAK8.fillEfficiencies(event,idx_fatjet)
            self.btagToolAK8_deep.fillEfficiencies(event,idx_fatjet)
            self.btagToolAK4.fillEfficiencies(event,idx_jet)
            self.btagToolAK4_deep.fillEfficiencies(event,idx_jet)
            self.BTagAK8Weight  = self.btagToolAK8.getWeight(event,idx_fatjet)
            self.BTagAK4Weight  = self.btagToolAK4.getWeight(event,idx_jet)
            self.BTagAK8Weight_deep  = self.btagToolAK8_deep.getWeight(event,idx_fatjet)
            self.BTagAK8Weight_deep_up  = self.btagToolAK8_deep_up.getWeight(event,idx_fatjet)
            self.BTagAK8Weight_deep_down  = self.btagToolAK8_deep_down.getWeight(event,idx_fatjet)
            self.BTagAK4Weight_deep  = self.btagToolAK4_deep.getWeight(event,idx_jet)
            self.BTagAK4Weight_deep_up  = self.btagToolAK4_deep_up.getWeight(event,idx_jet)
            self.BTagAK4Weight_deep_down  = self.btagToolAK4_deep_down.getWeight(event,idx_jet)
        ###########     X   and variables   ############
        X = V + H
        if self.isZtoNN:
            X_chs = V_chs + H
            self.X_mass_chs = X_chs.M()

        if self.isMC:
            X_jesUp = V + H_jesUp
            X_jesDown = V + H_jesDown
            X_jerUp = V + H_jerUp
            X_jerDown = V + H_jerDown
            X_MET_jesUp = MET_jesUp + H_jesUp
            X_MET_jesDown = MET_jesDown + H_jesDown
            X_MET_jerUp = MET_jerUp + H_jerUp
            X_MET_jerDown = MET_jerDown + H_jerDown
            self.X_mass_jesUp = X_jesUp.M()
            self.X_mass_jesDown = X_jesDown.M()
            self.X_mass_jerUp = X_jerUp.M()
            self.X_mass_jerDown = X_jerDown.M()
            self.X_mass_MET_jesUp = X_MET_jesUp.M()
            self.X_mass_MET_jesDown = X_MET_jesDown.M()
            self.X_mass_MET_jerUp = X_MET_jerUp.M()
            self.X_mass_MET_jerDown = X_MET_jerDown.M()

        self.V_pt  = V.Pt()
        self.V_eta = V.Eta()
        self.V_phi = V.Phi()
        self.V_mass = V.M()
        
        if self.isZtoNN:
            self.V_mass = 0.

        self.H_pt = H.Pt()
        self.H_eta = H.Eta()
        self.H_phi = H.Phi()
        self.H_M = H.M()
        self.H_mass = event.FatJet_msoftdrop[fatjet_idx_H]
        self.X_pt = X.Pt()
        self.X_eta = X.Eta()
        self.X_phi = X.Phi()
        self.X_mass = X.M()


        self.H_dbt = event.FatJet_btagHbb[fatjet_idx_H]
        self.BtagDeepB = event.FatJet_btagDeepB[fatjet_idx_H]
        self.DeepTagMD_H4qvsQCD = event.FatJet_deepTagMD_H4qvsQCD[fatjet_idx_H]
        self.DeepTagMD_HbbvsQCD = event.FatJet_deepTagMD_HbbvsQCD[fatjet_idx_H]
        self.DeepTagMD_ZHbbvsQCD = event.FatJet_deepTagMD_ZHbbvsQCD[fatjet_idx_H]
        self.DeepTagMD_ZbbvsQCD = event.FatJet_deepTagMD_ZbbvsQCD[fatjet_idx_H]
        self.DeepTagMD_bbvsLight = event.FatJet_deepTagMD_bbvsLight[fatjet_idx_H]
        self.DeepTagMD_WvsQCD = event.FatJet_deepTagMD_WvsQCD[fatjet_idx_H]
        self.DeepTagMD_ZvsQCD = event.FatJet_deepTagMD_ZvsQCD[fatjet_idx_H]
        self.H_tau21 = fatjet_tau21_list[fatjet_idx_H]
        self.H_tau41 = fatjet_tau41_list[fatjet_idx_H]
        self.H_tau42 = fatjet_tau42_list[fatjet_idx_H]
        self.H_tau31 = fatjet_tau31_list[fatjet_idx_H]
        self.H_tau32 = fatjet_tau32_list[fatjet_idx_H]
        self.VHDEta = abs(V.Eta() - H.Eta())

        
            
        if event.FatJet_subJetIdx1[fatjet_idx_H] >= 0:
            Hcsv1 = event.SubJet_btagCSVV2[event.FatJet_subJetIdx1[fatjet_idx_H]]
            Hdeepcsv1 = event.SubJet_btagDeepB[event.FatJet_subJetIdx1[fatjet_idx_H]]
        else:
            Hcsv1 = -1.
            Hdeepcsv1 = -1.
        if event.FatJet_subJetIdx2[fatjet_idx_H] >= 0:
            Hcsv2 = event.SubJet_btagCSVV2[event.FatJet_subJetIdx2[fatjet_idx_H]]
            Hdeepcsv2 = event.SubJet_btagDeepB[event.FatJet_subJetIdx2[fatjet_idx_H]]
        else:
            Hcsv2 = -1.
            Hdeepcsv2 = -1.
        
        self.H_csv1 = max(Hcsv1,Hcsv2)
        self.H_csv2 = min(Hcsv1,Hcsv2)
        self.H_deepcsv1 = max(Hdeepcsv1,Hdeepcsv2)
        self.H_deepcsv2 = min(Hdeepcsv1,Hdeepcsv2)


        if self.year == 2016:
            wp_loose = 0.2217
            wp_medium = 0.6321
            wp_tight = 0.8953
        elif self.year == 2017:
            wp_loose = 0.1522
            wp_medium = 0.4941
            wp_tight = 0.8001
        elif self.year == 2018:
            wp_loose = 0.1241
            wp_medium = 0.4184
            wp_tight = 0.7527

        if self.H_deepcsv2 > wp_loose:
            self.isHtobb = True
        if self.H_deepcsv1 > wp_medium and self.H_deepcsv2 > wp_loose:
            self.isHtobb_ml = True

        if self.MaxJetNoFatJetBTag > wp_loose:
            self.isMaxBTag_loose = True
        if self.MaxJetNoFatJetBTag > wp_medium:
            self.isMaxBTag_medium = True
        if self.MaxJetNoFatJetBTag > wp_tight:
            self.isMaxBTag_tight = True

        self.H_ntag = fatjet_nbtag_list[fatjet_idx_H]
        
        if self.H_mass != 0.:
            self.H_ddt = self.H_tau21 + 0.082 *np.log(self.H_mass*self.H_mass/self.H_pt)
        else:
            self.H_ddt = -1.
            
        self.X_tmass = np.sqrt(2.*V.Pt()*fatjet_tlv_list[fatjet_idx_H].Pt()*(1.-np.cos(fatjet_tlv_list[fatjet_idx_H].DeltaPhi(V))))
        if self.isZtoNN:
            self.X_mass = self.X_tmass
        else:
            self.X_mass = X.M()
        if self.X_mass > 750 and self.VH_deltaR > 2:
            if self.MinJetMetDPhi>0.5 and self.DPhi>2:
                for i,weight in enumerate(nncutflow_list):
                    self.out.nncutflow_inc.Fill(i,weight)
            if self.VHDEta<1.3:
                for i,weight in enumerate(eecutflow_list):
                    self.out.eecutflow_inc.Fill(i,weight)
                for i,weight in enumerate(mmcutflow_list):
                    self.out.mmcutflow_inc.Fill(i,weight)

        if self.isZtoEE or self.isZtoMM or self.isZtoNN or self.isTtoEM:
            self.fillBranches(event)
            return True
    


    
