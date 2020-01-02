#! /bin/bash

###
### Macro to check the stderr and stderr files of the ntuple submission on HTCondor to see if errors have occurred.
###

Errors=0

function clusternumber {
    n_size=7
    end_size=6
    let sum=$n_size+$end_size
    let start=${#1}-$sum
    echo ${1:$start:$n_size}
    }

function join {
    local IFS="$1"
    shift
    echo "$*"
    }

function err_to_out {
    let n=${#1}-3
    echo "${1:0:$n}out"
    }

function remove_procId {
    let n=${#1}-5
    echo "${1:0:$n}"
    }

function err_checker {
    err_check=$(./output_checker.py -i $1 -e)
    if [[ $(join $err_check) != $(join c l e a n) ]]; then  #not proud of this, but it works
        echo "An unknown error has been detected in ${1}:"
        echo $err_check
        let Errors=$Errors+1
    fi
    }

function out_checker {
    high_out=$(err_to_out $1)
    out_check=$(./output_checker.py -i $high_out -o)
     if [[ $(join $out_check) != $(join c l e a n) ]]; then  #stil not proud of this, but it works
        echo "Unexpected behavior has been detected in ${high_out}:"
        echo $out_check
        let Errors=$Errors+1
    fi
    }

function log_checker {
    log_file=$1
    log_check=$(./output_checker.py -i $log_file -l)
     if [[ $(join $log_check) != $(join c l e a n) ]]; then  #stil not proud of this, but it works
        echo "Unexpected behavior has been detected in ${log_file}:"
        echo $log_check
        let Errors=$Errors+1
    fi
    }


echo "checking status of submitted files"
read -p "year: " year
read -p "isMC [y/n]: " isMC
if [ $isMC = "y" ]; then
    read -p "isBkg [y/n]: " isBkg
    if [ $isBkg = "y" ]; then
        read -p "isQCD [y/n]: " isQCD
        if [ $isQCD = "y" ]; then     
            sample="MC_QCD_${year}"
        else
            sample="MC_TTbar_${year}"
        fi
    else
        sample="MC_signal_${year}"
    fi
else
    sample="data_${year}"
fi
echo "sample = ${sample}"

p=$(./global_paths.py -g SUBMISSIONLOGS) ## get location of submission logs via global_paths.py

dirs=$(ls -d  "${p}tmp_${sample}_"*)

for dir in $dirs; do

    echo "checking sample: ${dir}"

    let n=${#dir}
    #errs=$(ls ${dir}"/"*".err")
    errs=$(ls ${dir}"/"*".0.err")
    max=-1
    high_err=""

    for err in $errs; do
        num=$(clusternumber $err)
        [[ $num -gt $max ]] && max=$num
        if [[ $max -eq $num ]]; then
            high_err=$err
        fi
    done

    if [ $max -eq -1 ]; then
        echo "no maximal cluster number could be deduced!"
        exit 1
    fi
   
    err_files=$(ls $(remove_procId ${high_err})*.err)

    n_errs=0
    for errf in $err_files; do
        err_checker $errf  ## check stderr
        out_checker $errf  ## check stdout
        let n_errs=$n_errs+1
    done  

    logf=$(remove_procId ${high_err})log
    log_checker $logf      ## check log
   
    n_files=$(./output_checker.py -i ${dir}/submit.sub -n)

    if [ $n_errs -ne $n_files ]; then
        echo
        echo "----------------------------------------------------------------------"
        echo "WARNING!! The number of foreseen output files (${n_files}) is different that the number of stderr/stdout files (${n_errs}) !!"
        echo "----------------------------------------------------------------------"
        echo
    fi

    echo
done

if [[ $Errors -ne 0 ]]; then
    echo "There were ${Errors} issues found in the latest submission of ${sample}!"
else
    echo "The last submission of ${sample} returned no errors!"
fi

