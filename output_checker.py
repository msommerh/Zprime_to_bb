#! /usr/bin/env python

###
### Auxiliary file used by check_submission.sh to scan stderr and stdout files from HTCondor submissions for errors/anomalies.
###

from argparse import ArgumentParser
import sys

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-i', '--infile',   dest='infile', type=str, action='store', required=True,  help="Input file" )
    parser.add_argument('-e', '--err',     dest='err', action='store_true', default=False, help="set true if it is an .err file" )
    parser.add_argument('-o', '--out',     dest='out', action='store_true', default=False, help="set true if it is an .out file" )
    parser.add_argument('-n', '--filenumber',     dest='filenumber', action='store_true', default=False, help="Set true and plug in submit.sub file if you want to count the file number of a sample" )
    parser.add_argument('-l', '--log',     dest='log', action='store_true', default=False, help="set true if it is a .log file" )
    args = parser.parse_args()

    f = open(args.infile, 'r')
    lines = f.readlines()

    if args.err or args.out:   

        if args.err and args.out:
            print "can't select err and out"
            sys.exit()
    
        if args.err:
            clean_file = True
            for line in lines:
                if "TTree::SetBranchStatus:0: RuntimeWarning: No branch name is matching wildcard -> *GenPart*" in line:
                    continue
                elif "TTree::SetBranchStatus:0: RuntimeWarning: No branch name is matching wildcard -> *Dressed*" in line:
                    continue
                elif "TTree::SetBranchStatus:0: RuntimeWarning: No branch name is matching wildcard -> HTXS*" in line:
                    continue
                elif "TTree::SetBranchStatus:0: RuntimeWarning: No branch name is matching wildcard -> *GenJet*" in line:
                    continue
                elif "No branch name is matching wildcard -> HLT_DoublePFJets*" in line:
                    continue
                elif "working on file nr" in line:
                    continue
                else:
                    clean_file=False
                    print line
            if clean_file: print "c l e a n"
        elif args.out:
            if not ("--- endJob ---" in lines[-5] or ("--- endJob ---" in lines[-7] and "removing temporary files.." in lines[-4])): 
                if lines == []:
                    print "empty output"
                else:
                    for line in lines[-10:]:
                        print line
            else:
                print "c l e a n"

    elif args.filenumber:
        number_string = lines[6].replace("queue ","").replace("queue","")
        if "+JobFlavour" in number_string: number_string = lines[7].replace("queue ","").replace("queue","")
        if number_string=='':
            print 1
        else:
            print number_string

    elif args.log:
        clean_file = True
        for line in lines:
            if "Job removed" in line: 
                clean_file = False
                print line
        if clean_file: print "c l e a n"
    else: 
        print "no option selected"

    f.close() 
