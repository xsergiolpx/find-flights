#!/bin/bash

for dep in BKK HDY SGN KUL DAD MDL RGN URT
do	
	for dest in BKK HDY SGN KUL DAD MDL RGN URT
	do
		if [ $dep != $dest ]
		then
			python desktop-version.py -d 07 -r 00 -a $dep -b $dest -e es,co.uk &
			sleep 10
		fi
	done
done
