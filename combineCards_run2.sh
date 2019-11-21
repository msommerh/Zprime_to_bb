#!/bin/bash

########## input arguments ########## 
btagging=$1
#####################################

cd datacards/$btagging

for card_2016_bb in bb_2016_M*.txt; do
    mass="${card_2016_bb:9:4}"
    let n=${#card_2016_bb}-7
    suffix="${card_2016_bb:7:$n}"
    card_2016_bq="bq_2016${suffix}"
    card_2017_bb="bb_2017${suffix}"
    card_2017_bq="bq_2017${suffix}"
    card_2018_bb="bb_2018${suffix}"
    card_2018_bq="bq_2018${suffix}"

    ncards=0
    for card in $card_2016_bb $card_2016_bq $card_2017_bb $card_2017_bq $card_2018_bb $card_2018_bq; do
        if test -f "$card"; then   
            let ncards=$ncards+1
        fi
    done
    if [[ $ncards -eq 6 ]]; then
        echo "combining datacards/${btagging}/${card_2016_bb}, datacards/${btagging}/${card_2016_bq}, datacards/${btagging}/${card_2017_bb}, datacards/${btagging}/${card_2017_bq}, datacards/${btagging}/${card_2018_bb}, datacards/${btagging}/${card_2018_bq}"
        echo "output datacard: datacards/${btagging}/combined/fully_combined_run2${suffix}"
        combineCards.py bb_2016="$card_2016_bb" bq_2016="$card_2016_bq" bb_2017="$card_2017_bb" bq_2017="$card_2017_bq" bb_2018="$card_2018_bb" bq_2018="$card_2018_bq" > "combined/fully_combined_run2${suffix}"
    else
        echo "only ${ncards} could be associated to ${card_2016_bb}"
    fi

done

cd ../..

