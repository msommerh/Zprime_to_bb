#!/bin/bash

./Datacards.py -M -y 2016 -b medium
./Datacards.py -M -y 2017 -b medium
./Datacards.py -M -y 2018 -b medium
./Datacards.py -M -y run2 -b medium

./Datacards.py -y 2016 -b medium
./Datacards.py -y 2017 -b medium
./Datacards.py -y 2018 -b medium
./Datacards.py -y run2 -b medium

./combineCards.sh medium
./combineCards_run2.sh medium
