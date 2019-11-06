#!/bin/bash

# How to run:
#  source combine.sh -m alpha
# To filter jobs:
#  source combine.sh -m alpha XZhnnb_M

option=""
# option="--freezeNuisanceGroups=theory --run=blind"
#option="--freezeNuisanceGroups=theory"
#option="-H ProfileLikelihood"


#if [[ "$1" != "-m" ]] || [[ "$2" == "" ]] || [[ "$3" == "" ]]
#then
#    echo Select a method and a filter:
#    echo "  -m:          " $(ls datacards/)
#    return
#fi

higgsCombine() {
    inputfile=$1
    outputfile=$2
    mass=$(echo $inputfile | sed s/2016// | sed s/2017// | sed s/2018// | sed s/run2// |tr -dc '0-9') #delete every character except the numbers. First removes the year 
    #echo Running $method mass $mass on $inputfile...
    echo "Input file: ${inputfile}; Output file: ${outputfile}"

    > $outputfile
    #if echo "$option" | grep -q "blind"; then 
    #  echo '1' >> $outputfile
    #fi
    combine -M AsymptoticLimits -d $inputfile -m $mass | grep -e Observed -e Expected | awk '{print $NF}' >> $outputfile #i.e. take the output of combine, select the lines containing "Observed" and "Expected" via grep, select the last field via awk and append it to the outputfile
}


for card in datacards/$1/combined/$2*.txt
do
    #analysis=$(basename $(dirname $card))
    #signal=$(basename $card .txt)
#    echo Running with method $2 on $signal
    #higgsCombine $signal $2 &
    #output=$(echo $card | sed s:datacards/combined:combine/limits: | sed s/combined_//g)
    output=$(echo $card | sed s:datacards/:combine/limits/: | sed s:combined/combined_::g)
    higgsCombine $card $output &
done

## Clean
wait

rm higgsCombine*.root
rm roostats-*
rm mlfit*.root

echo -e "\e[00;32mAll clear\e[00m"

# python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/leeFromUpcrossings.py bands.root graph 1000 4500 --fit=best

# To derive Impacts (https://twiki.cern.ch/twiki/bin/viewauth/CMS/HiggsWG/SWGuideNonStandardCombineUses#Nuisance_parameter_impacts):
# text2workspace.py datacards/dijet/XVHah_M2000.txt
# produces .root file in the same directory of the datacard
# combine -M MultiDimFit -n _initialFit_Test --algo singles --redefineSignalPOIs r --robustFit 1 -m 2000 -d XVHah_M2000.root
# combineTool.py -M Impacts -d XVHah_M2000.root -m 2000 --robustFit 1 --doFits --parallel 10
# combineTool.py -M Impacts -d XVHah_M2000.root -m 2000 -o impacts.json
# plotImpacts.py -i impacts.json -o impacts
