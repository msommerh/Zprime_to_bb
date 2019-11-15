#! /usr/bin/env python

import sys
import os, re, glob
from commands import getoutput
from fnmatch import fnmatch
import itertools
from argparse import ArgumentParser
import json
#import checkFiles
#from checkFiles import getSampleShortName, matchSampleToPattern, header, ensureDirectory

if __name__ == "__main__":
  parser = ArgumentParser()
  parser.add_argument('-q', '--queue',   dest='queue', choices=['espresso', 'microcentury', 'longlunch', 'workday', 'tomorrow', 'testmatch', 'nextweek'], type=str, default='tomorrow', action='store',
                                         help="select queue for submission" )
  parser.add_argument('-y', '--year',    dest='year', type=str, default='2016', action='store', choices=['2016','2017','2018','run2'],
                                         help="set year, type run2 for combined submission." )
  parser.add_argument('-MC', '--isMC',   dest='isMC',  action='store_true', default=False,
                                         help="Select this if the sample is MC, otherwise it is flagged as data.")
  parser.add_argument("-b", "--btagging", action="store", type=str, dest="btagging", default="tight", choices=['tight', 'medium', 'loose'])
  parser.add_argument("-c", "--category", action="store", type=str, dest="category", default="", choices=['', 'bb', 'bq'],
                                         help="Choose b-tagging category (bb or bq) if combine should run merely on a single category.")
  args = parser.parse_args()
  #checkFiles.args = args

#jobflavour = 'espresso' #max 30min
#jobflavour = 'microcentury' #max 1h
#jobflavour = 'longlunch' #max 2h
#jobflavour = 'workday' #max 8h
#jobflavour = 'tomorrow' #max 1d
#jobflavour = 'testmatch' #max 3d

else:
  args = None

mass_points = range(1200,8001,100)
nJobs = len(mass_points)

def submitJobs():
    path = "/afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/src/NanoTreeProducer"
    workdir = "submission_files/tmp_combine{category}_{year}_{btagging}{suffix}".format(category="_"+args.category if args.category!="" else "", year=args.year, btagging=args.btagging, suffix="_MC" if args.isMC else "")
    if not os.path.exists(workdir):
        os.makedirs(workdir)
        print "Directory "+workdir+" created."
    else:
        print "Directory "+workdir+" already exists."
    os.chdir(workdir)

    #submit job
    os.system("cp /afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/src/NanoTreeProducer/combine{}.sh ./combine_{}_{}{}.sh".format("_single" if args.category!="" else "", args.year, args.btagging, "_"+args.category if args.category != "" else ""))
    os.system("chmod 755 combine_{}_{}{}.sh".format(args.year, args.btagging, "_"+args.category if args.category != "" else ""))
    makeSubmitFileCondor(args.queue, nJobs)
    os.system("condor_submit submit.sub")
    print "jobs submitted"
    os.chdir("../..")

def makeSubmitFileCondor(jobflavour, nJobs):
    print "make options file for condor job submission"
    suffix=""
    if args.category!="": suffix+=" "+args.category
    submitfile = open("submit.sub", "w")
    submitfile.write("executable            = combine_{}_{}{}.sh\n".format(args.year, args.btagging, "_"+args.category if args.category != "" else ""))
    submitfile.write("arguments             = "+str(int(args.isMC))+" "+str(args.year)+" "+args.btagging+" $(ProcId)"+suffix+"\n")
    submitfile.write("output                = "+str(args.year)+"_"+args.btagging+".$(ClusterId).$(ProcId).out\n")
    submitfile.write("error                 = "+str(args.year)+"_"+args.btagging+".$(ClusterId).$(ProcId).err\n")
    submitfile.write("log                   = "+str(args.year)+"_"+args.btagging+".$(ClusterId).log\n")
    submitfile.write('+JobFlavour           = "'+jobflavour+'"\n')
    submitfile.write('transfer_output_files = ""\n')
    submitfile.write("queue {}".format(nJobs))
    submitfile.close()

def main():

        submitJobs()

        print
        print "your jobs:"
        os.system("condor_q")
        userName=os.environ['USER']
        print
        print 'Done submitting jobs!'
        print

if __name__ == "__main__":
    print
    main()
    print "done"
