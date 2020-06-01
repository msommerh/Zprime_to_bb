#!/bin/bash

###
### Macro to be used as executable in the HTCondor submission by submit_combine.py.
###

## fetiching global variables
main_dir='./'        #to be replaced when submitted to HTCondor. Currently has to be on line 8 to be correctly replaced in submit_combine.py!
echo "main_dir = ${main_dir}"
combine_dir=$(${main_dir}global_paths.py -g COMBINEDIR)
echo "combine_dir = ${combine_dir}"
grid_cert=$(${main_dir}global_paths.py -g GRIDCERTIFICATE)
echo "grid_cert = ${grid_cert}"
bias_dir=$(${main_dir}global_paths.py -g BIASDIR)
echo "bias_dir = ${bias_dir}"

echo
echo
echo 'START---------------'
workdir=$(pwd)
echo "workdir = $workdir"
cd $combine_dir
eval `scram runtime -sh`
cd $workdir

export X509_USER_PROXY=$grid_cert
use_x509userproxy=true

#option=""

masses=(1600 1700 1800 1900 2000 2100 2200 2300 2400 2500 2600 2700 2800 2900 3000 3100 3200 3300 3400 3500 3600 3700 3800 3900 4000 4100 4200 4300 4400 4500 4600 4700 4800 4900 5000 5100 5200 5300 5400 5500 5600 5700 5800 5900 6000 6100 6200 6300 6400 6500 6600 6700 6800 6900 7000 7100 7200 7300 7400 7500 7600 7700 7800 7900 8000)

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

mkdir datacards
mkdir datacards/${btagging}
mkdir datacards/${btagging}/bias
mkdir datacards/${btagging}/bias/combined
mkdir workspace
mkdir workspace/${btagging}
mkdir workspace/${btagging}/bias

if [[ $combined -eq 1 ]]; then
    cp ${main_dir}datacards/${btagging}/bias/combined/fully_combined_run2_M${mass}${suffix} datacards/${btagging}/bias/combined/
    cp ${main_dir}workspace/${btagging}/MC_signal_201* workspace/${btagging}/
    cp ${main_dir}workspace/${btagging}/bias/${prefix}_201* workspace/${btagging}/bias/
else
    cp ${main_dir}datacards/${btagging}/bias/combined/combined_${year}_M${mass}${suffix} datacards/${btagging}/bias/combined/
    cp ${main_dir}workspace/${btagging}/MC_signal_${year}* workspace/${btagging}/
    cp ${main_dir}workspace/${btagging}/bias/${prefix}_${year}* workspace/${btagging}/bias/
fi


echo "ls datacards/${btagging}/bias/combined/"
ls datacards/${btagging}/bias/combined/
echo "ls workspace/${btagging}/bias/"
ls workspace/${btagging}/bias/


if [[ $combined -eq 1 ]]; then
    inputfile="datacards/${btagging}/bias/combined/fully_combined_${year}_M${mass}${suffix}"
    outputfile="${bias_dir}${btagging}/combined_run2/fitDiagnostics_M${mass}.root"
    #tempfile=$(echo $inputfile | sed s:datacards/${btagging}/bias/combined/fully_combined_:${workdir}/:g)
    tempfile="${bias_dir}logs/combined_run2_M${mass}.log"
    set_params1="index_Bkg_2016_bb=1,index_Bkg_2016_bq=1,index_Bkg_2016_mumu=1,index_Bkg_2017_bb=1,index_Bkg_2017_bq=1,index_Bkg_2017_mumu=1,index_Bkg_2018_bb=1,index_Bkg_2018_bq=1,index_Bkg_2018_mumu=1"
else
    inputfile="datacards/${btagging}/bias/combined/combined_${year}_M${mass}${suffix}"
    outputfile="${bias_dir}${btagging}/fitDiagnostics_M${mass}.root"
    #tempfile=$(echo $inputfile | sed s:datacards/${btagging}/bias/combined/combined_:${workdir}/:g)
    tempfile="${bias_dir}logs/${year}_M${mass}.log"
    set_params1="index_Bkg_run2_bb=1,index_Bkg_run2_bq=1,index_Bkg_run2_mumu=1"   
fi

echo "inputfile = ${inputfile}"
echo "outputfile = ${outputfile}"
echo "tempfile = ${tempfile}"

echo "starting to run main commands" > $tempfile
echo "inputfile = ${inputfile}" >> $tempfile
echo "outputfile = ${outputfile}" >> $tempfile

freeze_params=$(echo $set_params1 | sed s:"=1":"":g)
set_params0=$(echo $set_params1 | sed s:"=1":"=0":g)

echo
echo "  " >> $tempfile
echo "combine ${inputfile} -M GenerateOnly --setParameters ${set_params0} --toysFrequentist -t 100 --expectSignal 1 --saveToys -m ${mass} --freezeParameters ${freeze_params} >> ${tempfile}"
echo "combine ${inputfile} -M GenerateOnly --setParameters ${set_params0} --toysFrequentist -t 100 --expectSignal 1 --saveToys -m ${mass} --freezeParameters ${freeze_params} >> ${tempfile}" >> $tempfile
combine ${inputfile} -M GenerateOnly --setParameters ${set_params0} --toysFrequentist -t 100 --expectSignal 1 --saveToys -m ${mass} --freezeParameters ${freeze_params} >> $tempfile
echo
echo
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "combine toy generation output:"
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo
cat $tempfile
echo
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo
echo
echo "  " >> $tempfile
echo "combine ${inputfile} -M FitDiagnostics  --setParameters ${set_params1} --toysFile higgsCombineTest.GenerateOnly.mH${mass}.123456.root  -t 100 --rMin -10 --rMax 10 --freezeParameters ${freeze_params} --cminDefaultMinimizerStrategy=0 >> ${tempfile}"
echo "combine ${inputfile} -M FitDiagnostics  --setParameters ${set_params1} --toysFile higgsCombineTest.GenerateOnly.mH${mass}.123456.root  -t 100 --rMin -10 --rMax 10 --freezeParameters ${freeze_params} --cminDefaultMinimizerStrategy=0 >> ${tempfile}" >> $tempfile
combine ${inputfile} -M FitDiagnostics  --setParameters ${set_params1} --toysFile higgsCombineTest.GenerateOnly.mH${mass}.123456.root  -t 100 --rMin -10 --rMax 10 --freezeParameters ${freeze_params} --cminDefaultMinimizerStrategy=0 >> $tempfile
echo
echo
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "combine toy fit output:"
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo
cat $tempfile
echo
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo
echo "cp fitDiagnostics.root ${outputfile}"
cp fitDiagnostics.root ${outputfile}
echo "output copied to afs"

rm *.root

echo "all clear"

echo
echo
echo 'END ----------------'
echo
echo

