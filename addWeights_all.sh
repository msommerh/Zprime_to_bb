#!/bin/bash

./postprocessors/addWeight.py -y 2016 -MC -MT signal
./postprocessors/addWeight.py -y 2016 -MC -MT QCD
./postprocessors/addWeight.py -y 2016 -MC -MT TTbar
#./postprocessors/addWeight.py -y 2016

./postprocessors/addWeight.py -y 2017 -MC -MT signal
./postprocessors/addWeight.py -y 2017 -MC -MT QCD
./postprocessors/addWeight.py -y 2017 -MC -MT TTbar
#./postprocessors/addWeight.py -y 2017

./postprocessors/addWeight.py -y 2018 -MC -MT signal
./postprocessors/addWeight.py -y 2018 -MC -MT QCD
./postprocessors/addWeight.py -y 2018 -MC -MT TTbar
#./postprocessors/addWeight.py -y 2018
