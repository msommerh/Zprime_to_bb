#! /usr/bin/env python

deepFlavour = {
'loose': {'2016': 0.0614, '2017': 0.0521, '2018': 0.0494, 'run2':0.0494},
'medium': {'2016': 0.3093, '2017': 0.3033, '2018': 0.2770, 'run2':0.2770},
'tight': {'2016': 0.7221, '2017': 0.7489, '2018': 0.7264, 'run2':0.7264}  ## FIXME run2 needs to be taken care of sometime FIXME
}

working_points = {'loose': 1, 'medium': 2, 'tight': 3}

#alias = {
#    "preselection" : "jj_mass_widejet>1800 && jpt_1>600 && jj_deltaEta<1.1 && (HLT_PFHT1050 || HLT_PFHT900 || HLT_PFJet500 || HLT_PFJet550 || HLT_CaloJet500_NoJetID || HLT_CaloJet550_NoJetID || HLT_AK8PFJet500 || HLT_AK8PFJet550)",
#    "2b" : "jj_mass_widejet>1800 && jpt_1>600 && jj_deltaEta<1.1 && (HLT_PFHT1050 || HLT_PFHT900 || HLT_PFJet500 || HLT_PFJet550 || HLT_CaloJet500_NoJetID || HLT_CaloJet550_NoJetID || HLT_AK8PFJet500 || HLT_AK8PFJet550) && jdeepFlavour_1>{b_threshold} && jdeepFlavour_2>{b_threshold}",
#    "1b" : "jj_mass_widejet>1800 && jpt_1>600 && jj_deltaEta<1.1 && (HLT_PFHT1050 || HLT_PFHT900 || HLT_PFJet500 || HLT_PFJet550 || HLT_CaloJet500_NoJetID || HLT_CaloJet550_NoJetID || HLT_AK8PFJet500 || HLT_AK8PFJet550) && ((jdeepFlavour_1>{b_threshold} && jdeepFlavour_2<{b_threshold}) || (jdeepFlavour_1<{b_threshold} && jdeepFlavour_2>{b_threshold}))",
#}
#
#aliasSM = { ## a new btagging category that is semi medium, semi loose. Written for the direct b-tagging via the deepJet variable
#    "preselection" : "jj_mass_widejet>1800 && jpt_1>600 && jj_deltaEta<1.1 && (HLT_PFHT1050 || HLT_PFHT900 || HLT_PFJet500 || HLT_PFJet550 || HLT_CaloJet500_NoJetID || HLT_CaloJet550_NoJetID || HLT_AK8PFJet500 || HLT_AK8PFJet550)",
#    "2b" : "jj_mass_widejet>1800 && jpt_1>600 && jj_deltaEta<1.1 && (HLT_PFHT1050 || HLT_PFHT900 || HLT_PFJet500 || HLT_PFJet550 || HLT_CaloJet500_NoJetID || HLT_CaloJet550_NoJetID || HLT_AK8PFJet500 || HLT_AK8PFJet550) && jdeepFlavour_1>{b_threshold_medium} && jdeepFlavour_2>{b_threshold_loose}",
#    "1b" : "jj_mass_widejet>1800 && jpt_1>600 && jj_deltaEta<1.1 && (HLT_PFHT1050 || HLT_PFHT900 || HLT_PFJet500 || HLT_PFJet550 || HLT_CaloJet500_NoJetID || HLT_CaloJet550_NoJetID || HLT_AK8PFJet500 || HLT_AK8PFJet550) && ((jdeepFlavour_1>{b_threshold_medium} && jdeepFlavour_2<{b_threshold_loose}) || (jdeepFlavour_1<{b_threshold_loose} && jdeepFlavour_2>{b_threshold_medium}))",
#}


alias = { ## the same as above with the new btag_WP variable
    "preselection" : "jj_mass_widejet>1800 && jpt_1>600 && jj_deltaEta<1.1 && (HLT_PFHT1050 || HLT_PFHT900 || HLT_PFJet500 || HLT_PFJet550 || HLT_CaloJet500_NoJetID || HLT_CaloJet550_NoJetID || HLT_AK8PFJet500 || HLT_AK8PFJet550)",
    "2b" : "jj_mass_widejet>1800 && jpt_1>600 && jj_deltaEta<1.3 && (HLT_PFHT1050 || HLT_PFHT900 || HLT_PFJet500 || HLT_PFJet550 || HLT_CaloJet500_NoJetID || HLT_CaloJet550_NoJetID || HLT_AK8PFJet500 || HLT_AK8PFJet550) && jbtag_WP_1>={WP} && jbtag_WP_2>={WP}",
    "1b" : "jj_mass_widejet>1800 && jpt_1>600 && jj_deltaEta<1.3 && (HLT_PFHT1050 || HLT_PFHT900 || HLT_PFJet500 || HLT_PFJet550 || HLT_CaloJet500_NoJetID || HLT_CaloJet550_NoJetID || HLT_AK8PFJet500 || HLT_AK8PFJet550) && ((jbtag_WP_1>={WP} && jbtag_WP_2<{WP}) || (jbtag_WP_1<{WP} && jbtag_WP_2>={WP}))",
}

aliasSM = { ## a new btagging category that is semi medium, semi loose.
    "preselection" : "jj_mass_widejet>1800 && jpt_1>600 && jj_deltaEta<1.1 && (HLT_PFHT1050 || HLT_PFHT900 || HLT_PFJet500 || HLT_PFJet550 || HLT_CaloJet500_NoJetID || HLT_CaloJet550_NoJetID || HLT_AK8PFJet500 || HLT_AK8PFJet550)",
    "2b" : "jj_mass_widejet>1800 && jpt_1>600 && jj_deltaEta<1.1 && (HLT_PFHT1050 || HLT_PFHT900 || HLT_PFJet500 || HLT_PFJet550 || HLT_CaloJet500_NoJetID || HLT_CaloJet550_NoJetID || HLT_AK8PFJet500 || HLT_AK8PFJet550) && ((jbtag_WP_1>=2 && jbtag_WP_2>=1) || (jbtag_WP_1>=1 && jbtag_WP_2>=2))",
    "1b" : "jj_mass_widejet>1800 && jpt_1>600 && jj_deltaEta<1.1 && (HLT_PFHT1050 || HLT_PFHT900 || HLT_PFJet500 || HLT_PFJet550 || HLT_CaloJet500_NoJetID || HLT_CaloJet550_NoJetID || HLT_AK8PFJet500 || HLT_AK8PFJet550) && ((jbtag_WP_1>=2 && jbtag_WP_2<1) || (jbtag_WP_1<1 && jbtag_WP_2>=2))",
}

alias["bb"] = alias["2b"]
alias["bq"] = alias["1b"]
alias["qq"] = alias["preselection"]

aliasSM["bb"] = aliasSM["2b"]
aliasSM["bq"] = aliasSM["1b"]
aliasSM["qq"] = aliasSM["preselection"]


