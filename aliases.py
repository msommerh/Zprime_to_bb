#! /usr/bin/env python

###
### contains the selections for each b-tagging category, as well as the pre-selection
###

dijet_bins = [1, 3, 6, 10, 16, 23, 31, 40, 50, 61, 74, 88, 103, 119, 137, 156, 176, 197, 220, 244, 270, 296, 325, 354, 386, 419, 453, 489, 526, 565, 606, 649, 693, 740, 788, 838, 890, 944, 1000, 1058, 1118, 1181, 1246, 1313, 1383, 1455, 1530, 1607, 1687, 1770, 1856, 1945, 2037, 2132, 2231, 2332, 2438, 2546, 2659, 2775, 2895, 3019, 3147, 3279, 3416, 3558, 3704, 3854, 4010, 4171, 4337, 4509, 4686, 4869, 5058, 5253, 5455, 5663, 5877, 6099, 6328, 6564, 6808, 7060, 7320, 7589, 7866, 8152, 8447, 8752, 9067, 9391, 9726, 10072, 10430, 10798, 11179, 11571, 11977, 12395, 12827, 13272, 13732, 14000]

working_points = {'loose': 1, 'medium': 2, 'tight': 3}

reduced_triggers = "(HLT_PFHT1050==1 || HLT_PFHT900==1 || HLT_PFJet500==1 || HLT_PFJet550==1 || HLT_CaloJet500_NoJetID==1 || HLT_CaloJet550_NoJetID==1 || HLT_AK8PFJet500==1 || HLT_AK8PFJet550==1)"

#triggers = "(HLT_PFHT1050==1 || HLT_PFHT900==1 || HLT_PFJet500==1 || HLT_PFJet550==1 || HLT_CaloJet500_NoJetID==1 || HLT_CaloJet550_NoJetID==1 || HLT_AK8PFJet500==1 || HLT_AK8PFJet550==1 || HLT_DoublePFJets100_CaloBTagDeepCSV_p71==1 || HLT_DoublePFJets116MaxDeta1p6_DoubleCaloBTagDeepCSV_p71==1 || HLT_DoublePFJets128MaxDeta1p6_DoubleCaloBTagDeepCSV_p71==1 || HLT_DoublePFJets200_CaloBTagDeepCSV_p71==1 || HLT_DoublePFJets350_CaloBTagDeepCSV_p71==1 || HLT_DoublePFJets40_CaloBTagDeepCSV_p71==1)"
triggers = "(HLT_PFHT1050==1 || HLT_PFHT900==1 || HLT_PFJet500==1 || HLT_PFJet550==1 || HLT_CaloJet500_NoJetID==1 || HLT_CaloJet550_NoJetID==1 || HLT_AK8PFJet500==1 || HLT_AK8PFJet550==1)"

triggers_PFHT   = "(HLT_PFHT1050==1 || HLT_PFHT900==1)"
triggers_Jet    = "(HLT_PFJet500==1 || HLT_PFJet550==1 || HLT_CaloJet500_NoJetID==1 || HLT_CaloJet550_NoJetID==1 || HLT_AK8PFJet500==1 || HLT_AK8PFJet550==1)"
triggers_BTag   = "(HLT_DoublePFJets100_CaloBTagDeepCSV_p71==1 || HLT_DoublePFJets116MaxDeta1p6_DoubleCaloBTagDeepCSV_p71==1 || HLT_DoublePFJets128MaxDeta1p6_DoubleCaloBTagDeepCSV_p71==1 || HLT_DoublePFJets200_CaloBTagDeepCSV_p71==1 || HLT_DoublePFJets350_CaloBTagDeepCSV_p71==1 || HLT_DoublePFJets40_CaloBTagDeepCSV_p71==1)"

AK8veto = " && !(fatjetmass_1>65 && fatjetmass_2>65)"
electronVeto = " && nelectrons<1"
muonVeto = " && nmuons<1"

tight_jetID = " && jid_1>5 && jid_2>5"

preselection = "jj_mass_widejet>1530 && jj_deltaEta_widejet<1.1 && "

