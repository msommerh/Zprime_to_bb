#!/bin/bash

####################### input arguments ########################

plot_type=$1 
## possible choices:
### jj_mass
### jpt
### jeta
### jphi
### fatjetmass
### eff
### acc
### all

################################################################

# jj_mass_widejet:

if [[ $plot_type == 'jj_mass' || $plot_type == 'all' ]]; then
    echo "plotting jj_mass"
    ./Plot.py -B -v jj_mass_widejet -c "preselection" -y 2018 
    ./Plot.py -B -v jj_mass_widejet -c "1b" -y 2018 -b medium
    ./Plot.py -B -v jj_mass_widejet -c "2b" -y 2018 -b medium
    ./Plot.py -B -v jj_mass_widejet -c "preselection" -y 2017
    ./Plot.py -B -v jj_mass_widejet -c "1b" -y 2017 -b medium
    ./Plot.py -B -v jj_mass_widejet -c "2b" -y 2017 -b medium
    ./Plot.py -B -v jj_mass_widejet -c "preselection" -y 2016
    ./Plot.py -B -v jj_mass_widejet -c "1b" -y 2016 -b medium
    ./Plot.py -B -v jj_mass_widejet -c "2b" -y 2016 -b medium
    ./Plot.py -B -v jj_mass_widejet -c "preselection" -y run2
    ./Plot.py -B -v jj_mass_widejet -c "1b" -y run2 -b medium
    ./Plot.py -B -v jj_mass_widejet -c "2b" -y run2 -b medium
fi


### jpt:

if [[ $plot_type == 'jpt' || $plot_type == 'all' ]]; then
    echo "plotting jpt"
    ./Plot.py -B -v jpt_1 -c "preselection" -y 2018 
    ./Plot.py -B -v jpt_1 -c "1b" -y 2018 -b medium
    ./Plot.py -B -v jpt_1 -c "2b" -y 2018 -b medium
    ./Plot.py -B -v jpt_1 -c "preselection" -y 2017
    ./Plot.py -B -v jpt_1 -c "1b" -y 2017 -b medium
    ./Plot.py -B -v jpt_1 -c "2b" -y 2017 -b medium
    ./Plot.py -B -v jpt_1 -c "preselection" -y 2016
    ./Plot.py -B -v jpt_1 -c "1b" -y 2016 -b medium
    ./Plot.py -B -v jpt_1 -c "2b" -y 2016 -b medium
    ./Plot.py -B -v jpt_1 -c "preselection" -y run2
    ./Plot.py -B -v jpt_1 -c "1b" -y run2 -b medium
    ./Plot.py -B -v jpt_1 -c "2b" -y run2 -b medium
    ./Plot.py -B -v jpt_2 -c "preselection" -y 2018 
    ./Plot.py -B -v jpt_2 -c "1b" -y 2018 -b medium
    ./Plot.py -B -v jpt_2 -c "2b" -y 2018 -b medium
    ./Plot.py -B -v jpt_2 -c "preselection" -y 2017
    ./Plot.py -B -v jpt_2 -c "1b" -y 2017 -b medium
    ./Plot.py -B -v jpt_2 -c "2b" -y 2017 -b medium
    ./Plot.py -B -v jpt_2 -c "preselection" -y 2016
    ./Plot.py -B -v jpt_2 -c "1b" -y 2016 -b medium
    ./Plot.py -B -v jpt_2 -c "2b" -y 2016 -b medium
    ./Plot.py -B -v jpt_2 -c "preselection" -y run2
    ./Plot.py -B -v jpt_2 -c "1b" -y run2 -b medium
    ./Plot.py -B -v jpt_2 -c "2b" -y run2 -b medium
fi


### jeta:

if [[ $plot_type == 'jeta' || $plot_type == 'all' ]]; then
    echo "plotting jeta"
    ./Plot.py -B -v jeta_1 -c "preselection" -y 2018 
    ./Plot.py -B -v jeta_1 -c "1b" -y 2018 -b medium
    ./Plot.py -B -v jeta_1 -c "2b" -y 2018 -b medium
    ./Plot.py -B -v jeta_1 -c "preselection" -y 2017
    ./Plot.py -B -v jeta_1 -c "1b" -y 2017 -b medium
    ./Plot.py -B -v jeta_1 -c "2b" -y 2017 -b medium
    ./Plot.py -B -v jeta_1 -c "preselection" -y 2016
    ./Plot.py -B -v jeta_1 -c "1b" -y 2016 -b medium
    ./Plot.py -B -v jeta_1 -c "2b" -y 2016 -b medium
    ./Plot.py -B -v jeta_1 -c "preselection" -y run2
    ./Plot.py -B -v jeta_1 -c "1b" -y run2 -b medium
    ./Plot.py -B -v jeta_1 -c "2b" -y run2 -b medium
    ./Plot.py -B -v jeta_2 -c "preselection" -y 2018 
    ./Plot.py -B -v jeta_2 -c "1b" -y 2018 -b medium
    ./Plot.py -B -v jeta_2 -c "2b" -y 2018 -b medium
    ./Plot.py -B -v jeta_2 -c "preselection" -y 2017
    ./Plot.py -B -v jeta_2 -c "1b" -y 2017 -b medium
    ./Plot.py -B -v jeta_2 -c "2b" -y 2017 -b medium
    ./Plot.py -B -v jeta_2 -c "preselection" -y 2016
    ./Plot.py -B -v jeta_2 -c "1b" -y 2016 -b medium
    ./Plot.py -B -v jeta_2 -c "2b" -y 2016 -b medium
    ./Plot.py -B -v jeta_2 -c "preselection" -y run2
    ./Plot.py -B -v jeta_2 -c "1b" -y run2 -b medium
    ./Plot.py -B -v jeta_2 -c "2b" -y run2 -b medium
