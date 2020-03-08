#!/bin/bash

#./MANtag_Bkg_Fitter.py -y 2016 -b loose -c bb &
#./MANtag_Bkg_Fitter.py -y 2016 -b loose -c bq &
#./MANtag_Bkg_Fitter.py -y 2016 -b loose -c mumu &
#./MANtag_Bkg_Fitter.py -y 2017 -b loose -c bb &
#./MANtag_Bkg_Fitter.py -y 2017 -b loose -c bq &
#./MANtag_Bkg_Fitter.py -y 2017 -b loose -c mumu &
#./MANtag_Bkg_Fitter.py -y 2018 -b loose -c bb &
#./MANtag_Bkg_Fitter.py -y 2018 -b loose -c bq &
#./MANtag_Bkg_Fitter.py -y 2018 -b loose -c mumu &
#./MANtag_Bkg_Fitter.py -y run2 -b loose -c bb &
#./MANtag_Bkg_Fitter.py -y run2 -b loose -c bq &
#./MANtag_Bkg_Fitter.py -y run2 -b loose -c mumu &

#./MANtag_Bkg_Fitter.py -y 2016 -b loose -c bb &
./MANtag_Bkg_Fitter.py -y 2016 -b loose -c mumu -f 3 &
#./MANtag_Bkg_Fitter.py -y 2017 -b loose -c bb &
#./MANtag_Bkg_Fitter.py -y run2 -b loose -c bb -f 3 &
#./MANtag_Bkg_Fitter.py -y run2 -b loose -c bq -f 3 &

./MANtag_Bkg_Fitter.py -y 2016 -b loose -c bq -f 4 &
./MANtag_Bkg_Fitter.py -y 2017 -b loose -c bq -f 3 &
./MANtag_Bkg_Fitter.py -y 2017 -b loose -c mumu -f 4 &
./MANtag_Bkg_Fitter.py -y 2018 -b loose -c bq -f 4 &
./MANtag_Bkg_Fitter.py -y 2018 -b loose -c bb -f 4 &
./MANtag_Bkg_Fitter.py -y 2018 -b loose -c mumu -f 4 &

#./MANtag_Bkg_Fitter.py -y run2 -b loose -c mumu -f 4 &

wait