alias = { 
    "preselection_noveto" : "jj_mass_widejet>1530 && jj_deltaEta_widejet<1.1"+tight_jetID+" && "+reduced_triggers,
    "preselection" : preselection+triggers+tight_jetID+AK8veto+electronVeto+muonVeto,
    "2b" : preselection+triggers+tight_jetID+AK8veto+electronVeto+muonVeto+" && jbtag_WP_1>={WP} && jbtag_WP_2>={WP}",
    "1b" : preselection+triggers+tight_jetID+AK8veto+electronVeto+muonVeto+" && ((jbtag_WP_1>={WP} && jbtag_WP_2<{WP}) || (jbtag_WP_1<{WP} && jbtag_WP_2>={WP}))",
    #"2mu": preselection+triggers+tight_jetID+AK8veto+electronVeto+muonVeto+" && jbtag_WP_1<{WP} && jbtag_WP_2<{WP} && jnmuons_1>0 && jnmuons_2>0"
    "2mu": preselection+triggers+tight_jetID+AK8veto+electronVeto+muonVeto+" && jbtag_WP_1<{WP} && jbtag_WP_2<{WP} && (jnmuons_loose_1>0 || jnmuons_loose_2>0)",
    #"2mu": preselection+triggers+tight_jetID+AK8veto+electronVeto+muonVeto+" && jbtag_WP_1<{WP} && jbtag_WP_2<{WP} && (jnmuons_medium_1>0 || jnmuons_medium_2>0)" ## changing to medium muon WP
    "2mu_gen": preselection+triggers+tight_jetID+AK8veto+electronVeto+muonVeto+" && jbtag_WP_1<{WP} && jbtag_WP_2<{WP} && ((jnmuons_loose_1>0 && jnmuons_loose_genmatched_1>0) || (jnmuons_loose_2>0 && jnmuons_loose_genmatched_2>0))",
    "2mu_inclpt": preselection+triggers+tight_jetID+AK8veto+electronVeto+muonVeto+" && jbtag_WP_1<{WP} && jbtag_WP_2<{WP} && ((jnmuons_loose_1>0 && jmuon_gen_reco_dR_1<99) || (jnmuons_loose_2>0 && jmuon_gen_reco_dR_2<99))",
    "2mu_lowpt_1": preselection+triggers+tight_jetID+AK8veto+electronVeto+muonVeto+" && jbtag_WP_1<{WP} && jbtag_WP_2<{WP} && (jnmuons_loose_1>0 || jnmuons_loose_2>0) && jpt_1<500 && jmuon_gen_reco_dR_1<99",# && jnmuons_gen_1>1 && jnmuons_gen_pt_1>5",# && jmuon_gen_reco_dR_1<99",
    "2mu_medpt_1": preselection+triggers+tight_jetID+AK8veto+electronVeto+muonVeto+" && jbtag_WP_1<{WP} && jbtag_WP_2<{WP} && (jnmuons_loose_1>0 || jnmuons_loose_2>0) && jpt_1>500 && jmuon_gen_reco_dR_1<99",# && jpt_1<1500 && jnmuons_gen_1>1 && jnmuons_gen_pt_1>5",# && jmuon_gen_reco_dR_1<99",
    "2mu_highpt_1": preselection+triggers+tight_jetID+AK8veto+electronVeto+muonVeto+" && jbtag_WP_1<{WP} && jbtag_WP_2<{WP} && (jnmuons_loose_1>0 || jnmuons_loose_2>0) && jpt_1>1500 && jmuon_gen_reco_dR_1<99",# && jnmuons_gen_1>1 && jnmuons_gen_pt_1>5",# && jmuon_gen_reco_dR_1<99",
    "2mu_lowpt_2": preselection+triggers+tight_jetID+AK8veto+electronVeto+muonVeto+" && jbtag_WP_1<{WP} && jbtag_WP_2<{WP} && (jnmuons_loose_1>0 || jnmuons_loose_2>0) && jpt_2<500 && jmuon_gen_reco_dR_2<99",# && jnmuons_gen_2>1 && jnmuons_gen_pt_2>5",# && jmuon_gen_reco_dR_2<99",
    "2mu_medpt_2": preselection+triggers+tight_jetID+AK8veto+electronVeto+muonVeto+" && jbtag_WP_1<{WP} && jbtag_WP_2<{WP} && (jnmuons_loose_1>0 || jnmuons_loose_2>0) && jpt_2>500 && jmuon_gen_reco_dR_2<99",# && jnmuons_gen_2>1 && jnmuons_gen_pt_2>5",# && jpt_2<1500 && jmuon_gen_reco_dR_2<99",
    "2mu_highpt_2": preselection+triggers+tight_jetID+AK8veto+electronVeto+muonVeto+" && jbtag_WP_1<{WP} && jbtag_WP_2<{WP} && (jnmuons_loose_1>0 || jnmuons_loose_2>0) && jpt_2>1500 && jmuon_gen_reco_dR_2<99",# && jnmuons_gen_2>1 && jnmuons_gen_pt_2>5",# && jmuon_gen_reco_dR_2<99",
}

