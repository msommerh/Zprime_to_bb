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
  parser.add_argument("-c", "--category", action="store", type=str, dest="category", default="", choices=['bb','bq','qq',''],
                                         help="b-tagging category for the fitting to run on: bb, bq, qq. Leave empty to run all three")
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

def submitJobs(title, category):
    #path = os.getcwd()
    path = "/afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/src/NanoTreeProducer"
    workdir = "submission_files/tmp_fitting_"+title
    if not os.path.exists(workdir):
        os.makedirs(workdir)
        print "Directory "+workdir+" created."
    else:
        print "Directory "+workdir+" already exists."
    os.chdir(workdir)

    #write executable file for submission
    with open('job.sh', 'w') as fout:
        fout.write("#!/bin/sh\n")
        fout.write("echo\n")
        fout.write("echo\n")
        fout.write("echo 'START---------------'\n")
        fout.write("echo 'WORKDIR ' ${PWD}\n")

        fout.write("cd "+str(path)+"\n")
        fout.write("export SCRAM_ARCH=slc6_amd64_gcc700\n" )
        fout.write("if [ -r CMSSW_10_3_3/src ] ; then\n")
        fout.write("    echo 'release CMSSW_10_3_3 already exists'\n")
        fout.write("else\n")
        fout.write("    scram p CMSSW CMSSW_10_3_3\n")
        fout.write("fi\n")
        fout.write("cd CMSSW_10_3_3/src\n")
        fout.write("eval `scram runtime -sh`\n")
        fout.write("cd -\n" )
        fout.write("echo 'cmssw release = ' $CMSSW_BASE\n")
        fout.write("source /afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/src/NanoTreeProducer/setupEnv.sh\n")

        fout.write("export X509_USER_PROXY=/afs/cern.ch/user/m/msommerh/x509up_msommerh\n")
        fout.write("use_x509userproxy=true\n")

        fout.write("./Bkg_Fitter.py -S {}{}{}\n".format('-M ' if args.isMC else '', '-y '+args.year, ' -c '+category))
        fout.write("echo 'STOP---------------'\n")
        fout.write("echo\n")
        fout.write("echo\n")

    #submit job
    os.system("chmod 755 job.sh")
    os.system("mv job.sh "+title+".sh")
    makeSubmitFileCondor(title+".sh", title, args.queue)
    os.system("condor_submit submit.sub")
    print "job submitted"
    os.chdir("../..")

def makeSubmitFileCondor(exe, jobname, jobflavour):
    print "make options file for condor job submission"
    submitfile = open("submit.sub", "w")
    submitfile.write("executable            = "+exe+"\n")
    submitfile.write("arguments             = $(ClusterID) $(ProcId)\n")
    submitfile.write("output                = "+jobname+".$(ClusterId).$(ProcId).out\n")
    submitfile.write("error                 = "+jobname+".$(ClusterId).$(ProcId).err\n")
    submitfile.write("log                   = "+jobname+".$(ClusterId).log\n")
    submitfile.write('+JobFlavour           = "'+jobflavour+'"\n')
    submitfile.write("queue")
    submitfile.close()

def main():

        if args.category != '':
            title = "MC_QCD_TTbar" if args.isMC else "data"
            title+= "_"+args.year+"_"+args.category
            submitJobs(title, args.category)
        else:
            for category in ['bb', 'bq', 'qq']:
                title = "MC_QCD_TTbar" if args.isMC else "data"
                title+= "_"+args.year+"_"+category
                submitJobs(title, category)

        print
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
