#!/bin/bash

#./Datacards.py -M -y 2016 -b medium
#./Datacards.py -M -y 2017 -b medium
#./Datacards.py -M -y 2018 -b medium
#./Datacards.py -M -y run2 -b medium
#
./Datacards.py -y 2016 -b medium
./Datacards.py -y 2017 -b medium
./Datacards.py -y 2018 -b medium
./Datacards.py -y run2 -b medium

./combineCards.sh medium
./combineCards.sh medium 1

./combineCards_sepCat.sh medium bb
./combineCards_sepCat.sh medium bq
./combineCards_sepCat.sh medium mumu

#./Datacards.py -M -y 2016 -b loose 
#./Datacards.py -M -y 2017 -b loose
#./Datacards.py -M -y 2018 -b loose
#./Datacards.py -M -y run2 -b loose
#
#./combineCards.sh loose 
#./combineCards.sh loose 1