aliasSM = { ## a new btagging category that is semi medium, semi loose. DEPRECATED
    "preselection_noveto" : "jj_mass_widejet>1530 && jj_deltaEta_widejet<1.1"+tight_jetID,
    "preselection" : preselection+triggers+tight_jetID+AK8veto+electronVeto+muonVeto,
    "2b" : preselection+triggers+tight_jetID+AK8veto+electronVeto+muonVeto+" && ((jbtag_WP_1>=2 && jbtag_WP_2>=1) || (jbtag_WP_1>=1 && jbtag_WP_2>=2))",
    "1b" : preselection+triggers+tight_jetID+AK8veto+electronVeto+muonVeto+" && ((jbtag_WP_1>=2 && jbtag_WP_2<1) || (jbtag_WP_1<1 && jbtag_WP_2>=2))",
    "2mu": preselection+triggers+tight_jetID+AK8veto+electronVeto+muonVeto+" && jbtag_WP_1<2 && jbtag_WP_2<2 && jnmuons_1>0 && jnmuons_2>0"
}


WP_deepCSV = {}
WP_deepCSV['loose'] = {'2016':0.2217, '2017':0.1522, '2018':0.1241}
WP_deepCSV['medium'] = {'2016':0.6321, '2017':0.4941, '2018':0.4184}
alias_deepCSV = { 
    "preselection_noveto" : "jj_mass_widejet>1530 && jj_deltaEta_widejet<1.1"+tight_jetID+" && "+reduced_triggers,
    "preselection" : preselection+triggers+tight_jetID+AK8veto+electronVeto+muonVeto,
    "2b" : preselection+triggers+tight_jetID+AK8veto+electronVeto+muonVeto+" && jdeepCSV_1>={WP} && jdeepCSV_2>={WP}",
    "1b" : preselection+triggers+tight_jetID+AK8veto+electronVeto+muonVeto+" && ((jdeepCSV_1>={WP} && jdeepCSV_2<{WP}) || (jdeepCSV_1<{WP} && jdeepCSV_2>={WP}))",
    "2mu": preselection+triggers+tight_jetID+AK8veto+electronVeto+muonVeto+" && jdeepCSV_1<{WP} && jdeepCSV_2<{WP} && jnmuons_1>0 && jnmuons_2>0"
}

alias["bb"] = alias["2b"]
alias["bq"] = alias["1b"]
alias["mumu"] = alias["2mu"]
alias["qq"] = alias["preselection"]
alias['none'] = 'jj_deltaEta<1.1'

aliasSM["bb"] = aliasSM["2b"]
aliasSM["bq"] = aliasSM["1b"]
aliasSM["mumu"] = aliasSM["2mu"]
aliasSM["qq"] = aliasSM["preselection"]
aliasSM['none'] = 'jj_deltaEta<1.1'

alias_deepCSV["bb"]     = alias_deepCSV["2b"]
alias_deepCSV["bq"]     = alias_deepCSV["1b"]
alias_deepCSV["mumu"]   = alias_deepCSV["2mu"]
alias_deepCSV["qq"]     = alias_deepCSV["preselection"]
alias_deepCSV['none']   = 'jj_deltaEta<1.1'


