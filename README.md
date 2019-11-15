# Z' to bb analysis

## Process samples from DAS

### submit the samples:   

[year]: 2016, 2017, 2018

MC signal:
```
./submit.py -q longlunch -y [year] -MC -MT signal
```
MC background:     [MC_type]: QCD, TTbar
```
./submit.py -q tomorrow -y [year] -MC -MT [MC_type] -n 5 -c 4
```
data:
```
./submit.py -q tomorrow -y [year] -n 1 -c 16
```

### check if samples have finished correctly:
```
./check_submission.sh
```

### resubmit erroneous samples by putting the sample name in the corresponding file in *resubmission/[sample_name]* and run:
```
./submit.py [same options as original submission (or slightly adjusted)] -rs resubmission/[sample_name]
```
if the submission only crashes on a single file, identify the file nr from the stdout and resubmit via:
```
./submit.py [same options as original submission] -rs resubmission/[sample_name] -rf [file_nr]
```

output in: */eos/user/m/msommerh/Zprime_to_bb_analysis/*


## Postprocess samples

### add weights, even to the data and MC signal:    

[year]: 2016, 2017, 2018;   [MC_type]: signal, QCD, TTbar
```
./postprocessors/addWeights.py -y [year] -MC -MT [MC_type]
./postprocessors/addWeights.py -y [year] 
```
output in /eos/user/m/msommerh/Zprime_to_bb_analysis/weighted

### skim the samples:
```
./postprocessors/skim.py
```
output in */afs/cern.ch/work/m/msommerh/public/Zprime_to_bb_Analysis/Skim*


## plot MC/data comparison

[year] = 2016, 2017, 2018, run2;   [btagging]: tight, medium, loose

```
./Plot.py -v jj_mass -c "preselection" -y [year] -b [btagging]
./Plot.py -B -v jj_mass -c "1b" -y [year] -b [btagging]
./Plot.py -B -v jj_mass -c "2b" -y [year] -b [btagging]
```

output in: *plots/[preselection, 1b, 2b]/*


## apply fit on QCD_TTbar/data and signal

 [year]: 2016, 2017, 2018, run2;   [btagging]: tight, medium, loose

fit on the MC signal: 
```
./Signal_Fitter.py -y [year] -b [btagging]
```

fit on MC background:
```
./submit_Bkg_Fitter.py -q tomorrow -y [year] -MC -b [btagging]
```

fit on data: (currently not advised until blinding implemented or explicitly allowed)

~~`./submit_Bkg_Fitter.py -q tomorrow -y [year] -b [btagging]`~~


output in:

plots: *plots/[btagging]/[data_type]_[year]/*

workspace: *workspace/[btagging]/*


## create datacards

(works independently of the actual fits)
[year]: 2016, 2017, 2018, run2;   [btagging]: tight, medium, loose

MC:
```
./Datacards.py -M -y [year] -b [btagging]
```
data:
```
./Datacards.py -y [year] -b [btagging]
```
output in: *datacards/[btagging]/*

### combine cards of different btagging categories: 
(needs to be run with the CC7 setup)
```
./combineCards.sh [btagging]
```
output in: *datacards/[btagging]/combined/*


## limits plots

[year]: 2016, 2017, 2018, run2;   [btagging]: tight, medium, loose

### run combine:

MC:
```
./submit_combine.py -MC -q workday -y [year] -b [btagging]
```
data: (currently not advised until blinding implemented or explicitly allowed)

~~`./submit_combine.py -q workday -y [year] -b [btagging]`~~

output in: *combine/limits/[btagging]/*

### plot the limits:

MC:
```
./limit.py -M -y [year] -b [btagging]
```
data: (currently not advised until blinding implemented or explicitly allowed)

~~`./limit.py -y [year] -b [btagging]`~~

output in: *combine/plotsLimit/*

