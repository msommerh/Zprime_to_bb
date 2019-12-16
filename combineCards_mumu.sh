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
    card3="mumu${card1:2:$n}"
    if test -f "$card2"; then
        if test -f "$card3"; then
            echo "input cards:"
            echo "1) datacards/${btagging}/${card1}"
            echo "2) datacards/${btagging}/${card2}"
            echo "3) datacards/${btagging}/${card3}" 
            echo "output card: datacards/${btagging}/combined/combined${card1:2:$n}"
            combineCards.py bb="$card1" bq="$card2" mumu="$card3" > "combined/combined${card1:2:$n}"
        else
            echo "datacards/${btagging}/${card3} does not exist"
        fi
    else
        echo "datacards/${btagging}/${card2} does not exist"
    fi
done

cd ../..

