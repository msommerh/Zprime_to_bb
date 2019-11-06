#!/bin/bash

for card in datacards/medium/combined/2018_M*;do  
    #output=$(echo $card | sed s:datacards/combined:combine/limits: | sed s/combined_//g)
    output=$(echo $card | sed s:datacards/:combine/limits/: | sed s:combined/::g)
    echo "output = ${output}"
    #mv $card $output
done
