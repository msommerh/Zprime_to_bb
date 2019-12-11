from ROOT import TFile, TTree, TLorentzVector, TObject, TH1, TH1D, TF1, TH1F
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from TreeProducerCommon import TreeProducerCommon
#from PileupWeightTool import PileupWeightTool
import math

class TreeProducerObjectCounter(TreeProducerCommon):
    """Class to create a custom output file & tree; as well as create and contain branches."""
    
    def __init__(self, name, object_list):
        
        print 'TreeProducerZprimetobb is called', name
        self.name       = name
        self.outputfile = TFile(name, 'RECREATE')

        for obj in object_list: 
            exec "self.{obj} = TH1F('{obj}', '{obj}', 1,0,1)".format(obj=obj)

        self.all_events = TH1F('all_events', 'all_events',1,0,1)
 
    def endJob(self):
        self.outputfile.Write()
        self.outputfile.Close()


class ObjectCounterProducer(Module):
    """Simple module to test postprocessing."""
    
    def __init__(self, name, object_list, **kwargs):
        self.name = name
        self.object_list = object_list
        self.out  = TreeProducerObjectCounter(name, object_list)

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

        ######################### using this space for a quick test FIXME FIXME FIXME

        passedMETFilters = False
        try:
                if True \
                    and event.Flag_goodVertices \
                    and event.Flag_globalSuperTightHalo2016Filter \
                    and event.Flag_BadPFMuonFilter \
                    and event.Flag_EcalDeadCellTriggerPrimitiveFilter \
                    and event.Flag_HBHENoiseFilter \
                    and event.Flag_HBHENoiseIsoFilter \
                    and event.Flag_ecalBadCalibFilter:
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

        j1_p4 = TLorentzVector()
        j1_p4.SetPtEtaPhiM(event.Jet_pt[jetIds[0]], event.Jet_eta[jetIds[0]], event.Jet_phi[jetIds[0]], event.Jet_mass[jetIds[0]])
        j2_p4 = TLorentzVector()
        j2_p4.SetPtEtaPhiM(event.Jet_pt[jetIds[1]], event.Jet_eta[jetIds[1]], event.Jet_phi[jetIds[1]], event.Jet_mass[jetIds[1]])
        self.jj_mass       = (j1_p4+j2_p4).M()       

        if self.jj_mass < 800: return False

        nIsoElectrons = 0.
        if event.nElectron>0: print "event.nElectron", event.nElectron
        for iel in range(event.nElectron):
            if event.Electron_pt[iel] > 20:      
                print "event.Electron_pt[iel] > 20" 
            if abs(event.Electron_eta[iel]) < 2.5:
                print "abs(event.Electron_eta[iel]) < 2.5"
            if event.Electron_cutBased[iel] >= 1:
                print "event.Electron_cutBased[iel] >= 1"
            if event.Electron_pt[iel] > 20. and abs(event.Electron_eta[iel]) < 2.5 and event.Electron_cutBased[iel] >= 1:
                print "passes all!!!"
            if event.Electron_pt[iel] > 20. and abs(event.Electron_eta[iel]) < 2.5 and event.Electron_cutBased[iel] >= 1: nIsoElectrons += 1

        nIsoMuons = 0.
        if event.nMuon>0: print "event.nMuon", event.nMuon
        for imu in range(event.nMuon):
            if event.Muon_pt[imu] > 20.:
                print "event.Muon_pt[imu] > 20." 
            if abs(event.Muon_eta[imu]) < 2.4:
                print "abs(event.Muon_eta[imu]) < 2.4"
            if event.Muon_pfIsoId[imu] >= 2:
                print "event.Muon_pfIsoId[imu] >= 2"
            if event.Muon_pt[imu] > 20. and abs(event.Muon_eta[imu]) < 2.4 and event.Muon_looseId[imu] and event.Muon_pfIsoId[imu] >= 2:
                print "passes all!!!"

            if event.Muon_pt[imu] > 20. and abs(event.Muon_eta[imu]) < 2.4 and event.Muon_looseId[imu] and event.Muon_pfIsoId[imu] >= 2: nIsoMuons += 1

        ######################### ending quick test FIXME FIXME FIXME


        for obj in self.object_list:
            cmd_search = "obj_exists = event.{obj} != 0 and event.{obj} != -1".format(obj=obj)
            cmd_fill = "self.out.{obj}.Fill(0.)".format(obj=obj)

            try:
                exec cmd_search
            except RuntimeError:
                obj_exists = False
            if obj_exists:
                exec cmd_fill
            
        return True
        
