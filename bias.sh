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
ntoys=$5
seed=$6
#####################################

if [[ $seed == "" ]]; then
    seed=123456
fi

mass=${masses[${mass_nr}]}

if [[ $year == run2c ]]; then
    echo "Combining the 2016-2018 fits separately into a single limit..."
    year="run2"
    combined=1
else
    combined=0
fi

## varying signal injection depending on mass:
expectSignal=0
rmin=-30
rmax=70

####### use this for nice fits
#if [ $mass -eq 1600 ]; then
#    #expectSignal=20 
#elif [ $mass -eq 1700 ]; then
#    #expectSignal=15 
#elif [ $mass -eq 1800 ]; then
#    #expectSignal=10 
#elif [ $mass -eq 1900 ]; then
#    #expectSignal=15 
#elif [ $mass -eq 2000 ]; then
#    #expectSignal=15
#elif [ $mass -eq 2100 ]; then
#    #expectSignal=3 
#elif [ $mass -eq 2200 ]; then
#    #expectSignal=15 
#elif [ $mass -eq 2300 ]; then
#    #expectSignal=8 
#elif [ $mass -eq 2400 ]; then
#    #expectSignal=8 
#elif [ $mass -eq 2500 ]; then
#    #expectSignal=3 
#elif [ $mass -eq 2600 ]; then
#    #expectSignal=8 
#elif [ $mass -eq 2700 ]; then
#    #expectSignal=10 
#elif [ $mass -eq 2800 ]; then
#    #expectSignal=10 
#elif [ $mass -eq 2900 ]; then
#    #expectSignal=5
#elif [ $mass -eq 3000 ]; then
#    #expectSignal=8 
#elif [ $mass -eq 3100 ]; then
#    #expectSignal=10 
#elif [ $mass -eq 3200 ]; then
#    #expectSignal=15 
#elif [ $mass -eq 3300 ]; then
#    #expectSignal=3 
#elif [ $mass -eq 3400 ]; then
#    #expectSignal=10 
#elif [ $mass -eq 3500 ]; then
#    #expectSignal=5 
#elif [ $mass -eq 3600 ]; then
#    #expectSignal=15 
#elif [ $mass -eq 3700 ]; then
#    #expectSignal=5 
#elif [ $mass -eq 3800 ]; then
#    #expectSignal=3 
#elif [ $mass -eq 3900 ]; then
#    #expectSignal=1 
#elif [ $mass -eq 4000 ]; then
#    #expectSignal=1 
#elif [ $mass -eq 4100 ]; then
#    #expectSignal=1 
#elif [ $mass -eq 4200 ]; then
#    #expectSignal=10 
#elif [ $mass -eq 4300 ]; then
#    #expectSignal=8 
#elif [ $mass -eq 4400 ]; then
#    #expectSignal=8 
#elif [ $mass -eq 4500 ]; then
#    #expectSignal=15 
#elif [ $mass -eq 4600 ]; then
#    #expectSignal=8
#elif [ $mass -eq 4700 ]; then
#    #expectSignal=3 
#elif [ $mass -eq 4800 ]; then
#    #expectSignal=3 
#elif [ $mass -eq 4900 ]; then
#    #expectSignal=3 
#elif [ $mass -eq 5000 ]; then
#    #expectSignal=3 
#elif [ $mass -eq 5100 ]; then
#    #expectSignal=1 
#elif [ $mass -eq 5200 ]; then
#    #expectSignal=3 
#elif [ $mass -eq 5300 ]; then
#    #expectSignal=5 
#elif [ $mass -eq 5400 ]; then
#    #expectSignal=5 
#elif [ $mass -eq 5500 ]; then
#    #expectSignal=10 
#elif [ $mass -eq 5600 ]; then
#    #expectSignal=1 
#elif [ $mass -eq 5700 ]; then
#    #expectSignal=5 
#elif [ $mass -eq 5800 ]; then
#    #expectSignal=1 
#elif [ $mass -eq 5900 ]; then
#    #expectSignal=1 
#elif [ $mass -eq 6000 ]; then
#    #expectSignal=15 
#elif [ $mass -eq 6100 ]; then
#    #expectSignal=1 
#elif [ $mass -eq 6200 ]; then
#    #expectSignal=5 
#elif [ $mass -eq 6300 ]; then
#    #expectSignal=1 
#elif [ $mass -eq 6400 ]; then
#    #expectSignal=3 
#elif [ $mass -eq 6500 ]; then
#    #expectSignal=3 
#elif [ $mass -eq 6600 ]; then
#    #expectSignal=5 
#elif [ $mass -eq 6700 ]; then
#    #expectSignal=10 
#elif [ $mass -eq 6800 ]; then
#    #expectSignal=3 
#elif [ $mass -eq 6900 ]; then
#    #expectSignal=10 
#elif [ $mass -eq 7000 ]; then
#    #expectSignal=5 
#elif [ $mass -eq 7100 ]; then
#    #expectSignal=10 
#elif [ $mass -eq 7200 ]; then
#    #expectSignal=8 
#elif [ $mass -eq 7300 ]; then
#    #expectSignal=8 
#elif [ $mass -eq 7400 ]; then
#    #expectSignal=3 
#elif [ $mass -eq 7500 ]; then
#    #expectSignal=10 
#elif [ $mass -eq 7600 ]; then
#    #expectSignal=3 
#elif [ $mass -eq 7700 ]; then
#    #expectSignal=1 
#elif [ $mass -eq 7800 ]; then
#    #expectSignal=3 
#elif [ $mass -eq 7900 ]; then
#    #expectSignal=15 
#elif [ $mass -eq 8000 ]; then
#    #expectSignal=8 
#else
#    echo "mass point not recocnized"
#fi


