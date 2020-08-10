#!/bin/bash

./Bkg_Fitter.py -y 2016 -b medium -d & 
./Bkg_Fitter.py -y 2017 -b medium -d &
./Bkg_Fitter.py -y 2018 -b medium -d &
#./Bkg_Fitter.py -y run2 -b medium -d &
wait
