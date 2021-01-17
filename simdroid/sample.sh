#!/bin/bash

targdir=$1
apk1=""

for entry in "$targdir"/*
do
	if [ "${entry##*.}" == "apk" ]
	then
	    echo "Halo"
	    #echo "${entry}"
	    apk1="${entry}"
	    echo $apk1
	    	
	fi	
done



for entry in "$targdir"/*
do
    echo "${entry}"
    if [ -d "${entry}" ] 
    then
	#echo $entry
	for i in "${entry}"/*
	do
	    if [ "${i##*.}" == "apk" ]
	    then	
	        echo "sub"
	    	echo "${i}"
		apk2="${i}"
		if [ ! -z "${apk1// }" ]
		then
		    #echo "have"
		    #/usr/local/lib/python2.7.9/bin/python androsim.py -i "${apk1}" "${apk2}" > /home/jellybean/sim_analysis/Analysis/result.txt
		    #sync; sudo echo 3 > /proc/sys/vm/drop_caches			    
		    /usr/local/lib/python2.7.9/bin/python androsim.py -i "${apk2}" "${apk1}" > ../Result1.txt
		    #sync; sudo echo 3 > /proc/sys/vm/drop_caches	
		    echo "done"
		fi
	    fi
	done    
    
	    	
    fi	
done
#echo $1