####### use this for ~2sigma

### use putting some signal load into the datacards
#if [ $mass -eq 1600 ]; then
#    expectSignal=21
#elif [ $mass -eq 1700 ]; then
#    expectSignal=15
#elif [ $mass -eq 1800 ]; then
#    expectSignal=10 
#elif [ $mass -eq 1900 ]; then
#    expectSignal=8 
#elif [ $mass -eq 2000 ]; then
#    expectSignal=7
#elif [ $mass -eq 2100 ]; then
#    expectSignal=16 
#elif [ $mass -eq 2200 ]; then
#    expectSignal=14 
#elif [ $mass -eq 2300 ]; then
#    expectSignal=13 
#elif [ $mass -eq 2400 ]; then
#    expectSignal=12 
#elif [ $mass -eq 2500 ]; then
#    expectSignal=11 
###
##if [ $mass -eq 1600 ]; then
##    expectSignal=106
##elif [ $mass -eq 1700 ]; then
##    expectSignal=77
##elif [ $mass -eq 1800 ]; then
##    expectSignal=51 
##elif [ $mass -eq 1900 ]; then
##    expectSignal=41 
##elif [ $mass -eq 2000 ]; then
##    expectSignal=35
##elif [ $mass -eq 2100 ]; then
##    expectSignal=32 
##elif [ $mass -eq 2200 ]; then
##    expectSignal=28 
##elif [ $mass -eq 2300 ]; then
##    expectSignal=26 
##elif [ $mass -eq 2400 ]; then
##    expectSignal=23 
##elif [ $mass -eq 2500 ]; then
##    expectSignal=21 
#elif [ $mass -eq 2600 ]; then
#    expectSignal=20 
#elif [ $mass -eq 2700 ]; then
#    expectSignal=18 
#elif [ $mass -eq 2800 ]; then
#    expectSignal=17 
#elif [ $mass -eq 2900 ]; then
#    expectSignal=15
#elif [ $mass -eq 3000 ]; then
#    expectSignal=14 
#elif [ $mass -eq 3100 ]; then
#    expectSignal=13 
#elif [ $mass -eq 3200 ]; then
#    expectSignal=13 
#elif [ $mass -eq 3300 ]; then
#    expectSignal=12
#elif [ $mass -eq 3400 ]; then
#    expectSignal=11 
#elif [ $mass -eq 3500 ]; then
#    expectSignal=11 
#elif [ $mass -eq 3600 ]; then
#    expectSignal=10 
#elif [ $mass -eq 3700 ]; then
#    expectSignal=9 
#elif [ $mass -eq 3800 ]; then
#    expectSignal=9 
#elif [ $mass -eq 3900 ]; then
#    expectSignal=8 
#elif [ $mass -eq 4000 ]; then
#    expectSignal=8 
#elif [ $mass -eq 4100 ]; then
#    expectSignal=7 
#elif [ $mass -eq 4200 ]; then
#    expectSignal=7 
#elif [ $mass -eq 4300 ]; then
#    expectSignal=6 
#elif [ $mass -eq 4400 ]; then
#    expectSignal=6 
#elif [ $mass -eq 4500 ]; then
#    expectSignal=6 
#elif [ $mass -eq 4600 ]; then
#    expectSignal=5 
#elif [ $mass -eq 4700 ]; then
#    expectSignal=5 
#elif [ $mass -eq 4800 ]; then
#    expectSignal=4 
#elif [ $mass -eq 4900 ]; then
#    expectSignal=4 
#elif [ $mass -eq 5000 ]; then
#    expectSignal=4 
#elif [ $mass -eq 5100 ]; then
#    expectSignal=4 
#elif [ $mass -eq 5200 ]; then
#    expectSignal=3 
#elif [ $mass -eq 5300 ]; then
#    expectSignal=3 
#elif [ $mass -eq 5400 ]; then
#    expectSignal=3 
#elif [ $mass -eq 5500 ]; then
#    expectSignal=3 
#elif [ $mass -eq 5600 ]; then
#    expectSignal=2 
#elif [ $mass -eq 5700 ]; then
#    expectSignal=2 
#elif [ $mass -eq 5800 ]; then
#    expectSignal=2 
#elif [ $mass -eq 5900 ]; then
#    expectSignal=2 
#elif [ $mass -eq 6000 ]; then
#    expectSignal=2 
#elif [ $mass -eq 6100 ]; then
#    expectSignal=2 
#elif [ $mass -eq 6200 ]; then
#    expectSignal=1 
#elif [ $mass -eq 6300 ]; then
#    expectSignal=1 
#elif [ $mass -eq 6400 ]; then
#    expectSignal=1 
#elif [ $mass -eq 6500 ]; then
#    expectSignal=1 
#elif [ $mass -eq 6600 ]; then
#    expectSignal=1 
#elif [ $mass -eq 6700 ]; then
#    expectSignal=1 
#elif [ $mass -eq 6800 ]; then
#    expectSignal=1 
#elif [ $mass -eq 6900 ]; then
#    expectSignal=1 
#elif [ $mass -eq 7000 ]; then
#    expectSignal=1 
#elif [ $mass -eq 7100 ]; then
#    expectSignal=1 
#elif [ $mass -eq 7200 ]; then
#    expectSignal=1 
#elif [ $mass -eq 7300 ]; then
#    expectSignal=1 
#elif [ $mass -eq 7400 ]; then
#    expectSignal=1 
#elif [ $mass -eq 7500 ]; then
#    expectSignal=1 
#elif [ $mass -eq 7600 ]; then
#    expectSignal=1 
#elif [ $mass -eq 7700 ]; then
#    expectSignal=1 
#elif [ $mass -eq 7800 ]; then
#    expectSignal=1 
#elif [ $mass -eq 7900 ]; then
#    expectSignal=1 
#elif [ $mass -eq 8000 ]; then
#    expectSignal=1 
#else
#    echo "mass point not recocnized"
#fi


