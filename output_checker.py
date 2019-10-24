#! /usr/bin/env python

from argparse import ArgumentParser
import sys

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-i', '--infile',   dest='infile', type=str, action='store', required=True,  help="Input file" )
    parser.add_argument('-e', '--err',     dest='err', action='store_true', default=False, help="set true if it is an .err file" )
    parser.add_argument('-o', '--out',     dest='out', action='store_true', default=False, help="set true if it is an .out file" )
    args = parser.parse_args()
   
    if args.err and args.out:
        print "can't select err and out"
        sys.exit()

    f = open(args.infile, 'r')
    lines = f.readlines()


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
            elif "working on file nr" in line:
                continue
            else:
                clean_file=False
                print line
        if clean_file: print "c l e a n"
    elif args.out:
        if not "--- endJob ---" in lines[-5]: 
            if lines == []:
                print "empty output"
            else:
                for line in lines[-10:]:
                    print line
        else:
            print "c l e a n"

    else: 
        print "no option selected"

    f.close() 
