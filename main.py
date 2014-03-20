#!/usr/bin/python

import datetime
import serial
import time
import RPi.GPIO as GPIO

SLEEP_TICK = 1
MODEM_PORT = '/dev/ttyUSB0'
DESTINATION_NUMBER = '+7xxxxxxxxxx'

EOM_MARKERS = ['OK', 'ERROR']

def str_send (port, data):
    print "<<" + data
    port.write(data)

    response = ''
    while True:
        while port.inWaiting() > 0:
            response = response + port.read(1)
            for eo in EOM_MARKERS:
                if response[-len(eo):] == eo:
                    print ">>%s"%response
                    return True
        time.sleep(1)
    return False

def main():
    GPIO.setmode(GPIO.BOARD)

    # Configuring GPIO4 (pin 7) as INPUT
    GPIO.setup(7, GPIO.IN)

    print "Initialising serial..."
    stty = serial.Serial(MODEM_PORT, 115200, timeout=1)
    stty.open()

    str_send(stty, 'ATI\r')
    
    #str_send(stty, 'AT+CMGF=1\r')
    #str_send(stty, 'AT+CMGS="%s",\r'%DESTINATION_NUMBER)
    msg = 'hello world'
    msg = msg + '\x1A'
    #str_send(stty, msg)

    stty.close()

    print "Watching"
    alert_state = False
    while True:
        status = GPIO.input(7)
        if status and not alert_state:
            ts = datetime.datetime.now()
            print "[ALERT] @ %s"%ts
            alert_state = True
        if alert_state and not status:
            alert_duration = datetime.datetime.now() - ts
            print "[NORMAL] alert was %s"%alert_duration
            alert_state = False
        time.sleep(SLEEP_TICK)

if __name__ == '__main__':
    main()