###### use this for ~5sigma

## use putting some signal load into the datacards
if [ $mass -eq 1600 ]; then
    expectSignal=11
elif [ $mass -eq 1700 ]; then
    expectSignal=16
elif [ $mass -eq 1800 ]; then
    expectSignal=8 
elif [ $mass -eq 1900 ]; then
    expectSignal=6 
elif [ $mass -eq 2000 ]; then
    expectSignal=8
elif [ $mass -eq 2100 ]; then
    expectSignal=8 
elif [ $mass -eq 2200 ]; then
    expectSignal=7 
elif [ $mass -eq 2300 ]; then
    expectSignal=8 
elif [ $mass -eq 2400 ]; then
    expectSignal=3 
elif [ $mass -eq 2500 ]; then
    expectSignal=4 
elif [ $mass -eq 2600 ]; then
    expectSignal=7 
elif [ $mass -eq 2700 ]; then
    expectSignal=5 
elif [ $mass -eq 2800 ]; then
    expectSignal=6 
elif [ $mass -eq 2900 ]; then
    expectSignal=2
elif [ $mass -eq 3000 ]; then
    expectSignal=6 
elif [ $mass -eq 3100 ]; then
    expectSignal=3 
elif [ $mass -eq 3200 ]; then
    expectSignal=1 
