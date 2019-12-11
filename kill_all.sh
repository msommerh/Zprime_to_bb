#!/bin/bash

process_list=$(ps | grep -e python | awk '{print $1}')
#echo $process_list

for process in $process_list; do
    kill $process
done
