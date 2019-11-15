#!/bin/bash

./submit_combine.py -MC -q workday -y run2 -b tight
#./submit_combine.py -MC -q workday -y run2 -b medium
./submit_combine.py -MC -q workday -y run2 -b loose
./submit_combine.py -MC -q workday -y 2018 -b tight
./submit_combine.py -MC -q workday -y 2018 -b medium
./submit_combine.py -MC -q workday -y 2018 -b loose
./submit_combine.py -MC -q workday -y 2017 -b tight
./submit_combine.py -MC -q workday -y 2017 -b medium
./submit_combine.py -MC -q workday -y 2017 -b loose
./submit_combine.py -MC -q workday -y 2016 -b tight
./submit_combine.py -MC -q workday -y 2016 -b medium
./submit_combine.py -MC -q workday -y 2016 -b loose
