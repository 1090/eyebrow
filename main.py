#!/usr/bin/python

import datetime
import humod
import time
import RPi.GPIO as GPIO

SLEEP_TICK = 1
DESTINATION_NUMBER = '+7xxxxxxxxxx'

def main():
    GPIO.setmode(GPIO.BOARD)

    # Configuring GPIO4 (pin 7) as INPUT
    GPIO.setup(7, GPIO.IN)

    print "Initialising modem..."
    rf = humod.Modem()
    #print "Found %s"%(rf.show_model())
    #rf.enable_textmode(True)
    print rf.sms_send(DESTINATION_NUMBER, 'hello world')

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


