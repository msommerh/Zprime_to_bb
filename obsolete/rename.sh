#! /bin/bash

function cutoff {
    let n=${#1}-1
    echo ${1:0:$n}
    }

echo "starting renaming"
path="/eos/user/m/msommerh/Zprime_to_bb_analysis/"

directories=$(ls -d ${path}2016*/)
n=${#path}
#echo "path length: $n"
let n2=${n}+5
#echo "got the value ${n2}"
#echo "intermediate step"
for i in $directories; do
    n3="MC_signal_2016_${i:${n2}}"
    rm "${path}${n3}2016_$(cutoff ${i:${n2}})_flatTuple2_0.root"
done
echo "end"


#/eos/user/m/msommerh/Zprime_to_bb_analysis/
#
#2016_M1000                MC_QCD_2017_HT300to500    MC_signal_2017_M5500  backup_during_resubmission
#2016_M3000                MC_QCD_2017_HT500to700    MC_signal_2017_M600   data_2016_B
#2016_M4000                MC_QCD_2017_HT50to100     MC_signal_2017_M6000  data_2016_C
#2016_M500                 MC_QCD_2017_HT700to1000   MC_signal_2017_M7000  data_2016_D
#2016_M5000                MC_QCD_2018_HT1000to1500  MC_signal_2017_M800   data_2016_E
#2016_M6000                MC_QCD_2018_HT100to200    MC_signal_2017_M8000  data_2016_F
#2016_M7000                MC_QCD_2018_HT1500to2000  MC_signal_2018_M1000  data_2016_G
#2016_M8000                MC_QCD_2018_HT2000toInf   MC_signal_2018_M1200  data_2016_H
#2016_M9000
