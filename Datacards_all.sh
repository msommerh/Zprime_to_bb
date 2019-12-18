#!/bin/bash

#./Datacards.py -M -y 2016 -b semimedium
#./Datacards.py -M -y 2016 -b loose
./Datacards.py -M -y 2016 -b medium
#./Datacards.py -M -y 2016 -b tight
#./Datacards.py -M -y 2017 -b semimedium
#./Datacards.py -M -y 2017 -b loose
./Datacards.py -M -y 2017 -b medium
#./Datacards.py -M -y 2017 -b tight
#./Datacards.py -M -y 2018 -b semimedium
#./Datacards.py -M -y 2018 -b loose
./Datacards.py -M -y 2018 -b medium
#./Datacards.py -M -y 2018 -b tight
#./Datacards.py -M -y run2 -b semimedium
#./Datacards.py -M -y run2 -b loose
./Datacards.py -M -y run2 -b medium
#./Datacards.py -M -y run2 -b tight

#./combineCards_mumu.sh semimedium
#./combineCards_mumu.sh loose
./combineCards_mumu.sh medium
#./combineCards_mumu.sh tight
#
#./combineCards_run2_mumu.sh semimedium
#./combineCards_run2_mumu.sh loose
./combineCards_run2_mumu.sh medium
#./combineCards_run2_mumu.sh tight
