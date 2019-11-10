#! /usr/bin/env python

deepFlavour = {
'loose': {'2016': 0.0614, '2017': 0.0521, '2018': 0.0494, 'run2':0.0494},
'medium': {'2016': 0.3093, '2017': 0.3033, '2018': 0.2770, 'run2':0.2770},
'tight': {'2016': 0.7221, '2017': 0.7489, '2018': 0.7264, 'run2':0.7264}  ## FIXME run2 needs to be taken care of sometime FIXME
}

#alias = {
#   "preselection" : "jj_mass>1400 && jpt_1>600 && jj_deltaEta<1.3 && (HLT_PFHT1050 || HLT_PFHT900 || HLT_PFJet500 || HLT_PFJet550 || HLT_CaloJet500_NoJetID || HLT_CaloJet550_NoJetID || HLT_AK8PFJet500 || HLT_AK8PFJet550)",
#   "2b" : "jj_mass>1400 && jpt_1>600 && jj_deltaEta<1.3 && (HLT_PFHT1050 || HLT_PFHT900 || HLT_PFJet500 || HLT_PFJet550 || HLT_CaloJet500_NoJetID || HLT_CaloJet550_NoJetID || HLT_AK8PFJet500 || HLT_AK8PFJet550) && jdeepFlavour_1>0.7264 && jdeepFlavour_2>0.7264",
#   "1b" : "jj_mass>1400 && jpt_1>600 && jj_deltaEta<1.3 && (HLT_PFHT1050 || HLT_PFHT900 || HLT_PFJet500 || HLT_PFJet550 || HLT_CaloJet500_NoJetID || HLT_CaloJet550_NoJetID || HLT_AK8PFJet500 || HLT_AK8PFJet550) && ((jdeepFlavour_1>0.7264 && jdeepFlavour_2<0.7264) || (jdeepFlavour_1<0.7264 && jdeepFlavour_2>0.7264))",
#}

alias = {
    "preselection" : "jj_mass>1400 && jpt_1>600 && jj_deltaEta<1.3 && (HLT_PFHT1050 || HLT_PFHT900 || HLT_PFJet500 || HLT_PFJet550 || HLT_CaloJet500_NoJetID || HLT_CaloJet550_NoJetID || HLT_AK8PFJet500 || HLT_AK8PFJet550)",
    "2b" : "jj_mass>1400 && jpt_1>600 && jj_deltaEta<1.3 && (HLT_PFHT1050 || HLT_PFHT900 || HLT_PFJet500 || HLT_PFJet550 || HLT_CaloJet500_NoJetID || HLT_CaloJet550_NoJetID || HLT_AK8PFJet500 || HLT_AK8PFJet550) && jdeepFlavour_1>{b_threshold} && jdeepFlavour_2>{b_threshold}",
    "1b" : "jj_mass>1400 && jpt_1>600 && jj_deltaEta<1.3 && (HLT_PFHT1050 || HLT_PFHT900 || HLT_PFJet500 || HLT_PFJet550 || HLT_CaloJet500_NoJetID || HLT_CaloJet550_NoJetID || HLT_AK8PFJet500 || HLT_AK8PFJet550) && ((jdeepFlavour_1>{b_threshold} && jdeepFlavour_2<{b_threshold}) || (jdeepFlavour_1<{b_threshold} && jdeepFlavour_2>{b_threshold}))",
}


alias["bb"] = alias["2b"]
alias["bq"] = alias["1b"]
alias["qq"] = alias["preselection"]

