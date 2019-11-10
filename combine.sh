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

higgsCombine() {
    inputfile=$1
    outputfile=$2
    lower_mass=$3
    upper_mass=$4
    mass=$(echo $inputfile | sed s:/afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/src/:: | sed s/2016// | sed s/2017// | sed s/2018// | sed s/run2// |tr -dc '0-9') #delete every character except the numbers. First removes the year
    echo "started higgsCombine()"
    echo "mass = ${mass}"
    if [[ $mass -gt $lower_mass ]] && [[ $mass -le $upper_mass ]]; then
        echo "Input file: ${inputfile}; Output file: ${outputfile}"
        > $outputfile
        #if echo "$option" | grep -q "blind"; then 
        #  echo '1' >> $outputfile
        #fi
        combine -M AsymptoticLimits -d $inputfile -m $mass | grep -e Observed -e Expected | awk '{print $NF}' >> $outputfile #i.e. take the output of combine, select the lines containing "Observed" and "Expected" via grep, select the last field via awk and append it to the outputfile
    fi
}

########## input arguments ########## 
btagging=$1
year=$2
isMC=$3
#####################################

echo "btagging = ${btagging}"
echo "year = ${year}"
echo "isMC = ${isMC}"

if [[ $isMC -eq 1]]; then
    echo "running purely on MC..."
    suffix="_MC.txt"
else
    suffix=".txt"
fi

#for low_mass in 1000 2000 3000 4000 5000 6000 7000; do
    #let high_mass=$low_mass+1000
for low_mass in 1999 2099; do
    let high_mass=$low_mass+101

    echo "low_mass=${low_mass}, high_mass=${high_mass}"

    for card in /afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/src/NanoTreeProducer/datacards/$btagging/combined/combined_$year*$suffix; do
        #output=$(echo $card | sed s:datacards/:combine/limits/: | sed s:combined/combined_::g)
        output=$(echo $card | sed s:/afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/src/NanoTreeProducer/datacards/${btagging}/combined/combined_::g)
        echo "card = ${card}"
        echo "output = ${output}"
        higgsCombine $card $output $low_mass $high_mass &
        cp $output /afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/src/NanoTreeProducer/combine/limits/sub_test/${btagging}/
    done
    wait
done

## Clean
wait

rm higgsCombine*.root
rm roostats-*
rm mlfit*.root

echo -e "\e[00;32mAll clear\e[00m"

echo
echo
echo 'END ----------------'
echo
echo


