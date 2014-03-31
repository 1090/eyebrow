#!/usr/bin/python

import datetime
import serial
import time
import sys
import RPi.GPIO as GPIO

CONFIG_FILE = '/home/pi/eyebrow/default.conf'

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

    state = STATE_NORMAL
    sleep_interval = NORMAL_MODE_INTERVAL
    state_counter = 0
    state_counter_neg = 0
    print "Entered mode STATE_NORMAL"
    while True:
        status = GPIO.input(7)
        state_counter = state_counter + int(status)
        state_counter_neg = state_counter_neg + 1 - int(status)
        if state == STATE_NORMAL and state_counter >= NORMAL_MODE_TOSUSPICIOUS_THRESHOLD:
            ts_suspicious = datetime.datetime.now()
            state = STATE_SUSPICIOUS
            sleep_interval = SUSPICIOUS_MODE_INTERVAL
            state_counter = 0
            state_counter_neg = 0
            print "[SUSPICIOUS] @ %s"%ts_suspicious
        if state == STATE_SUSPICIOUS and state_counter >= SUSPICIOUS_MODE_TOALERT_THRESHOLD:
            ts_alert = datetime.datetime.now()
            state = STATE_ALERT
            sleep_interval = ALERT_MODE_INTERVAL
            state_counter = 0
            state_counter_neg = 0
            print "[ALERT] @ %s"%ts_alert
        if state == STATE_SUSPICIOUS and state_counter_neg >= SUSPICIOUS_MODE_TONORMAL_THRESHOLD:
            suspicious_duration = datetime.datetime.now() - ts_suspicious
            print "[NORMAL] reverted back from SUSPICIOUS after %s s"%suspicious_duration
            state = STATE_NORMAL
            sleep_interval = NORMAL_MODE_INTERVAL
            state_counter = 0
            state_counter_neg = 0
        if state == STATE_ALERT and state_counter_neg >= ALERT_MODE_TONORMAL_THRESHOLD:
            alert_duration = datetime.datetime.now() - ts_alert
            print "[NORMAL] reverted back from ALTER after %s s"%alert_duration
            state = STATE_NORMAL
            sleep_interval = NORMAL_MODE_INTERVAL
            state_counter = 0
            state_counter_neg = 0
        time.sleep(sleep_interval)

if __name__ == '__main__':

    # Parsing ARGV
    for a in sys.argv:
        r = a.split('=')
        if len(r) == 2:
            if r[0] == '--config':
                CONFIG_FILE = r[1]

    # Applying config
    try:
        execfile(CONFIG_FILE)
    except Exception, e:
        print e
        sys.exit()

    main()


