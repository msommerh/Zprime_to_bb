#!/bin/bash

cd datacards/$1

for card1 in bb_*_MC.txt
do
    mass="${card1:9:4}"
    let n=${#card1}-2
    card2="bq${card1:2:$n}"
    if test -f "$card2"; then
        echo "combining ${card1} and ${card2} into combined/combined${card1:2:$n}"
        combineCards.py bb="$card1" bq="$card2" > "combined/combined${card1:2:$n}"
    else
        echo "${card2} does not exist"
    fi
done

cd ../..