additional_selections = {"": "", "AK8veto": " && !(fatjetmass_1>65 && fatjetmass_2>65)", "electronVeto": " && nelectrons<1", "muonVeto": " && nmuons<1"}

additional_selections['leptonVeto'] = additional_selections['electronVeto']+additional_selections['muonVeto']
additional_selections['fullVeto'] = additional_selections['AK8veto']+additional_selections['leptonVeto']


#bias_functions = { ## old bias study only comparing to the +1 param functino of the same family
#    "2016": { "bb":   "CMS2016_bb_p2_1  flatParam\nCMS2016_bb_p2_2  flatParam\nCMS2016_bb_p3_1  flatParam\nCMS2016_bb_p3_2  flatParam\nCMS2016_bb_p3_3  flatParam\n",
#              "bq":   "CMS2016_bq_p2_1  flatParam\nCMS2016_bq_p2_2  flatParam\nCMS2016_bq_p3_1  flatParam\nCMS2016_bq_p3_2  flatParam\nCMS2016_bq_p3_3  flatParam\n",
#              "mumu": "CMS2016_mumu_p3_1  flatParam\nCMS2016_mumu_p3_2  flatParam\nCMS2016_mumu_p3_3  flatParam\nCMS2016_mumu_p4_1  flatParam\nCMS2016_mumu_p4_2  flatParam\nCMS2016_mumu_p4_3  flatParam\nCMS2016_mumu_p4_4  flatParam\n"
#        },
#    "2017": { "bb":   "CMS2017_bb_p3_1  flatParam\nCMS2017_bb_p3_2  flatParam\nCMS2017_bb_p3_3  flatParam\nCMS2017_bb_p4_1  flatParam\nCMS2017_bb_p4_2  flatParam\nCMS2017_bb_p4_3  flatParam\nCMS2017_bb_p4_4  flatParam\n",
#              "bq":   "CMS2017_bq_p2_1  flatParam\nCMS2017_bq_p2_2  flatParam\nCMS2017_bq_p3_1  flatParam\nCMS2017_bq_p3_2  flatParam\nCMS2017_bq_p3_3  flatParam\n",
#              "mumu": "CMS2017_mumu_p2_1  flatParam\nCMS2017_mumu_p2_2  flatParam\nCMS2017_mumu_p3_1  flatParam\nCMS2017_mumu_p3_2  flatParam\nCMS2017_mumu_p3_3  flatParam\n"
#        },
#    "2018": { "bb":   "CMS2018_bb_p2_1  flatParam\nCMS2018_bb_p2_2  flatParam\nCMS2018_bb_p3_1  flatParam\nCMS2018_bb_p3_2  flatParam\nCMS2018_bb_p3_3  flatParam\n",
#              "bq":   "CMS2018_bq_p2_1  flatParam\nCMS2018_bq_p2_2  flatParam\nCMS2018_bq_p3_1  flatParam\nCMS2018_bq_p3_2  flatParam\nCMS2018_bq_p3_3  flatParam\n",
#              "mumu": "CMS2018_mumu_p2_1  flatParam\nCMS2018_mumu_p2_2  flatParam\nCMS2018_mumu_p3_1  flatParam\nCMS2018_mumu_p3_2  flatParam\nCMS2018_mumu_p3_3  flatParam\n"
#        }
#    }

