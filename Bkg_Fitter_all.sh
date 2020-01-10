#!/bin/bash

./Bkg_Fitter.py -M -y 2016 -b medium -s fullVeto & 
./Bkg_Fitter.py -M -y 2017 -b medium -s fullVeto &
./Bkg_Fitter.py -M -y 2018 -b medium -s fullVeto &
./Bkg_Fitter.py -M -y run2 -b medium -s fullVeto &
wait
