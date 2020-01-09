#! /usr/bin/env python

###
### Macro for submitting ntuple production to HTCondor.
###

import global_paths
import sys
import os, re, glob
from commands import getoutput
from fnmatch import fnmatch
import itertools
from argparse import ArgumentParser
import json
from math import ceil
#import checkFiles
#from checkFiles import getSampleShortName, matchSampleToPattern, header, ensureDirectory

if __name__ == "__main__":
  parser = ArgumentParser()
  parser.add_argument('-q', '--queue',   dest='queue', choices=['espresso', 'microcentury', 'longlunch', 'workday', 'tomorrow', 'testmatch', 'nextweek'], type=str, default='tomorrow', action='store',
                                         help="select queue for submission" )
  parser.add_argument('-v', '--verbose', dest='verbose', default=False, action='store_true',
                                         help="set verbose" )
  parser.add_argument('-y', '--year',    dest='year', type=str, default='2016', action='store',
                                         help="set year." )
  parser.add_argument('-MC', '--isMC',   dest='isMC',  action='store_true', default=False,
                                         help="Select this if the sample is MC, otherwise it is flagged as data.")
  parser.add_argument('-MT', '--mcType',   dest='mcType', type=str, action='store', default="QCD", choices=['QCD', 'TTbar', 'signal'],                                        help="Select the type of MC. Either signal, QCD or TTbar." )
  parser.add_argument('-rs', '--resubmit',   dest='resubmit', type=str, action='store', default="",
                                         help="Indicate file containing titles of the sample for resubmission." )
  parser.add_argument('-rf', '--resubmit_file',   dest='resubmit_file', type=int, action='store', default=-1,
                                         help="Indicate output file number for single resubmission." )
  parser.add_argument('-n', '--nFiles',  dest='nFiles',   action='store', type=int, default=10,
                                         help="Number of input files per output nTuple.")
  parser.add_argument('-s', '--single',   dest='single', type=str, action='store', default="",
                                         help="Single dataset to be submitted instead of the standard datasets." )
  parser.add_argument('-c', '--cores',  dest='cores',   action='store', type=int, default=1,
                                         help="Number of cpu cores. A number >1 will enable multiprocessing.")
  parser.add_argument('-mn', '--multinode',   dest='multinode',  action='store_true', default=False,
                                         help="Select this to parallelize the submission via multiple condor nodes.")
  parser.add_argument('-Tr', '--trigger',   dest='trigger',  action='store_true', default=False,
                                         help="Select this to run on the SingleMuon sample for a trigger study.")
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

if args.multinode and args.resubmit_file!=-1:
    print "Cannot use multinode mode with distinct file submission! Aborting..."
    sys.exit()

if args.trigger and args.isMC:
    print "Cannot run trigger study on MC! Aborting..."
    sys.exit()

def getFileListDAS(dataset):
        """Get list of files from DAS."""
        dataset  = dataset.replace('__','/')
        instance = 'prod/global'
        if 'USER' in dataset:
            instance = 'prod/phys03'
        cmd = 'dasgoclient -query="file dataset={} instance={}"'.format(dataset, instance)
        #print "Executing ",cmd
        cmd_out  = getoutput( cmd )
        #print "output: ",cmd_out
        tmpList  = cmd_out.split(os.linesep)
        filelist = [ ]
        for line in tmpList:
          if '.root' in line:
            #filelist.append("root://xrootd-cms.infn.it/"+line)
            filelist.append("root://cms-xrd-global.cern.ch/"+line)
        return filelist


def submitJobs(title, infiles, outdir, jobflavour):
    path = global_paths.MAINDIR
    if not os.path.exists(outdir+title):
        os.makedirs(outdir+title)
        print "Directory "+outdir+title+" created."
    else:
        print "Directory "+outdir+title+" already exists."
    workdir = global_paths.SUBMISSIONLOGS+"tmp_"+title
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
        fout.write("source "+global_paths.MAINDIR+"setupEnv.sh\n")

        fout.write("export X509_USER_PROXY="+global_paths.GRIDCERTIFICATE+"\n")
        fout.write("use_x509userproxy=true\n")

        fout.write("########## input arguments ##########\n")
        fout.write("file_nr=$1\n")
        fout.write("#####################################\n")

        fout.write("./postprocessors/Zprime_to_bb.py -t {} -i {} -o {} -y {}{} -n {} -r {}{}{}\n".format(title, infiles, outdir+title, args.year, ' -MC' if args.isMC else '', args.nFiles, '$file_nr' if args.multinode else args.resubmit_file, " -mp" if args.cores>1 else "", " -Tr" if args.trigger else ""))
        fout.write("echo 'STOP---------------'\n")
        fout.write("echo\n")
        fout.write("echo\n")

    #submit job
    os.system("chmod 755 job.sh")
    if args.resubmit_file==-1:
        os.system("mv job.sh "+title+".sh")
        makeSubmitFileCondor(title+".sh", title, jobflavour, path+"/"+infiles)
    else:
        os.system("mv job.sh "+title+"_"+str(args.resubmit_file)+".sh")
        makeSubmitFileCondor(title+"_"+str(args.resubmit_file)+".sh", title, jobflavour, path+"/"+infiles)
    os.system("condor_submit submit.sub")
    print "job submitted"
    os.chdir(path)

