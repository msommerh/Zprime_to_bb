#!/bin/bash

masses=(1200 1300 1400 1500 1600 1700 1800 1900 2000 2100 2200 2300 2400 2500 2600 2700 2800 2900 3000 3100 3200 3300 3400 3500 3600 3700 3800 3900 4000 4100 4200 4300 4400 4500 4600 4700 4800 4900 5000 5100 5200 5300 5400 5500 5600 5700 5800 5900 6000 6100 6200 6300 6400 6500 6600 6700 6800 6900 7000 7100 7200 7300 7400 7500 7600 7700 7800 7900 8000)

########## input arguments ########## 
isMC=$1
year=$2
btagging=$3
mass_nr=$4
#####################################

mass=${masses[${mass_nr}]}

if [[ $year == run2c ]]; then
    echo "Combining the 2016-2018 fits separately into a single limit..."
    year="run2"
    combined=1
else
    combined=0
fi

echo "isMC = ${isMC}"
echo "year = ${year}"
echo "btagging = ${btagging}"
echo "mass_nr = ${mass_nr}"
echo "mass = ${mass}"
echo "combined = ${combined}"

if [[ $isMC -eq 1 ]]; then
    echo "running purely on MC..."
    suffix="_MC.txt"
    prefix="MC_QCD_TTbar"
else
    echo "running on real data..."
    suffix=".txt"
    prefix="data"
fi


## setting up a repository structure on the local working node:

echo "mkdir datacards"
echo "mkdir datacards/${btagging}"
echo "mkdir datacards/${btagging}/combined"
echo "mkdir workspace"
echo "mkdir workspace/${btagging}"

if [[ $combined -eq 1 ]]; then
    echo "cp /afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/src/NanoTreeProducer/datacards/${btagging}/combined/fully_combined_run2_M${mass}${suffix} datacards/${btagging}/combined/"
    echo "cp /afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/src/NanoTreeProducer/workspace/${btagging}/MC_signal_201* workspace/${btagging}/"
    echo "cp /afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/src/NanoTreeProducer/workspace/${btagging}/${prefix}_201* workspace/${btagging}/"
else
    echo "cp /afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/src/NanoTreeProducer/datacards/${btagging}/combined/combined_${year}_M${mass}${suffix} datacards/${btagging}/combined/"
    echo "cp /afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/src/NanoTreeProducer/workspace/${btagging}/MC_signal_${year}* workspace/${btagging}/"
    echo "cp /afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/src/NanoTreeProducer/workspace/${btagging}/${prefix}_${year}* workspace/${btagging}/"
fi

echo "ls datacards/${btagging}/combined/"
#ls datacards/${btagging}/combined/
echo "ls workspace/${btagging}/"
#ls workspace/${btagging}/


if [[ $combined -eq 1 ]]; then
   echo "fully combined" 
else
    echo "not fully combined"
fi