fi


### jphi:

if [[ $plot_type == 'jphi' || $plot_type == 'all' ]]; then
    echo "plotting jphi"
    ./Plot.py -B -v jphi_1 -c "preselection" -y 2018 
    ./Plot.py -B -v jphi_1 -c "1b" -y 2018 -b medium
    ./Plot.py -B -v jphi_1 -c "2b" -y 2018 -b medium
    ./Plot.py -B -v jphi_1 -c "preselection" -y 2017
    ./Plot.py -B -v jphi_1 -c "1b" -y 2017 -b medium
    ./Plot.py -B -v jphi_1 -c "2b" -y 2017 -b medium
    ./Plot.py -B -v jphi_1 -c "preselection" -y 2016
    ./Plot.py -B -v jphi_1 -c "1b" -y 2016 -b medium
    ./Plot.py -B -v jphi_1 -c "2b" -y 2016 -b medium
    ./Plot.py -B -v jphi_1 -c "preselection" -y run2
    ./Plot.py -B -v jphi_1 -c "1b" -y run2 -b medium
    ./Plot.py -B -v jphi_1 -c "2b" -y run2 -b medium
    ./Plot.py -B -v jphi_2 -c "preselection" -y 2018 
    ./Plot.py -B -v jphi_2 -c "1b" -y 2018 -b medium
    ./Plot.py -B -v jphi_2 -c "2b" -y 2018 -b medium
    ./Plot.py -B -v jphi_2 -c "preselection" -y 2017
    ./Plot.py -B -v jphi_2 -c "1b" -y 2017 -b medium
    ./Plot.py -B -v jphi_2 -c "2b" -y 2017 -b medium
    ./Plot.py -B -v jphi_2 -c "preselection" -y 2016
    ./Plot.py -B -v jphi_2 -c "1b" -y 2016 -b medium
    ./Plot.py -B -v jphi_2 -c "2b" -y 2016 -b medium
    ./Plot.py -B -v jphi_2 -c "preselection" -y run2
    ./Plot.py -B -v jphi_2 -c "1b" -y run2 -b medium
    ./Plot.py -B -v jphi_2 -c "2b" -y run2 -b medium
fi


### fatjetmass_1:

if [[ $plot_type == 'fatjetmass' || $plot_type == 'all' ]]; then
    echo "plotting fatjetmass"
    ./Plot.py -B -v fatjetmass_1 -c "preselection" -y 2018 
    ./Plot.py -B -v fatjetmass_1 -c "1b" -y 2018 -b medium
    ./Plot.py -B -v fatjetmass_1 -c "2b" -y 2018 -b medium
    ./Plot.py -B -v fatjetmass_1 -c "preselection" -y 2017
    ./Plot.py -B -v fatjetmass_1 -c "1b" -y 2017 -b medium
    ./Plot.py -B -v fatjetmass_1 -c "2b" -y 2017 -b medium
    ./Plot.py -B -v fatjetmass_1 -c "preselection" -y 2016
    ./Plot.py -B -v fatjetmass_1 -c "1b" -y 2016 -b medium
    ./Plot.py -B -v fatjetmass_1 -c "2b" -y 2016 -b medium
    ./Plot.py -B -v fatjetmass_1 -c "preselection" -y run2
    ./Plot.py -B -v fatjetmass_1 -c "1b" -y run2 -b medium
    ./Plot.py -B -v fatjetmass_1 -c "2b" -y run2 -b medium
fi


### efficiency:

if [[ $plot_type == 'eff' || $plot_type == 'all' ]]; then
    echo "plotting the efficiency"
    ./Plot.py -e -y run2 -b medium
    ./Plot.py -e -y 2018 -b medium
    ./Plot.py -e -y 2017 -b medium
    ./Plot.py -e -y 2016 -b medium
fi


### acceptance:

if [[ $plot_type == 'acc' || $plot_type == 'all' ]]; then
    echo "plotting the acceptance"
    ./Plot.py -a -y run2
    ./Plot.py -a -y 2018
    ./Plot.py -a -y 2017
    ./Plot.py -a -y 2016
fi