#bias_functions = { ## newer bias study comparing also to two other families of functions but with the same number of parameters
#    "2016": { "bb":   "CMS2016_bb_p2_1  flatParam\nCMS2016_bb_p2_2  flatParam\nCMS2016_bb_p3_1  flatParam\nCMS2016_bb_p3_2  flatParam\nCMS2016_bb_p3_3  flatParam\nCMS2016_bb_exp_p2_1  flatParam\nCMS2016_bb_exp_p2_2  flatParam\nCMS2016_bb_atlas_p2_1  flatParam\nCMS2016_bb_atlas_p2_2  flatParam\n",
#              "bq":   "CMS2016_bq_p2_1  flatParam\nCMS2016_bq_p2_2  flatParam\nCMS2016_bq_p3_1  flatParam\nCMS2016_bq_p3_2  flatParam\nCMS2016_bq_p3_3  flatParam\nCMS2016_bq_exp_p2_1  flatParam\nCMS2016_bq_exp_p2_2  flatParam\nCMS2016_bq_atlas_p2_1  flatParam\nCMS2016_bq_atlas_p2_2  flatParam\n",
#              "mumu": "CMS2016_mumu_p3_1  flatParam\nCMS2016_mumu_p3_2  flatParam\nCMS2016_mumu_p3_3  flatParam\nCMS2016_mumu_p4_1  flatParam\nCMS2016_mumu_p4_2  flatParam\nCMS2016_mumu_p4_3  flatParam\nCMS2016_mumu_p4_4  flatParam\nCMS2016_mumu_exp_p3_1  flatParam\nCMS2016_mumu_exp_p3_2  flatParam\nCMS2016_mumu_exp_p3_3  flatParam\nCMS2016_mumu_atlas_p3_1  flatParam\nCMS2016_mumu_atlas_p3_2  flatParam\nCMS2016_mumu_atlas_p3_3  flatParam\n"
#        },
#    "2017": { "bb":   "CMS2017_bb_p3_1  flatParam\nCMS2017_bb_p3_2  flatParam\nCMS2017_bb_p3_3  flatParam\nCMS2017_bb_p4_1  flatParam\nCMS2017_bb_p4_2  flatParam\nCMS2017_bb_p4_3  flatParam\nCMS2017_bb_p4_4  flatParam\nCMS2017_bb_exp_p3_1  flatParam\nCMS2017_bb_exp_p3_2  flatParam\nCMS2017_bb_exp_p3_3  flatParam\nCMS2017_bb_atlas_p3_1  flatParam\nCMS2017_bb_atlas_p3_2  flatParam\nCMS2017_bb_atlas_p3_3  flatParam\n",
#              "bq":   "CMS2017_bq_p2_1  flatParam\nCMS2017_bq_p2_2  flatParam\nCMS2017_bq_p3_1  flatParam\nCMS2017_bq_p3_2  flatParam\nCMS2017_bq_p3_3  flatParam\nCMS2017_bq_exp_p2_1  flatParam\nCMS2017_bq_exp_p2_2  flatParam\nCMS2017_bq_atlas_p2_1  flatParam\nCMS2017_bq_atlas_p2_2  flatParam\n",
#              "mumu": "CMS2017_mumu_p2_1  flatParam\nCMS2017_mumu_p2_2  flatParam\nCMS2017_mumu_p3_1  flatParam\nCMS2017_mumu_p3_2  flatParam\nCMS2017_mumu_p3_3  flatParam\nCMS2017_mumu_exp_p2_1  flatParam\nCMS2017_mumu_exp_p2_2  flatParam\nCMS2017_mumu_atlas_p2_1  flatParam\nCMS2017_mumu_atlas_p2_2  flatParam\n"
#        },
#    "2018": { "bb":   "CMS2018_bb_p2_1  flatParam\nCMS2018_bb_p2_2  flatParam\nCMS2018_bb_p3_1  flatParam\nCMS2018_bb_p3_2  flatParam\nCMS2018_bb_p3_3  flatParam\nCMS2018_bb_exp_p2_1  flatParam\nCMS2018_bb_exp_p2_2  flatParam\nCMS2018_bb_atlas_p2_1  flatParam\nCMS2018_bb_atlas_p2_2  flatParam\n",
#              "bq":   "CMS2018_bq_p2_1  flatParam\nCMS2018_bq_p2_2  flatParam\nCMS2018_bq_p3_1  flatParam\nCMS2018_bq_p3_2  flatParam\nCMS2018_bq_p3_3  flatParam\nCMS2018_bq_exp_p2_1  flatParam\nCMS2018_bq_exp_p2_2  flatParam\nCMS2018_bq_atlas_p2_1  flatParam\nCMS2018_bq_atlas_p2_2  flatParam\n",
#              "mumu": "CMS2018_mumu_p2_1  flatParam\nCMS2018_mumu_p2_2  flatParam\nCMS2018_mumu_p3_1  flatParam\nCMS2018_mumu_p3_2  flatParam\nCMS2018_mumu_p3_3  flatParam\nCMS2018_mumu_exp_p2_1  flatParam\nCMS2018_mumu_exp_p2_2  flatParam\nCMS2018_mumu_atlas_p2_1  flatParam\nCMS2018_mumu_atlas_p2_2  flatParam\n"
#        }
#    }

