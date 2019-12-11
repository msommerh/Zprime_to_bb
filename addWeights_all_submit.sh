#!/bin/bash

echo
echo
echo "----- start -----"
echo
echo 'WORKDIR ' ${PWD}
cd /afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/src/NanoTreeProducer
export SCRAM_ARCH=slc6_amd64_gcc700
if [ -r CMSSW_10_3_3/src ] ; then
    echo 'release CMSSW_10_3_3 already exists'
else
    scram p CMSSW CMSSW_10_3_3
fi
cd CMSSW_10_3_3/src
eval `scram runtime -sh`
cd -
echo 'cmssw release = ' $CMSSW_BASE
source /afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/src/NanoTreeProducer/setupEnv.sh
export X509_USER_PROXY=/afs/cern.ch/user/m/msommerh/x509up_msommerh
use_x509userproxy=true

./postprocessors/addWeight.py -y 2016 -MC -MT signal &
./postprocessors/addWeight.py -y 2016 -MC -MT QCD &
./postprocessors/addWeight.py -y 2016 -MC -MT TTbar &
#./postprocessors/addWeight.py -y 2016

./postprocessors/addWeight.py -y 2017 -MC -MT signal &
./postprocessors/addWeight.py -y 2017 -MC -MT QCD &
./postprocessors/addWeight.py -y 2017 -MC -MT TTbar &
#./postprocessors/addWeight.py -y 2017

./postprocessors/addWeight.py -y 2018 -MC -MT signal &
./postprocessors/addWeight.py -y 2018 -MC -MT QCD &
./postprocessors/addWeight.py -y 2018 -MC -MT TTbar &
#./postprocessors/addWeight.py -y 2018

echo
echo "----- stop -----"
echo
echo