elif [ $mass -eq 3300 ]; then
    expectSignal=3
elif [ $mass -eq 3400 ]; then
    expectSignal=4 
elif [ $mass -eq 3500 ]; then
    expectSignal=2 
elif [ $mass -eq 3600 ]; then
    expectSignal=5 
elif [ $mass -eq 3700 ]; then
    expectSignal=4
elif [ $mass -eq 3800 ]; then
    expectSignal=1
elif [ $mass -eq 3900 ]; then
    expectSignal=3
elif [ $mass -eq 4000 ]; then
    expectSignal=2
##

#if [ $mass -eq 1600 ]; then
#    expectSignal=264
#elif [ $mass -eq 1700 ]; then
#    expectSignal=192
#elif [ $mass -eq 1800 ]; then
#    expectSignal=128 
#elif [ $mass -eq 1900 ]; then
#    expectSignal=102 
#elif [ $mass -eq 2000 ]; then
#    expectSignal=88
#elif [ $mass -eq 2100 ]; then
#    expectSignal=79 
#elif [ $mass -eq 2200 ]; then
#    expectSignal=71 
#elif [ $mass -eq 2300 ]; then
#    expectSignal=64 
#elif [ $mass -eq 2400 ]; then
#    expectSignal=58 
#elif [ $mass -eq 2500 ]; then
#    expectSignal=53 
#elif [ $mass -eq 2600 ]; then
#    expectSignal=49 
#elif [ $mass -eq 2700 ]; then
#    expectSignal=45 
#elif [ $mass -eq 2800 ]; then
#    expectSignal=41 
#elif [ $mass -eq 2900 ]; then
#    expectSignal=38
#elif [ $mass -eq 3000 ]; then
#    expectSignal=36 
#elif [ $mass -eq 3100 ]; then
#    expectSignal=33 
#elif [ $mass -eq 3200 ]; then
#    expectSignal=31 
#elif [ $mass -eq 3300 ]; then
#    expectSignal=30
#elif [ $mass -eq 3400 ]; then
#    expectSignal=28 
#elif [ $mass -eq 3500 ]; then
#    expectSignal=26 
#elif [ $mass -eq 3600 ]; then
#    expectSignal=25 
#elif [ $mass -eq 3700 ]; then
#    expectSignal=24
#elif [ $mass -eq 3800 ]; then
#    expectSignal=23
#elif [ $mass -eq 3900 ]; then
#    expectSignal=21
#elif [ $mass -eq 4000 ]; then
#    expectSignal=20
elif [ $mass -eq 4100 ]; then
    expectSignal=19
elif [ $mass -eq 4200 ]; then
    expectSignal=17
elif [ $mass -eq 4300 ]; then
    expectSignal=16
elif [ $mass -eq 4400 ]; then
    expectSignal=15
elif [ $mass -eq 4500 ]; then
    expectSignal=14
elif [ $mass -eq 4600 ]; then
    expectSignal=13
elif [ $mass -eq 4700 ]; then
    expectSignal=12
elif [ $mass -eq 4800 ]; then
    expectSignal=11
elif [ $mass -eq 4900 ]; then
    expectSignal=10
elif [ $mass -eq 5000 ]; then
    expectSignal=9
elif [ $mass -eq 5100 ]; then
    expectSignal=9 
elif [ $mass -eq 5200 ]; then
    expectSignal=8 