bias_functions = { ## newest bias study comparing also to two other families of functions with independent F-tests
    "2016": { "bb":   "CMS2016_bb_p2_1  flatParam\nCMS2016_bb_p2_2  flatParam\nCMS2016_bb_p3_1  flatParam\nCMS2016_bb_p3_2  flatParam\nCMS2016_bb_p3_3  flatParam\nCMS2016_bb_exp_p4_1  flatParam\nCMS2016_bb_exp_p4_2  flatParam\nCMS2016_bb_exp_p4_3  flatParam\nCMS2016_bb_exp_p4_4  flatParam\nCMS2016_bb_atlas_p2_1  flatParam\nCMS2016_bb_atlas_p2_2  flatParam\n",
              "bq":   "CMS2016_bq_p2_1  flatParam\nCMS2016_bq_p2_2  flatParam\nCMS2016_bq_p3_1  flatParam\nCMS2016_bq_p3_2  flatParam\nCMS2016_bq_p3_3  flatParam\nCMS2016_bq_exp_p2_1  flatParam\nCMS2016_bq_exp_p2_2  flatParam\nCMS2016_bq_atlas_p3_1  flatParam\nCMS2016_bq_atlas_p3_2  flatParam\nCMS2016_bq_atlas_p3_3  flatParam\n",
              "mumu": "CMS2016_mumu_p3_1  flatParam\nCMS2016_mumu_p3_2  flatParam\nCMS2016_mumu_p3_3  flatParam\nCMS2016_mumu_p4_1  flatParam\nCMS2016_mumu_p4_2  flatParam\nCMS2016_mumu_p4_3  flatParam\nCMS2016_mumu_p4_4  flatParam\nCMS2016_mumu_exp_p2_1  flatParam\nCMS2016_mumu_exp_p2_2  flatParam\nCMS2016_mumu_atlas_p4_1  flatParam\nCMS2016_mumu_atlas_p4_2  flatParam\nCMS2016_mumu_atlas_p4_3  flatParam\nCMS2016_mumu_atlas_p4_4  flatParam\n"
              #"bq":   "CMS2016_bq_p2_1  flatParam\nCMS2016_bq_p2_2  flatParam\nCMS2016_bq_p3_1  flatParam\nCMS2016_bq_p3_2  flatParam\nCMS2016_bq_p3_3  flatParam\nCMS2016_bq_exp_p3_1  flatParam\nCMS2016_bq_exp_p3_2  flatParam\nCMS2016_bq_exp_p3_3  flatParam\nCMS2016_bq_atlas_p3_1  flatParam\nCMS2016_bq_atlas_p3_2  flatParam\nCMS2016_bq_atlas_p3_3  flatParam\n",
              #"mumu": "CMS2016_mumu_p3_1  flatParam\nCMS2016_mumu_p3_2  flatParam\nCMS2016_mumu_p3_3  flatParam\nCMS2016_mumu_p4_1  flatParam\nCMS2016_mumu_p4_2  flatParam\nCMS2016_mumu_p4_3  flatParam\nCMS2016_mumu_p4_4  flatParam\nCMS2016_mumu_exp_p3_1  flatParam\nCMS2016_mumu_exp_p3_2  flatParam\nCMS2016_mumu_exp_p3_3  flatParam\nCMS2016_mumu_atlas_p4_1  flatParam\nCMS2016_mumu_atlas_p4_2  flatParam\nCMS2016_mumu_atlas_p4_3  flatParam\nCMS2016_mumu_atlas_p4_4  flatParam\n"
        },
    "2017": { "bb":   "CMS2017_bb_p3_1  flatParam\nCMS2017_bb_p3_2  flatParam\nCMS2017_bb_p3_3  flatParam\nCMS2017_bb_p4_1  flatParam\nCMS2017_bb_p4_2  flatParam\nCMS2017_bb_p4_3  flatParam\nCMS2017_bb_p4_4  flatParam\nCMS2017_bb_exp_p2_1  flatParam\nCMS2017_bb_exp_p2_2  flatParam\nCMS2017_bb_atlas_p3_1  flatParam\nCMS2017_bb_atlas_p3_2  flatParam\nCMS2017_bb_atlas_p3_3  flatParam\n",
              "bq":   "CMS2017_bq_p2_1  flatParam\nCMS2017_bq_p2_2  flatParam\nCMS2017_bq_p3_1  flatParam\nCMS2017_bq_p3_2  flatParam\nCMS2017_bq_p3_3  flatParam\nCMS2017_bq_exp_p3_1  flatParam\nCMS2017_bq_exp_p3_2  flatParam\nCMS2017_bq_exp_p3_3  flatParam\nCMS2017_bq_atlas_p3_1  flatParam\nCMS2017_bq_atlas_p3_2  flatParam\nCMS2017_bq_atlas_p3_3  flatParam\n",
              "mumu": "CMS2017_mumu_p2_1  flatParam\nCMS2017_mumu_p2_2  flatParam\nCMS2017_mumu_p3_1  flatParam\nCMS2017_mumu_p3_2  flatParam\nCMS2017_mumu_p3_3  flatParam\nCMS2017_mumu_exp_p3_1  flatParam\nCMS2017_mumu_exp_p3_2  flatParam\nCMS2017_mumu_exp_p3_3  flatParam\nCMS2017_mumu_atlas_p3_1  flatParam\nCMS2017_mumu_atlas_p3_2  flatParam\nCMS2017_mumu_atlas_p3_3  flatParam\n"
              #"bq":   "CMS2017_bq_p2_1  flatParam\nCMS2017_bq_p2_2  flatParam\nCMS2017_bq_p3_1  flatParam\nCMS2017_bq_p3_2  flatParam\nCMS2017_bq_p3_3  flatParam\nCMS2017_bq_exp_p2_1  flatParam\nCMS2017_bq_exp_p2_2  flatParam\nCMS2017_bq_atlas_p3_1  flatParam\nCMS2017_bq_atlas_p3_2  flatParam\nCMS2017_bq_atlas_p3_3  flatParam\n",
              #"mumu": "CMS2017_mumu_p2_1  flatParam\nCMS2017_mumu_p2_2  flatParam\nCMS2017_mumu_p3_1  flatParam\nCMS2017_mumu_p3_2  flatParam\nCMS2017_mumu_p3_3  flatParam\nCMS2017_mumu_exp_p2_1  flatParam\nCMS2017_mumu_exp_p2_2  flatParam\nCMS2017_mumu_atlas_p3_1  flatParam\nCMS2017_mumu_atlas_p3_2  flatParam\nCMS2017_mumu_atlas_p3_3  flatParam\n"
        },
    "2018": { "bb":   "CMS2018_bb_p2_1  flatParam\nCMS2018_bb_p2_2  flatParam\nCMS2018_bb_p3_1  flatParam\nCMS2018_bb_p3_2  flatParam\nCMS2018_bb_p3_3  flatParam\nCMS2018_bb_exp_p2_1  flatParam\nCMS2018_bb_exp_p2_2  flatParam\nCMS2018_bb_atlas_p3_1  flatParam\nCMS2018_bb_atlas_p3_2  flatParam\nCMS2018_bb_atlas_p3_3  flatParam\n",
              "bq":   "CMS2018_bq_p2_1  flatParam\nCMS2018_bq_p2_2  flatParam\nCMS2018_bq_p3_1  flatParam\nCMS2018_bq_p3_2  flatParam\nCMS2018_bq_p3_3  flatParam\nCMS2018_bq_exp_p2_1  flatParam\nCMS2018_bq_exp_p2_2  flatParam\nCMS2018_bq_atlas_p3_1  flatParam\nCMS2018_bq_atlas_p3_2  flatParam\nCMS2018_bq_atlas_p3_3  flatParam\n",
              "mumu": "CMS2018_mumu_p2_1  flatParam\nCMS2018_mumu_p2_2  flatParam\nCMS2018_mumu_p3_1  flatParam\nCMS2018_mumu_p3_2  flatParam\nCMS2018_mumu_p3_3  flatParam\nCMS2018_mumu_exp_p2_1  flatParam\nCMS2018_mumu_exp_p2_2  flatParam\nCMS2018_mumu_atlas_p3_1  flatParam\nCMS2018_mumu_atlas_p3_2  flatParam\nCMS2018_mumu_atlas_p3_3  flatParam\n"
              #"mumu": "CMS2018_mumu_p2_1  flatParam\nCMS2018_mumu_p2_2  flatParam\nCMS2018_mumu_p3_1  flatParam\nCMS2018_mumu_p3_2  flatParam\nCMS2018_mumu_p3_3  flatParam\nCMS2018_mumu_exp_p3_1  flatParam\nCMS2018_mumu_exp_p3_2  flatParam\nCMS2018_mumu_exp_p3_3  flatParam\nCMS2018_mumu_atlas_p3_1  flatParam\nCMS2018_mumu_atlas_p3_2  flatParam\nCMS2018_mumu_atlas_p3_3  flatParam\n"
        }
    }


