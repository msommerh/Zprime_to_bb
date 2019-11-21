#!/bin/bash

echo
echo
echo 'START---------------'
workdir=$(pwd)
echo "workdir = $workdir"
cd /afs/cern.ch/user/m/msommerh/CMSSW_10_2_13/src/HiggsAnalysis/CombinedLimit
eval `scram runtime -sh`
cd $workdir

export X509_USER_PROXY=/afs/cern.ch/user/m/msommerh/x509up_msommerh
use_x509userproxy=true

#option=""

masses=(1200 1300 1400 1500 1600 1700 1800 1900 2000 2100 2200 2300 2400 2500 2600 2700 2800 2900 3000 3100 3200 3300 3400 3500 3600 3700 3800 3900 4000 4100 4200 4300 4400 4500 4600 4700 4800 4900 5000 5100 5200 5300 5400 5500 5600 5700 5800 5900 6000 6100 6200 6300 6400 6500 6600 6700 6800 6900 7000 7100 7200 7300 7400 7500 7600 7700 7800 7900 8000)

########## input arguments ########## 
isMC=$1
year=$2
btagging=$3
mass_nr=$4
#####################################

mass=${masses[${mass_nr}]}

echo "isMC = ${isMC}"
echo "year = ${year}"
echo "btagging = ${btagging}"
echo "mass_nr = ${mass_nr}"
echo "mass = ${mass}"

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

mkdir datacards
mkdir datacards/${btagging}
mkdir datacards/${btagging}/combined
mkdir workspace
mkdir workspace/${btagging}

cp /afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/src/NanoTreeProducer/datacards/${btagging}/combined/fully_combined_run2_M${mass}${suffix} datacards/${btagging}/combined/ #FIXME remove "fully" sometime
cp /afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/src/NanoTreeProducer/workspace/${btagging}/MC_signal_201* workspace/${btagging}/
cp /afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/src/NanoTreeProducer/workspace/${btagging}/${prefix}_201* workspace/${btagging}/

echo "ls datacards/${btagging}/combined/"
ls datacards/${btagging}/combined/
echo "ls workspace/${btagging}/"
ls workspace/${btagging}/


#inputfile=/afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/src/NanoTreeProducer/datacards/${btagging}/combined/combined_${year}_M${mass}${suffix}
inputfile="datacards/${btagging}/combined/fully_combined_${year}_M${mass}${suffix}" #FIXME remove "fully" sometime
outputfile="/afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/src/NanoTreeProducer/combine/limits/${btagging}/combined_run2/" #FIXME remove "combined_run2/" sometime
tempfile=$(echo $inputfile | sed s:datacards/${btagging}/combined/fully_combined_:${workdir}/:g) #FIXME remove "fully" sometime
echo "inputfile = ${inputfile}"
echo "outputfile = ${outputfile}"
echo "tempfile = ${tempfile}"

> $tempfile

#echo "combine -M AsymptoticLimits -d ${inputfile} -m ${mass} | grep -e Observed -e Expected | awk '{print ${NF}}' >> ${tempfile}"
#combine -M AsymptoticLimits -d $inputfile -m $mass | grep -e Observed -e Expected | awk '{print $NF}' >> $tempfile
echo "combine -M AsymptoticLimits -d $inputfile -m $mass > tmp_stdout.txt"
combine -M AsymptoticLimits -d $inputfile -m $mass > tmp_stdout.txt
echo
echo
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "combine output:"
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo
cat tmp_stdout.txt
echo
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo
echo
echo "cat tmp_stdout.txt | grep -e Observed -e Expected | awk '{print $NF}' >> $tempfile"
cat tmp_stdout.txt | grep -e Observed -e Expected | awk '{print $NF}' >> $tempfile


cp $tempfile $outputfile
echo "output copied to afs"

rm higgsCombine*.root
rm roostats-*
rm mlfit*.root

echo "all clear"

echo
echo
echo 'END ----------------'
echo
echo