elif [ $mass -eq 5300 ]; then
    expectSignal=7 
elif [ $mass -eq 5400 ]; then
    expectSignal=7 
elif [ $mass -eq 5500 ]; then
    expectSignal=6 
elif [ $mass -eq 5600 ]; then
    expectSignal=6 
elif [ $mass -eq 5700 ]; then
    expectSignal=5 
elif [ $mass -eq 5800 ]; then
    expectSignal=5 
elif [ $mass -eq 5900 ]; then
    expectSignal=5 
elif [ $mass -eq 6000 ]; then
    expectSignal=4 
elif [ $mass -eq 6100 ]; then
    expectSignal=4 
elif [ $mass -eq 6200 ]; then
    expectSignal=4 
elif [ $mass -eq 6300 ]; then
    expectSignal=3 
elif [ $mass -eq 6400 ]; then
    expectSignal=3 
elif [ $mass -eq 6500 ]; then
    expectSignal=3 
elif [ $mass -eq 6600 ]; then
    expectSignal=3 
elif [ $mass -eq 6700 ]; then
    expectSignal=2 
elif [ $mass -eq 6800 ]; then
    expectSignal=2 
elif [ $mass -eq 6900 ]; then
    expectSignal=2 
elif [ $mass -eq 7000 ]; then
    expectSignal=2 
elif [ $mass -eq 7100 ]; then
    expectSignal=2 
elif [ $mass -eq 7200 ]; then
    expectSignal=2 
elif [ $mass -eq 7300 ]; then
    expectSignal=2 
elif [ $mass -eq 7400 ]; then
    expectSignal=2 
elif [ $mass -eq 7500 ]; then
    expectSignal=1 
elif [ $mass -eq 7600 ]; then
    expectSignal=1 
elif [ $mass -eq 7700 ]; then
    expectSignal=1 
elif [ $mass -eq 7800 ]; then
    expectSignal=1 
elif [ $mass -eq 7900 ]; then
    expectSignal=1 
elif [ $mass -eq 8000 ]; then
    expectSignal=1 
else
    echo "mass point not recocnized"
fi



echo "isMC = ${isMC}"
echo "year = ${year}"
echo "btagging = ${btagging}"
echo "mass_nr = ${mass_nr}"
echo "mass = ${mass}"
echo "combined = ${combined}"
echo "seed = ${seed}"
echo "expectSignal = ${expectSignal}"
echo "rmin = ${rmin}"
echo "rmax = ${rmax}"

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
    #cp ${main_dir}datacards/${btagging}/bias/combined/fully_combined_run2_M${mass}${suffix} datacards/${btagging}/bias/combined/
    #cp ${main_dir}datacards/${btagging}/bias/combined_varying_rate_2sigma/fully_combined_run2_M${mass}${suffix} datacards/${btagging}/bias/combined/ ##FIXME FIXME
    cp ${main_dir}datacards/${btagging}/bias/combined_varying_rate_5sigma/fully_combined_run2_M${mass}${suffix} datacards/${btagging}/bias/combined/ ##FIXME FIXME
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
    outputfile="${bias_dir}${btagging}/combined_run2/fitDiagnostics_M${mass}_${seed}.root"
    #tempfile=$(echo $inputfile | sed s:datacards/${btagging}/bias/combined/fully_combined_:${workdir}/:g)
    tempfile="${bias_dir}logs/combined_run2_M${mass}_${seed}.log"
    set_params1="index_Bkg_2016_bb=1,index_Bkg_2016_bq=1,index_Bkg_2016_mumu=1,index_Bkg_2017_bb=1,index_Bkg_2017_bq=1,index_Bkg_2017_mumu=1,index_Bkg_2018_bb=1,index_Bkg_2018_bq=1,index_Bkg_2018_mumu=1"
