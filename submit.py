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
  #parser.add_argument('-f', '--force',   dest='force', action='store_true', default=False,
  #                                       help="submit jobs without asking confirmation" )
  #parser.add_argument('-y', '--year',    dest='years', choices=[2016,2017,2018], type=int, nargs='+', default=[2017], action='store',
  #                                       help="select year" )
  #parser.add_argument('-c', '--channel', dest='channels', choices=['ll'], type=str, nargs='+', default=['ll'], action='store',
  #                                       help="channels to submit" )
  #parser.add_argument('-s', '--sample',  dest='samples', type=str, nargs='+', default=[ ], action='store',
  #                                       help="filter these samples, glob patterns (wildcards * and ?) are allowed." )
  #parser.add_argument('-x', '--veto',    dest='vetos', nargs='+', default=[ ], action='store',
  #                                       help="veto this sample" )
  #parser.add_argument('-t', '--type',    dest='type', choices=['data','mc'], type=str, default=None, action='store',
  #                                       help="filter data or MC to submit" )
  #parser.add_argument('-T', '--tes',     dest='tes', type=float, default=1.0, action='store',
  #                                       help="tau energy scale" )
  #parser.add_argument('-L', '--ltf',     dest='ltf', type=float, default=1.0, action='store',
  #                                       help="lepton to tau fake energy scale" )
  #parser.add_argument('-J', '--jtf',     dest='jtf', type=float, default=1.0, action='store',
  #                                       help="jet to tau fake energy scale" )
  #parser.add_argument('-d', '--das',     dest='useDAS', action='store_true', default=False,
  #                                       help="get file list from DAS" )
  #parser.add_argument('-n', '--njob',    dest='nFilesPerJob', action='store', type=int, default=-1,
  #                                       help="number of files per job" )
  #parser.add_argument('-q', '--queue',   dest='queue', choices=['all.q','short.q','long.q'], type=str, default=None, action='store',
  #                                       help="select queue for submission" )
  #parser.add_argument('-m', '--mock',    dest='mock', action='store_true', default=False,
  #                                       help="mock-submit jobs for debugging purposes" )
  parser.add_argument('-v', '--verbose', dest='verbose', default=False, action='store_true',
                                         help="set verbose" )
  parser.add_argument('-y', '--year', 	 dest='year', type=int, default=2016, action='store',
                                         help="set year, type '0' for QCD" )

  args = parser.parse_args()
  #checkFiles.args = args


else:
  args = None

#class bcolors:
#    HEADER = '\033[95m'
#    OKBLUE = '\033[94m'
#    OKGREEN = '\033[92m'
#    WARNING = '\033[93m'
#    FAIL = '\033[91m'
#    ENDC = '\033[0m'
#    BOLD = '\033[1m'
#    UNDERLINE = '\033[4m'

def getFileListDAS(dataset):
	"""Get list of files from DAS."""
	dataset  = dataset.replace('__','/')
	instance = 'prod/global'
	if 'USER' in dataset:
	    instance = 'prod/phys03'
	cmd = 'dasgoclient -query="file dataset={} instance={}"'.format(dataset, instance)
	if args.verbose:
	  print "Executing ",cmd
	cmd_out  = getoutput( cmd )
	tmpList  = cmd_out.split(os.linesep)
	filelist = [ ]
	for line in tmpList:
	  if '.root' in line:
	    #filelist.append("root://xrootd-cms.infn.it/"+line)
	    filelist.append("root://cms-xrd-global.cern.ch/"+line)
	return filelist


def submitJobs(title, infiles, outdir, jobflavour):
    #path = os.getcwd()
    path = "/afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/src/NanoTreeProducer"
    if not os.path.exists(outdir+title):
        os.makedirs(outdir+title)
	print "Directory "+outdir+title+" created."
    else:
	print "Directory "+outdir+title+" already exists."
    workdir = "submission_files/tmp_"+title
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
	#fout.write("cd /afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/src/NanoTreeProducer\n")
        fout.write("echo 'cmssw release = ' $CMSSW_BASE\n")
	fout.write("source /afs/cern.ch/user/m/msommerh/CMSSW_10_3_3/src/NanoTreeProducer/setupEnv.sh\n")

	fout.write("export X509_USER_PROXY=/afs/cern.ch/user/m/msommerh/x509up_msommerh\n")
	fout.write("use_x509userproxy=true\n")

        fout.write("./postprocessors/Zprime_to_bb.py -t {} -i {} -o {} -y {}\n".format(title, infiles, outdir+title, args.year))
        fout.write("echo 'STOP---------------'\n")
        fout.write("echo\n")
        fout.write("echo\n")

    #submit job
    os.system("chmod 755 job.sh")
    os.system("mv job.sh "+title+".sh")
    makeSubmitFileCondor(title+".sh", title, jobflavour)
    os.system("condor_submit submit.sub")
    print "job submitted"
    os.chdir("../..")

def makeSubmitFileCondor(exe, jobname, jobflavour):
    print "make options file for condor job submission"
    submitfile = open("submit.sub", "w")
    submitfile.write("executable  	    = "+exe+"\n")
    submitfile.write("arguments             = $(ClusterID) $(ProcId)\n")
    submitfile.write("output                = "+jobname+".$(ClusterId).$(ProcId).out\n")
    submitfile.write("error                 = "+jobname+".$(ClusterId).$(ProcId).err\n")
    submitfile.write("log                   = "+jobname+".$(ClusterId).log\n")
    submitfile.write('+JobFlavour           = "'+jobflavour+'"\n')
    submitfile.write("queue")
    submitfile.close()

def main():

	outdir = "/eos/user/m/msommerh/Zprime_to_bb_analysis/"
	
	#infiles = "filelists/default.txt"
	#title = "test_QCD"
	#submitJobs(title+"_1", infiles, outdir, "longlunch")
	#submitJobs(title+"_2", infiles.replace(".txt","2.txt"), outdir, "longlunch")
	#submitJobs(title+"_3", infiles.replace(".txt","3.txt"), outdir, "longlunch")
	#sys.exit()

	## load data sets from file
	if args.year in [2016,2017,2018]:
		data_set_file = 'samples_{}.json'.format(args.year)
	elif args.year == 0:
		data_set_file = 'samples_QCD.json'
	else:
		print "Unknown year. Abort submission!!"
		sys.exit()

	with open(data_set_file, 'r') as json_file:
		data_sets = json.load(json_file)

	for title in data_sets.keys():

		data_set = data_sets[title]
		infiles = "filelists/"+title+".txt"

		## create filelist from DAS 
		txtfile = open(infiles, "w")
		txtfile.write("# created from {}\n".format(data_set))
		filelist = getFileListDAS(data_set)
		for entry in filelist:
		      txtfile.write(entry+"\n")
		txtfile.close()

		## submit job
		#jobflavour = 'espresso' #max 30min
		#jobflavour = 'microcentury' #max 1h
		#jobflavour = 'longlunch' #max 2h
		#jobflavour = 'workday' #max 8h
		jobflavour = 'tomorrow' #max 1d
		#jobflavour = 'testmatch' #max 3d
		submitJobs(title, infiles, outdir, jobflavour)
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
