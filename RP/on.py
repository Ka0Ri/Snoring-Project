#!/usr/bin/python
#
# Monitor removal of bluetooth reciever
import os
import sys
import subprocess
import time

subprocess.call('sudo killall bluealsa', shell=True)
time.sleep(3)
subprocess.call('pulseaudio --start', shell=True)
time.sleep(2)
status = subprocess.call('ls /dev/input/event0 2>/dev/null', shell=True)  
while (True):
    print("Bluetooth On")
    subprocess.call('~/scripts/autopair', shell=True)
    subprocess.call('pacmd set-card-profile bluez_card.B8_F8_BE_69_F2_34 headset_head_unit', shell=True)
    subprocess.call('pacmd set-default-sink bluez_sink.B8_F8_BE_69_F2_34.headset_head_unit', shell=True)
    subprocess.call('pacmd set-default-source bluez_source.B8_F8_BE_69_F2_34.headset_head_unit', shell=True)
    time.sleep(5)
