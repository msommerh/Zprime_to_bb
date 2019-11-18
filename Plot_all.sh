#!/bin/bash

./Plot.py -v jj_mass -c "preselection" -y run2
./Plot.py -B -v jj_mass -c "1b" -y run2 -b tight
./Plot.py -B -v jj_mass -c "1b" -y run2 -b medium
./Plot.py -B -v jj_mass -c "1b" -y run2 -b loose
./Plot.py -B -v jj_mass -c "2b" -y run2 -b tight
./Plot.py -B -v jj_mass -c "2b" -y run2 -b medium
./Plot.py -B -v jj_mass -c "2b" -y run2 -b loose

./Plot.py -v jj_mass -c "preselection" -y 2018 
./Plot.py -B -v jj_mass -c "1b" -y 2018 -b tight
./Plot.py -B -v jj_mass -c "1b" -y 2018 -b medium
./Plot.py -B -v jj_mass -c "1b" -y 2018 -b loose
./Plot.py -B -v jj_mass -c "2b" -y 2018 -b tight
./Plot.py -B -v jj_mass -c "2b" -y 2018 -b medium
./Plot.py -B -v jj_mass -c "2b" -y 2018 -b loose

./Plot.py -v jj_mass -c "preselection" -y 2017
./Plot.py -B -v jj_mass -c "1b" -y 2017 -b tight
./Plot.py -B -v jj_mass -c "1b" -y 2017 -b medium
./Plot.py -B -v jj_mass -c "1b" -y 2017 -b loose
./Plot.py -B -v jj_mass -c "2b" -y 2017 -b tight
./Plot.py -B -v jj_mass -c "2b" -y 2017 -b medium
./Plot.py -B -v jj_mass -c "2b" -y 2017 -b loose

./Plot.py -v jj_mass -c "preselection" -y 2016
./Plot.py -B -v jj_mass -c "1b" -y 2016 -b tight
./Plot.py -B -v jj_mass -c "1b" -y 2016 -b medium
./Plot.py -B -v jj_mass -c "1b" -y 2016 -b loose
./Plot.py -B -v jj_mass -c "2b" -y 2016 -b tight
./Plot.py -B -v jj_mass -c "2b" -y 2016 -b medium
./Plot.py -B -v jj_mass -c "2b" -y 2016 -b loose
