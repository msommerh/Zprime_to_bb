import numpy as num
from ROOT import TTree, TFile, TH1D, TH2D

root_dtype = {
  float: 'D',  int: 'I',  bool: 'O',
  'f':   'D',  'i': 'I',  '?':  'O',  'b': 'b',
}

num_dtype = {
  'D':   'f',  'I': 'i',  'O':  '?',  'b': 'b'
}


class TreeProducerCommon(object):
    """Class to create a custom output file & tree; as well as create and contain branches."""
    
    def __init__(self, name, dataType, **kwargs):
        print 'TreeProducerCommon is called for', name
        
        self.name       = name
        self._isData    = dataType=='data'
        self.doJECSys   = kwargs.get('doJECSys', True ) and not self._isData
        ###self.isVectorLQ = kwargs.get('isVectorLQ', 'VectorLQ' in self.name )
        
        # TREE
        self.outputfile = TFile(name, 'RECREATE')
        self.tree       = TTree('tree','tree')
        
        # HISTOGRAM
        self.cutflow = TH1D('cutflow', 'cutflow',  25, 0,  25)
        self.pileup  = TH1D('pileup',  'pileup',  100, 0, 100)
        
        #### CHECK genPartFlav
        ###self.flags_LTF_DM1 = TH1D('flags_LTF_DM1', "flags for l #rightarrow #tau_{h}, DM1", 18, 0, 18)
        ###self.flags_LTF_DM0 = TH1D('flags_LTF_DM0', "flags for l #rightarrow #tau_{h}, DM0", 18, 0, 18)
        ###self.flags_LTF_mis = TH1D('flags_LTF_mis', "flags for l #rightarrow #tau_{h}, DM1, wrong genPartFlav", 18, 0, 18)
        ###self.flags_LTF_DM1_sn1 = TH1D('flags_LTF_DM1_sn1', "flags for l #rightarrow #tau_{h}, DM1 (status!=1)", 18, 0, 18)
        ###self.flags_LTF_DM0_sn1 = TH1D('flags_LTF_DM0_sn1', "flags for l #rightarrow #tau_{h}, DM0 (status!=1)", 18, 0, 18)
        ###self.flags_LTF_mis_sn1 = TH1D('flags_LTF_mis_sn1', "flags for l #rightarrow #tau_{h}, DM1, wrong genPartFlav (status!=1)", 18, 0, 18)
        ###for hist in [self.flags_LTF_DM1, self.flags_LTF_DM0, self.flags_LTF_mis, self.flags_LTF_DM0_sn1, self.flags_LTF_DM1_sn1, self.flags_LTF_mis_sn1]:
        ###  hist.GetXaxis().SetBinLabel( 1,  "isPrompt"                            )
        ###  hist.GetXaxis().SetBinLabel( 2,  "isDirectPromptTauDecayProduct"       )
        ###  hist.GetXaxis().SetBinLabel( 3,  "isHardProcess"                       )
        ###  hist.GetXaxis().SetBinLabel( 4,  "fromHardProcess"                     )
        ###  hist.GetXaxis().SetBinLabel( 5,  "isDirectHardProcessTauDecayProduct"  )
        ###  hist.GetXaxis().SetBinLabel( 6,  "fromHardProcessBeforeFSR"            )
        ###  hist.GetXaxis().SetBinLabel( 7,  "isFirstCopy"                         )
        ###  hist.GetXaxis().SetBinLabel( 8,  "isLastCopy"                          )
        ###  hist.GetXaxis().SetBinLabel( 9,  "isLastCopyBeforeFSR"                 )
        ###  hist.GetXaxis().SetBinLabel(10,  "status==1"                           )
        ###  hist.GetXaxis().SetBinLabel(11,  "status==23"                          )
        ###  hist.GetXaxis().SetBinLabel(12,  "status==44"                          )
        ###  hist.GetXaxis().SetBinLabel(13,  "status==51"                          )
        ###  hist.GetXaxis().SetBinLabel(14,  "status==52"                          )
        ###  hist.GetXaxis().SetBinLabel(15,  "other status"                        )
        ###  hist.GetXaxis().SetLabelSize(0.041)
        ###self.genmatch_corr     = TH2D("genmatch_corr","correlation between Tau_genPartFlav and genmatch",6,0,6,6,0,6)
        ###self.genmatch_corr_DM0 = TH2D("genmatch_corr_DM0","correlation between Tau_genPartFlav and genmatch for DM0",6,0,6,6,0,6)
        ###self.genmatch_corr_DM1 = TH2D("genmatch_corr_DM1","correlation between Tau_genPartFlav and genmatch for DM1",6,0,6,6,0,6)
        
        
        #############
        #   EVENT   #
        #############
        
        self.addBranch('run',                     'i')
        self.addBranch('lumi',                    'i')
        self.addBranch('event',                   'i')
        self.addBranch('isData',                  '?', self._isData)
        
        self.addBranch('npvs',                    'i')
        self.addBranch('npvsGood',                'i')
        self.addBranch('metfilter',               '?')
        
        if not self._isData:
          self.addBranch('nPU',                   'i', -1)
          self.addBranch('nTrueInt',              'i', -1)
          self.addBranch('LHE_Njets',             'i', -1)
        
        
        ##############
        #   WEIGHT   #
        ##############
        
        if not self._isData:
          self.addBranch('weight',                'f', 1.)
          self.addBranch('genweight',             'f', 1.)
          self.addBranch('trigweight',            'f', 1.)
          self.addBranch('puweight',              'f', 1.)
          self.addBranch('idisoweight_1',         'f', 1.)
          self.addBranch('idisoweight_2',         'f', 1.)
          self.addBranch('zptweight',             'f', 1.)
          self.addBranch('ttptweight',            'f', 1.)
          self.addBranch('btagweight',            'f', 1.)
          self.addBranch('btagweight_loose',      'f', 1.)
          self.addBranch('btagweight50',          'f', 1.)
          self.addBranch('btagweight50_loose',    'f', 1.)
        
        
        ############
        #   JETS   #
        ############
        
        self.addBranch('njets',                   'i')
        self.addBranch('njets50',                 'i')
        self.addBranch('ncjets',                  'i')
        self.addBranch('nfjets',                  'i')
        self.addBranch('nbtag',                   'i')
        self.addBranch('nbtag50',                 'i')
        self.addBranch('nbtag_loose',             'i')
        self.addBranch('nbtag50_loose',           'i')
        
        self.addBranch('jpt_1',                   'f')
        self.addBranch('jeta_1',                  'f')
        self.addBranch('jphi_1',                  'f')
        self.addBranch('jdeepb_1',                'f')
        self.addBranch('jpt_2',                   'f')
        self.addBranch('jeta_2',                  'f')
        self.addBranch('jphi_2',                  'f')
        self.addBranch('jdeepb_2',                'f')
        
        self.addBranch('bpt_1',                   'f')
        self.addBranch('beta_1',                  'f')
        self.addBranch('bpt_2',                   'f')
        self.addBranch('beta_2',                  'f')
        
        if self.doJECSys:
          for uncertainty in ['jer','jes']:
            for variation in ['Down','Up']:
              label = '_'+uncertainty+variation
              self.addBranch('njets'+label,         'i')
              self.addBranch('njets50'+label,       'i')
              self.addBranch('nbtag50'+label,       'i')
              self.addBranch('nbtag50_loose'+label, 'i')
              self.addBranch('jpt_1'+label,         'f')
              self.addBranch('jpt_2'+label,         'f')
        
        self.addBranch('met',                     'f')
        self.addBranch('metphi',                  'f')
        ###self.addBranch('puppimet',                'f')
        ###self.addBranch('puppimetphi',             'f')
        ###self.addBranch('metsignificance',         'f')
        ###self.addBranch('metcovXX',                'f')
        ###self.addBranch('metcovXY',                'f')
        ###self.addBranch('metcovYY',                'f')
        ###self.addBranch('fixedGridRhoFastjetAll',  'f')
        if not self._isData:
          self.addBranch('genmet',                'f', -1)
          self.addBranch('genmetphi',             'f', -9)
        
        
        #############
        #   OTHER   #
        #############
        
        self.addBranch('pfmt_1',                  'f')
        self.addBranch('pfmt_2',                  'f')
        self.addBranch('m_vis',                   'f')
        self.addBranch('pt_ll',                   'f')
        self.addBranch('dR_ll',                   'f')
        self.addBranch('dphi_ll',                 'f')
        self.addBranch('deta_ll',                 'f')
        self.addBranch('chi',                     'f')
        
        self.addBranch('pzetamiss',               'f')
        self.addBranch('pzetavis',                'f')
        self.addBranch('dzeta',                   'f')
        
        if self.doJECSys:
          for uncertainty in ['jer','jes','unclEn']:
            for variation in ['Down','Up']:
              label = '_'+uncertainty+variation
              self.addBranch('met'+label,         'f')
              self.addBranch('pfmt_1'+label,      'f')
              self.addBranch('dzeta'+label,       'f')
        
        self.addBranch('dilepton_veto',           '?')
        self.addBranch('extraelec_veto',          '?')
        self.addBranch('extramuon_veto',          '?')
        self.addBranch('lepton_vetos',            '?')
        self.addBranch('lepton_vetos_noTau',      '?')
        
        if not self._isData:
          ###self.addBranch('ngentauhads',           'i', -1)
          ###self.addBranch('ngentaus',              'i', -1)
          self.addBranch('m_genboson',            'f', -1)
          self.addBranch('pt_genboson',           'f', -1)
          ###if self.isVectorLQ:
          ###  self.addBranch('ntops',               'i', -1)
        
        ###self.addBranch('m_taub',                  'f')
        ###self.addBranch('m_taumub',                'f')
        ###self.addBranch('m_tauj',                  'f')
        ###self.addBranch('m_muj',                   'f')
        ###self.addBranch('m_coll_muj',              'f')
        ###self.addBranch('m_coll_tauj',             'f')
        ###self.addBranch('mt_coll_muj',             'f')
        ###self.addBranch('mt_coll_tauj',            'f')
        ###self.addBranch('m_max_lj',                'f')
        ###self.addBranch('m_max_lb',                'f')
        ###self.addBranch('m_mub',                   'f')
        
    
    def addBranch(self, name, dtype='f', default=None):
        """Add branch with a given name, and create an array of the same name as address."""
        if hasattr(self,name):
          print "ERROR! TreeProducerCommon.addBranch: Branch of name '%s' already exists!"%(name)
          exit(1)
        if isinstance(dtype,str):
          if dtype.lower()=='f': # 'f' is only a 'float32', and 'F' is a 'complex64', which do not work for filling float branches
            dtype = float        # float is a 'float64' ('f8')
          elif dtype.lower()=='i': # 'i' is only a 'int32'
            dtype = int            # int is a 'int64' ('i8')
        setattr(self,name,num.zeros(1,dtype=dtype))
        self.tree.Branch(name, getattr(self,name), '%s/%s'%(name,root_dtype[dtype]))
        if default!=None:
          getattr(self,name)[0] = default
        
    
    def endJob(self):
        """Write and close files after the job ends."""
        self.outputfile.Write()
        self.outputfile.Close()
        

