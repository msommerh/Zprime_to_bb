#!/bin/bash

./Datacards.py -y 2016 -b medium -d -s 2  > /dev/null
./Datacards.py -y 2017 -b medium -d -s 2  > /dev/null 
./Datacards.py -y 2018 -b medium -d -s 2  > /dev/null
./combineCards_bias.sh medium 1  > /dev/null
cp datacards/medium/bias/combined/fully_combined_run2_M* datacards/medium/bias/combined/2sigma/
echo "combined 2 sigma signal. check out datacards/medium/bias/combined/2sigma/"

./Datacards.py -y 2016 -b medium -d -s 5  > /dev/null
./Datacards.py -y 2017 -b medium -d -s 5  > /dev/null 
./Datacards.py -y 2018 -b medium -d -s 5  > /dev/null
./combineCards_bias.sh medium 1  > /dev/null
cp datacards/medium/bias/combined/fully_combined_run2_M* datacards/medium/bias/combined/5sigma/
echo "combined 2 sigma signal. check out datacards/medium/bias/combined/5sigma/"

./Datacards.py -y 2016 -b medium -d -s ""  > /dev/null
./Datacards.py -y 2017 -b medium -d -s ""  > /dev/null 
./Datacards.py -y 2018 -b medium -d -s ""  > /dev/null
./combineCards_bias.sh medium 1  > /dev/null

echo "combined 0 signal. check out datacards/medium/bias/combined/"

