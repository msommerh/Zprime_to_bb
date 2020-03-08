#!/bin/bash

./MANtag_Datacards.py -y 2016 -b loose 
./MANtag_Datacards.py -y 2017 -b loose
./MANtag_Datacards.py -y 2018 -b loose
./MANtag_Datacards.py -y run2 -b loose

./MANtag_combineCards.sh loose 
./MANtag_combineCards.sh loose 1
