import RPi.GPIO as GPIO
import time
import subprocess


def flash_LED(s):
    GPIO.output(18,GPIO.HIGH)
    time.sleep(s)
    GPIO.output(18,GPIO.LOW)
    
    
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)

flash_LED(1)
time.sleep(1)

def check_and_turn_on_BT(MAC_address):
    isignal = 0
    while(isignal != 1):
    #connect mic
        subprocess.call('/home/pi/snoring/autodis', shell=True)
        time.sleep(3)
        subprocess.call('sudo killall bluealsa', shell=True)
        subprocess.call('pulseaudio --start', shell=True)
        time.sleep(1)
        subprocess.call('/home/pi/snoring/autopair', shell=True)
        time.sleep(3)
        string = "set-card-profile bluez_card." + MAC_address
        check = subprocess.check_output(["pacmd", string, "headset_head_unit"])
        if(check != b''):
            flash_LED(1)
        else:
            isignal += 1
            string = "pacmd set-card-profile bluez_card." + MAC_address + " headset_head_unit"
            subprocess.call(string, shell=True)
            string = "pacmd set-default-sink bluez_sink." + MAC_address + ".headset_head_unit"
            subprocess.call(string, shell=True)
            string = "pacmd set-default-source bluez_source." + MAC_address + ".headset_head_unit"
            subprocess.call(string, shell=True)
            for i in range(5):
                flash_LED(0.2)
                time.sleep(0.2)
check_and_turn_on_BT("34_81_F4_38_F6_48")