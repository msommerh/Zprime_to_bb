#! /bin/bash

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

Errors=0
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

#p="submission_files/"
p="/afs/cern.ch/work/m/msommerh/public/Zprime_to_bb_Analysis/submission_files/"
dirs=$(ls -d  "${p}tmp_${sample}_"*)

for dir in $dirs; do

    echo "checking sample: ${dir}"

    let n=${#dir}
    errs=$(ls ${dir}"/"*".err")
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
    
    err_check=$(./output_checker.py -i $high_err -e)
    if [[ $(join $err_check) != $(join c l e a n) ]]; then  #not proud of this, but it works
        echo "An unknown error has been detected in ${high_err}:"
        echo $err_check
        let Errors=$Errors+1
    fi
    
    high_out=$(err_to_out $high_err)
    out_check=$(./output_checker.py -i $high_out -o)
     if [[ $(join $out_check) != $(join c l e a n) ]]; then  #stil not proud of this, but it works
        echo "Unexpected behavior has been detected in ${high_out}:"
        echo $out_check
        let Errors=$Errors+1
    fi
   
    echo
done

if [[ $Errors -ne 0 ]]; then
    echo "There were ${Errors} issues found in the latest submission of ${sample}!"
else
    echo "The last submission of ${sample} returned no errors!"
fi

