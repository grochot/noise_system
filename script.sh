#!/bin/bash
sudo chmod 777 /dev/ttyUSB0 
sudo chmod 777 /dev/ttyUSB1 
cd /home/pw/git/noise_system/
#git stash 
#git pull 
python3 noise_measurement_system.py

