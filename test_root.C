{
    TFile f("/afs/cern.ch/work/m/msommerh/public/Zprime_to_bb_Analysis/Skim_test/data_2018_A.root", "READ");
    TIter next(f.GetListOfKeys());
    TKey *key;
    while ((key=(TKey*)next())){
        printf("key: %s points to an object of class: %s at %lld \n",
        key->GetName(),
        key->GetClassName(), key->GetSeekKey());
    }
}
