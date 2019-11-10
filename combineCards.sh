#!/bin/bash

########## input arguments ########## 
btagging=$1
#####################################

cd datacards/$btagging

for card1 in bb_*.txt
do
    mass="${card1:9:4}"
    let n=${#card1}-2
    card2="bq${card1:2:$n}"
    if test -f "$card2"; then
        echo "combining datacards/${btagging}/${card1} and datacards/${btagging}/${card2} into datacards/${btagging}/combined/combined${card1:2:$n}"
        combineCards.py bb="$card1" bq="$card2" > "combined/combined${card1:2:$n}"
    else
        echo "datacards/${btagging}/${card2} does not exist"
    fi
done

cd ../..

