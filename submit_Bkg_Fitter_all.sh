#!/bin/bash

./submit_Bkg_Fitter.py -MC -q tomorrow -y run2 -b loose
./submit_Bkg_Fitter.py -MC -q tomorrow -y run2 -b medium
./submit_Bkg_Fitter.py -MC -q tomorrow -y run2 -b tight
./submit_Bkg_Fitter.py -MC -q tomorrow -y 2018 -b loose
./submit_Bkg_Fitter.py -MC -q tomorrow -y 2018 -b medium
./submit_Bkg_Fitter.py -MC -q tomorrow -y 2018 -b tight
./submit_Bkg_Fitter.py -MC -q tomorrow -y 2017 -b loose
./submit_Bkg_Fitter.py -MC -q tomorrow -y 2017 -b medium
./submit_Bkg_Fitter.py -MC -q tomorrow -y 2017 -b tight
./submit_Bkg_Fitter.py -MC -q tomorrow -y 2016 -b loose
./submit_Bkg_Fitter.py -MC -q tomorrow -y 2016 -b medium
./submit_Bkg_Fitter.py -MC -q tomorrow -y 2016 -b tight
