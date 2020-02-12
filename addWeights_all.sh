#!/bin/bash

./postprocessors/addWeight.py -y 2016 -MC -MT signal -s
./postprocessors/addWeight.py -y 2016 -MC -MT QCD -s
./postprocessors/addWeight.py -y 2016 -MC -MT TTbar -s
#./postprocessors/addWeight.py -y 2016

#./postprocessors/addWeight.py -y 2017 -MC -MT signal -s
#./postprocessors/addWeight.py -y 2017 -MC -MT QCD -s
#./postprocessors/addWeight.py -y 2017 -MC -MT TTbar -s
#./postprocessors/addWeight.py -y 2017

#./postprocessors/addWeight.py -y 2018 -MC -MT signal -s
#./postprocessors/addWeight.py -y 2018 -MC -MT QCD -s
#./postprocessors/addWeight.py -y 2018 -MC -MT TTbar -s #FIXME remove -s later
#./postprocessors/addWeight.py -y 2018