bias_pulls = {
    '2sigma': { 
                1600: 106.,
                1700: 77.,
                1800: 51.,
                1900: 41.,
                2000: 35.,
                2100: 32.,
                2200: 28.,
                2300: 26.,
                2400: 23.,
                2500: 21.,
                2600: 20.,
                2700: 18.,
                2800: 17.,
                2900: 15.,
                3000: 14.,
                3100: 13.,
                3200: 13.,
                3300: 12.,
                3400: 11.,
                3500: 11.,
                3600: 10.,
                3700: 9.,
                3800: 9.,
                3900: 8.,
                4000: 8.,
                4100: 7.,
                4200: 7.,
                4300: 6.,
                4400: 6.,
                4500: 6.,
                4600: 5.,
                4700: 5.,
                4800: 4.,
                4900: 4.,
                5000: 4.,
                5100: 4.,
                5200: 3.,
                5300: 3.,
                5400: 3.,
                5500: 3.,
                5600: 2.,
                5700: 2.,
                5800: 2.,
                5900: 2.,
                6000: 2.,
                6100: 2.,
                6200: 1.,
                6300: 1.,
                6400: 1.,
                6500: 1.,
                6600: 1.,
                6700: 1.,
                6800: 1.,
                6900: 1.,
                7000: 1.,
                7100: 1.,
                7200: 1., 
                7300: 1.,
                7400: 1.,
                7500: 1.,
                7600: 1.,
                7700: 1.,
                7800: 1.,
                7900: 1.,
                8000: 1.,
            },
    '5sigma': { 
                1600: 264.,
                1700: 192.,
                1800: 128.,
                1900: 102.,
                2000: 88.,
                2100: 79.,
                2200: 71.,
                2300: 64.,
                2400: 58.,
                2500: 53.,
                2600: 49.,
                2700: 45.,
                2800: 41.,
                2900: 38.,
                3000: 36.,
                3100: 33.,
                3200: 31.,
                3300: 30.,
                3400: 28.,
                3500: 26.,
                3600: 25.,
                3700: 24.,
                3800: 23.,
                3900: 21.,
                4000: 20.,
                4100: 19.,
                4200: 17.,
                4300: 16.,
                4400: 15.,
                4500: 14.,
                4600: 13.,
                4700: 12.,
                4800: 11.,
                4900: 10.,
                5000: 9.,
                5100: 9.,
                5200: 8.,
                5300: 7.,
                5400: 7.,
                5500: 6.,
                5600: 6.,
                5700: 5.,
                5800: 5.,
                5900: 5.,
                6000: 4.,
                6100: 4.,
                6200: 4.,
                6300: 3.,
                6400: 3.,
                6500: 3.,
                6600: 3.,
                6700: 2.,
                6800: 2.,
                6900: 2.,
                7000: 2.,
                7100: 2.,
                7200: 2.,
                7300: 2.,
                7400: 2.,
                7500: 1.,
                7600: 1.,
                7700: 1.,
                7800: 1.,
                7900: 1.,
                8000: 1.,
            }
    }

