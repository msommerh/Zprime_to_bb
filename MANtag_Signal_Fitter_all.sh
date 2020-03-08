#!/bin/bash

./MANtag_Signal_Fitter.py -y run2 -b loose -c mumu 
./MANtag_Signal_Fitter.py -y 2016 -b loose -c mumu
./MANtag_Signal_Fitter.py -y 2017 -b loose -c mumu
./MANtag_Signal_Fitter.py -y 2018 -b loose -c mumu

wait

