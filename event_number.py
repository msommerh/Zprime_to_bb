#! /usr/bin/env python

import sys
from argparse import ArgumentParser
from commands import getoutput
import json

if __name__ == "__main__":
  parser = ArgumentParser()
  parser.add_argument('-s', '--sample',   dest='sample', type=str, default='', action='store',
                                         help="DAS dataset" )
  parser.add_argument('-f', '--file',   dest='file', type=str, default='', action='store',
                                         help="file containing DAS datasets" )
  args = parser.parse_args()

else:
  args = None


def event_number(sample):
    cmd = 'dasgoclient -query="summary dataset={} instance=prod/global"'.format(sample)
    summary_str = getoutput( cmd )
    summary_str = "summary = "+summary_str
    exec summary_str
    return summary[0]['num_event']
    
if __name__ == "__main__":
    if args.sample != '':
        print event_number(args.sample)
    elif args.file != '':
        
         with open(args.file, 'r') as json_file:
                    data_sets = json.load(json_file)        
    
                    for sample in data_sets.keys():
                        print sample, ":", event_number(data_sets[sample]), "events"

    else:
        years = ['2016', '2017', '2018']
        nEvents = {}
        for year in years:  
            nEvents[year] = {}
            f = 'samples/samples_MC_signal_{}.json'.format(year)
            with open(f, 'r') as json_file:
                data_sets = json.load(json_file)
                for sample in data_sets.keys():
                    nEvents[year][int(sample.replace("MC_signal_"+year+"_M",""))] =  event_number(data_sets[sample])
        print nEvents

        mass_points = [600, 800, 1000, 1200, 1400, 1600, 1800, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 7000, 8000]
           
        for m in mass_points:
            
            print "M"+str(m), ":", "'genEvents' : { '2016':"+str(nEvents['2016'][m])+", '2017':"+str(nEvents['2017'][m])+", '2018':"+str(nEvents['2018'][m])+"}"

