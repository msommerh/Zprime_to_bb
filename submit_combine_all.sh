#!/bin/bash

#./submit_combine.py -MC -q longlunch -y run2 -b tight
#./submit_combine.py -MC -q longlunch -y run2 -b medium
#./submit_combine.py -MC -q longlunch -y run2 -b loose
#./submit_combine.py -MC -q longlunch -y run2 -b semimedium
#./submit_combine.py -MC -q longlunch -y run2c -b tight
./submit_combine.py -MC -q espresso -y run2c -b medium
#./submit_combine.py -MC -q longlunch -y run2c -b loose
#./submit_combine.py -MC -q longlunch -y run2c -b semimedium

#./submit_combine.py -MC -q longlunch -y 2018 -b tight
./submit_combine.py -MC -q espresso -y 2018 -b medium
#./submit_combine.py -MC -q longlunch -y 2018 -b loose
#./submit_combine.py -MC -q longlunch -y 2018 -b semimedium
#./submit_combine.py -MC -q longlunch -y 2017 -b tight
./submit_combine.py -MC -q espresso -y 2017 -b medium
#./submit_combine.py -MC -q longlunch -y 2017 -b loose
#./submit_combine.py -MC -q longlunch -y 2017 -b semimedium
#./submit_combine.py -MC -q longlunch -y 2016 -b tight
./submit_combine.py -MC -q espresso -y 2016 -b medium
#./submit_combine.py -MC -q longlunch -y 2016 -b loose
#./submit_combine.py -MC -q longlunch -y 2016 -b semimedium
