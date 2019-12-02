#!/bin/bash

#./submit.py -q longlunch -y 2016 -MC -MT signal
#./submit.py -q longlunch -y 2017 -MC -MT signal
#./submit.py -q longlunch -y 2018 -MC -MT signal
#
#./submit.py -q tomorrow -y 2016 -MC -MT QCD -n 5 -c 4
#./submit.py -q tomorrow -y 2016 -MC -MT TTbar -n 5 -c 4
#./submit.py -q tomorrow -y 2017 -MC -MT QCD -n 5 -c 4
#./submit.py -q tomorrow -y 2017 -MC -MT TTbar -n 5 -c 4
#./submit.py -q tomorrow -y 2018 -MC -MT QCD -n 5 -c 4
#./submit.py -q tomorrow -y 2018 -MC -MT TTbar -n 5 -c 4

./submit.py -q tomorrow -y 2016 -n 2 -c 16
./submit.py -q tomorrow -y 2017 -n 2 -c 16
./submit.py -q tomorrow -y 2018 -n 2 -c 16

