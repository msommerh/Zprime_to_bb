#!/bin/bash

# How to run:
#  source combineTest.sh datacard


option="" #--freezeNuisanceGroups=shape2"
#option="-t -1" # Asimov dataset
#option="--freezeNuisanceGroups=theory"
#option="--freezeNuisanceGroups=theory  --minimizerAlgo=Minuit2 --minimizerStrategy=2"

dir=combine/test
cp $1 $dir
name=$(basename $1 .txt)
mass=$(echo $name | tr -dc '0-9')
echo name: $name, mass: $mass

combine -M MaxLikelihoodFit --datacard $dir/$name.txt --saveShapes --saveWithUncertainties --expectSignal=0 --robustFit=1 $option --keepFailures -n _$name #| grep Best # -t -1 generates errors 
mv -f mlfit_$name.root $dir # --plots
python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/diffNuisances.py --vtol=0.0000001 -f text $dir/mlfit_$name.root | sed -e 's/!/ /g' -e 's/,/ /g' | tail -n +2 > $dir/pulls_$name.txt # -g rootfiles/pull_$1$2\_M$3.root
python pulls.py -b -f $dir/pulls_$name.txt -o $dir/pulls_$name

#mass=1000
## To derive Impacts (https://twiki.cern.ch/twiki/bin/viewauth/CMS/HiggsWG/SWGuideNonStandardCombineUses#Nuisance_parameter_impacts):
#text2workspace.py $dir/$name.txt # produces .root file in the same directory of the datacard
#combine -M MultiDimFit -n _initialFit_Test --algo singles --redefineSignalPOIs r --robustFit 1 --mass $mass $option -d $dir/$name.root
#combineTool.py -M Impacts -d $dir/$name.root --mass $mass --robustFit 1 --doFits --parallel 12
#combineTool.py -M Impacts -d $dir/$name.root --mass $mass -o $dir/impacts_$name.json
#plotImpacts.py -i $dir/impacts_$name.json --cms-label Preliminary -o $dir/impacts_$name # --transparent --color-groups 1,8,9,39,2
##pdftoppm -png -f 1 $dir/impacts_$name.pdf $dir/impacts_$name

## Clean
wait

#rm $dir/pulls_$name.txt $dir/$name.txt # $dir/mlfit_$name.root
#rm $dir/impacts_$name.json $dir/$name.root
#rm higgsCombine*.root
#rm roostats-*
#rm mlfit*.root

echo -e "\e[00;32mAll clear\e[00m"

# combine -M HybridNew --frequentist --datacard datacards/dijet/XVHah_M2600.txt --significance -H ProfileLikelihood --fork 32 -T 2000 -i 3
# combine -M HybridNew -d datacards/alpha/XZHnn_M2000.txt --signif -T 10000 -> 2.6
# combine -M HybridNew -d datacards/alpha/XZHnnbb_M2000.txt --signif -T 5000 -> 2.07

# python $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/test/leeFromUpcrossings.py bands.root graph 1000 4500 --fit=best
