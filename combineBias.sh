#!/bin/bash

# How to run:
#  source combineTest.sh datacard

ntoys=250 #0

option=""
#option="--toysFrequentist --noErrors --minos none --robustFit=1"
#option="--minimizerAlgo=Minuit2 --robustFit=1"
#option="--freezeNuisanceGroups=shapeS,shape2,shape1,norm"
#option="--freezeNuisanceGroups=theory"
#option="--freezeNuisanceGroups=theory  --minimizerAlgo=Minuit2 --minimizerStrategy=2"
signal="" #--setParameters r=10"

injectSignal=true # set false for bias, true for signal injection

plotname="bias"
if [ $injectSignal ]; then
    plotname="injection"
fi

dir=combine/bias
#cp $1 $dir
name=$(basename $1 .txt)
mass=$(echo $name | tr -dc '0-9')

expectSignal=0
rmin=-3
rmax=3


#if [ $injectSignal ]; then
#    if [ $mass -eq 1000 ]; then
#        expectSignal=10
#        rmin=-10
#        rmax=20
#    elif [ $mass -eq 2000 ]; then
#        expectSignal=6
#        rmin=-5
#        rmax=25
#    elif [ $mass -eq 3000 ]; then
#        expectSignal=3
#        rmin=-5
#        rmax=15
#    elif [ $mass -eq 3500 ]; then
#        expectSignal=2
#        rmin=-5
#        rmax=10
#    elif [ $mass -eq 4000 ]; then
#        expectSignal=1
#        rmin=-2
#        rmax=10
#    elif [ $mass -eq 5000 ]; then
#        expectSignal=1
#        rmin=-1
#        rmax=3
#    else
#        echo ERROR: expectSignal option not recognized, choose 0 or 1
#    fi
#fi

if [ $injectSignal ]; then
    if [ $mass -eq 1000 ]; then
        expectSignal=10
        rmin=-20
        rmax=30
    elif [ $mass -eq 2000 ]; then
        expectSignal=10
        rmin=-5
        rmax=25
    elif [ $mass -eq 3000 ]; then
        expectSignal=6
        rmin=-5
        rmax=20
    elif [ $mass -eq 3500 ]; then
        expectSignal=4
        rmin=-5
        rmax=10
    elif [ $mass -eq 4000 ]; then
        expectSignal=3
        rmin=-2
        rmax=8
    elif [ $mass -eq 5000 ]; then
        expectSignal=2
        rmin=-1
        rmax=4
    else
        echo ERROR: expectSignal option not recognized, choose 0 or 1
    fi
fi

#echo Signal multiplied by $expectSignal, fit ranges [$rmin, $rmax]

#for s in 123456 111111 222222 333333 444444
#do
#    echo name: $name, mass: $mass, seed: $s
#    combine $1 -M GenerateOnly --toysFrequentist -t $ntoys -s $s --expectSignal=$expectSignal --saveToys -m $mass -n _$name $signal
#    combine $1 -M FitDiagnostics --toysFile higgsCombine_$name.GenerateOnly.mH$mass.$s.root --toysFrequentist -s $s --expectSignal=$expectSignal -m $mass -n _$name.$s -t $ntoys --rMin $rmin --rMax $rmax --cminDefaultMinimizerStrategy=0 $option
#    # DO NOT remove --toysFrequentist from FitDiagnostics!
#done

#hadd -f $dir/fitDiagnostics_"$expectSignal"_$name.root fitDiagnostics_$name.*.root
#rm fitDiagnostics_$name.*.root

# Make plot
python toys.py -f $dir/fitDiagnostics_"$expectSignal"_$name.root -o plotsBias/"$plotname"_$name --injection $expectSignal

#if [ $expectSignal -eq 0 ]; then
#    python toys.py -f $dir/fitDiagnostics_"$expectSignal"_$name.root -o plotsBias/bias_$name
#elif [ $expectSignal -eq 1 ]; then
#    python toys.py -f $dir/fitDiagnostics_"$expectSignal"_$name.root -o plotsBias/injection_$name --injection $expectSignal
#else
#    echo ERROR: expectSignal option not recognized, choose 0 or 1
#fi

# Clean
#wait

#rm higgsCombineTest*.root
rm higgsCombine*.root
rm roostats-*

echo -e "\e[00;32mAll clear\e[00m"

# source combineBias.sh combine/bias/XZHslcomb_M1000.txt &> log_M1000.txt &
# source combineBias.sh combine/bias/XZHslcomb_M2000.txt &> log_M2000.txt &
# source combineBias.sh combine/bias/XZHslcomb_M3000.txt &> log_M3000.txt &
# source combineBias.sh combine/bias/XZHslcomb_M3500.txt &> log_M3500.txt &
# source combineBias.sh combine/bias/XZHslcomb_M4000.txt &> log_M4000.txt &
# source combineBias.sh datacards/alpha/XZHVBFslcomb_M1000.txt &> /dev/null &
# source combineBias.sh datacards/alpha/XZHVBFslcomb_M2000.txt &> /dev/null &
# source combineBias.sh datacards/alpha/XZHVBFslcomb_M3000.txt &> /dev/null &
# source combineBias.sh datacards/alpha/XZHVBFslcomb_M3500.txt &> /dev/null &
# source combineBias.sh datacards/alpha/XZHVBFslcomb_M4000.txt &> /dev/null &
                                                                                                           
