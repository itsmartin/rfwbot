#!/bin/bash
while true; do
	python3 rfwbot.py
	echo Crashed, restarting
	sleep 1
done
