#!/bin/bash

dest=$1

cp workspace/medium/*.root $dest
cp combine/plotsLimit/ExclusionLimits/*_medium_MC.p* $dest
cp combine/plotsLimit/ExclusionLimits/*_medium_MC_comb.p* $dest
cp -r plots/medium/MC_* $dest
