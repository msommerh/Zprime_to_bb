#!/bin/bash

./Datacards.py -M -y 2016 -b loose
./Datacards.py -M -y 2016 -b medium
./Datacards.py -M -y 2016 -b tight
./Datacards.py -M -y 2017 -b loose
./Datacards.py -M -y 2017 -b medium
./Datacards.py -M -y 2017 -b tight
./Datacards.py -M -y 2018 -b loose
./Datacards.py -M -y 2018 -b medium
./Datacards.py -M -y 2018 -b tight
./Datacards.py -M -y run2 -b loose
./Datacards.py -M -y run2 -b medium
./Datacards.py -M -y run2 -b tight

./combineCards.sh loose
./combineCards.sh medium
./combineCards.sh tight