else
    inputfile="datacards/${btagging}/bias/combined/combined_${year}_M${mass}${suffix}"
    outputfile="${bias_dir}${btagging}/fitDiagnostics_M${mass}_${seed}.root"
    #tempfile=$(echo $inputfile | sed s:datacards/${btagging}/bias/combined/combined_:${workdir}/:g)
    tempfile="${bias_dir}logs/${year}_M${mass}_${seed}.log"
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
shape0="CMS2016_bb_p2_1,CMS2016_bb_p2_2,CMS2016_bq_p2_1,CMS2016_bq_p2_2,CMS2016_mumu_p3_1,CMS2016_mumu_p3_2,CMS2016_mumu_p3_3,CMS2017_bb_p3_1,CMS2017_bb_p3_2,CMS2017_bb_p3_3,CMS2017_bq_p2_1,CMS2017_bq_p2_2,CMS2017_mumu_p2_1,CMS2017_mumu_p2_2,CMS2018_bb_p2_1,CMS2018_bb_p2_2,CMS2018_bq_p2_1,CMS2018_bq_p2_2,CMS2018_mumu_p2_1,CMS2018_mumu_p2_2"
shape1="CMS2016_bb_p3_1,CMS2016_bb_p3_2,CMS2016_bb_p3_3,CMS2016_bq_p3_1,CMS2016_bq_p3_2,CMS2016_bq_p3_3,CMS2016_mumu_p4_1,CMS2016_mumu_p4_2,CMS2016_mumu_p4_3,CMS2016_mumu_p4_4,CMS2017_bb_p4_1,CMS2017_bb_p4_2,CMS2017_bb_p4_3,CMS2017_bb_p4_4,CMS2017_bq_p3_1,CMS2017_bq_p3_2,CMS2017_bq_p3_3,CMS2017_mumu_p3_1,CMS2017_mumu_p3_2,CMS2017_mumu_p3_3,CMS2018_bb_p3_1,CMS2018_bb_p3_2,CMS2018_bb_p3_3,CMS2018_bq_p3_1,CMS2018_bq_p3_2,CMS2018_bq_p3_3,CMS2018_mumu_p3_1,CMS2018_mumu_p3_2,CMS2018_mumu_p3_3"

echo
echo "  " >> $tempfile
echo "combine ${inputfile} -M GenerateOnly --setParameters ${set_params0} --toysFrequentist -t ${ntoys} --expectSignal=${expectSignal} --saveToys -s ${seed} -m ${mass} --freezeParameters ${freeze_params} >> ${tempfile}"
echo "combine ${inputfile} -M GenerateOnly --setParameters ${set_params0} --toysFrequentist -t ${ntoys} --expectSignal=${expectSignal} --saveToys -s ${seed} -m ${mass} --freezeParameters ${freeze_params} >> ${tempfile}" >> $tempfile
combine ${inputfile} -M GenerateOnly --setParameters ${set_params0} --toysFrequentist -t ${ntoys} --expectSignal=$expectSignal --saveToys -s ${seed} -m ${mass} --freezeParameters ${freeze_params} >> $tempfile
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
echo "combine ${inputfile} -M FitDiagnostics  --setParameters ${set_params1} --toysFile higgsCombineTest.GenerateOnly.mH${mass}.${seed}.root -s ${seed} -t ${ntoys} --rMin ${rmin} --rMax ${rmax} --freezeParameters ${freeze_params},${shape0} --cminDefaultMinimizerStrategy=0 --toysFrequentist --expectSignal=${expectSignal} >> ${tempfile}"
echo "combine ${inputfile} -M FitDiagnostics  --setParameters ${set_params1} --toysFile higgsCombineTest.GenerateOnly.mH${mass}.${seed}.root -s ${seed} -t ${ntoys} --rMin ${rmin} --rMax ${rmax} --freezeParameters ${freeze_params},${shape0} --cminDefaultMinimizerStrategy=0 --toysFrequentist --expectSignal=${expectSignal} >> ${tempfile}" >> $tempfile
combine ${inputfile} -M FitDiagnostics  --setParameters ${set_params1} --toysFile higgsCombineTest.GenerateOnly.mH${mass}.${seed}.root -s ${seed} -t ${ntoys} --rMin $rmin --rMax $rmax --freezeParameters ${freeze_params},${shape0} --cminDefaultMinimizerStrategy=0 --toysFrequentist --expectSignal=$expectSignal >> $tempfile
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