def makeSubmitFileCondor(exe, jobname, jobflavour, infiles):
    print "make options file for condor job submission"
    submitfile = open("submit.sub", "w")
    submitfile.write("executable            = "+exe+"\n")
    submitfile.write("arguments             = $(ProcId)\n")
    submitfile.write("output                = "+jobname+".$(ClusterId).$(ProcId).out\n")
    submitfile.write("error                 = "+jobname+".$(ClusterId).$(ProcId).err\n")
    submitfile.write("log                   = "+jobname+".$(ClusterId).log\n")
    submitfile.write('+JobFlavour           = "'+jobflavour+'"\n')
    if args.cores>1: submitfile.write('RequestCpus           = {}\n'.format(args.cores))
    if args.multinode and args.resubmit_file==-1:
        file_list = []
        file_content = open(infiles, 'r').readlines()
        for entry in file_content:
            if not entry.startswith("#"):
                filepath = entry.replace('\n','')
                #filepath = filepath.replace('cms-xrd-global.cern.ch', 'xrootd-cms.infn.it')
                file_list.append(filepath)
        nJobs = int(ceil(float(len(file_list))/args.nFiles))
        submitfile.write("queue {}".format(nJobs))
    else:
        submitfile.write("queue") 
    submitfile.close()

def main():

        outdir = global_paths.PRODUCTIONDIR
        
        #infiles = "filelists/default.txt"
        #title = "test_QCD"
        #submitJobs(title+"_1", infiles, outdir, "longlunch")
        #submitJobs(title+"_2", infiles.replace(".txt","2.txt"), outdir, "longlunch")
        #submitJobs(title+"_3", infiles.replace(".txt","3.txt"), outdir, "longlunch")
        #sys.exit()
       
        if args.cores>1:
            print "Enabling multiprocessing and requesting {} cpu cores.".format(args.cores)
 
        if args.resubmit_file != -1: print "only submitting output file nr", args.resubmit_file

        if args.single!="":
            data_set = args.single
            infiles = "filelists/single.txt"

            ## create filelist from DAS 
            txtfile = open(infiles, "w")
            txtfile.write("# created from {}\n".format(data_set))
            filelist = getFileListDAS(data_set)
            for entry in filelist:
                  txtfile.write(entry+"\n")
            txtfile.close()

            ## submit job
            submitJobs("single_8core", infiles, outdir, args.queue)


        else:

            ## load data sets from file
            if args.isMC:
                    data_type="MC_"+args.mcType
            else:
                    if args.trigger:
                        data_type="SingleMuon"
                    else:
                        data_type="data"
    
            if args.year in ['2016','2017','2018']:
                    data_set_file = 'samples/samples_{}_{}.json'.format(data_type, args.year)
            else:
                    print "Unknown year. Abort submission!!"
                    sys.exit()
    
            with open(data_set_file, 'r') as json_file:
                    data_sets = json.load(json_file)
    
            if args.resubmit != "":
                    rs_titles = open(args.resubmit, 'r').readlines()
                    for n, entry in enumerate(rs_titles):
                            rs_titles[n] = entry.replace("\n", "")
                    print "resubmitting the following samples:", rs_titles
    
            for title in data_sets.keys():
    
                    if args.resubmit != "":
                            if title not in rs_titles: continue 
    
                    data_set = data_sets[title]
                    infiles = "filelists/"+title+".txt"
    
                    ## create filelist from DAS
                    if not os.path.exists("filelists"):
                        os.makedirs("filelists")                    
                    txtfile = open(infiles, "w")
                    txtfile.write("# created from {}\n".format(data_set))
                    filelist = getFileListDAS(data_set)
                    for entry in filelist:
                          txtfile.write(entry+"\n")
                    txtfile.close()
    
                    ## submit job
                    submitJobs(title, infiles, outdir, args.queue) 
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
