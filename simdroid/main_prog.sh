#!/bin/bash

fldr=$1
 for entry in "$fldr"/*
do
    if [ -d "${entry}" ] 
    then
	bash sample.sh "${entry}"
    fi
done
