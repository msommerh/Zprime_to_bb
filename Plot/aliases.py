#! /usr/bin/env python

alias = {
   "preselection" : "jj_mass>1200 && jpt_1>600 && jj_deltaEta<1.3 && (HLT_PFHT1050 || HLT_PFHT900 || HLT_PFJet500 || HLT_PFJet550 || HLT_CaloJet500_NoJetID || HLT_CaloJet550_NoJetID || HLT_AK8PFJet500 || HLT_AK8PFJet550)",
   "2b" : "jj_mass>1200 && jpt_1>600 && jj_deltaEta<1.3 && (HLT_PFHT1050 || HLT_PFHT900 || HLT_PFJet500 || HLT_PFJet550 || HLT_CaloJet500_NoJetID || HLT_CaloJet550_NoJetID || HLT_AK8PFJet500 || HLT_AK8PFJet550) && jdeepFlavour_1>0.7264 && jdeepFlavour_2>0.7264",
   "1b" : "jj_mass>1200 && jpt_1>600 && jj_deltaEta<1.3 && (HLT_PFHT1050 || HLT_PFHT900 || HLT_PFJet500 || HLT_PFJet550 || HLT_CaloJet500_NoJetID || HLT_CaloJet550_NoJetID || HLT_AK8PFJet500 || HLT_AK8PFJet550) && ((jdeepFlavour_1>0.7264 && jdeepFlavour_2<0.7264) || (jdeepFlavour_1<0.7264 && jdeepFlavour_2>0.7264))",
}




