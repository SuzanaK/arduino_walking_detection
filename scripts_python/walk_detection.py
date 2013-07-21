#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import time
import os
import sys
import serial
import argparse
 
"""
Read sensor values from an Arduino with a Piezo sensor. This script will read
in values from a serial connection with the Arduino and calculate the walking
speed or the number of steps.

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --onlysteps           only count the number of steps, do not print the speed
  --step STEP           threshold value to start a new step (default: 500
  --nostep NOSTEP       threshold value to stop a started step (default:200)
  --timewindow TIMEWINDOW
                        time window in seconds to calculate the speed
                        (default: 3)
  --duration DURATION   duration of the sample record in seconds (default: 30)
  --verbose, -v         verbose output

"""



def walk_detection(STEPS, THRESHOLD_STEP, THRESHOLD_NO_STEP, TIME_WINDOW, DURATION, VERBOSITY): 

    # try multiple port names because Linux has a problem here 
    PORTS = ['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2', '/dev/ttyACM3', '/dev/ttyACM4']
    ser = None

    for port in PORTS:

        try:
            ser = serial.Serial(port, baudrate=9600, timeout=3) 
        except serial.SerialException as e:
            print >> sys.stderr, "Could not connect to the serial port: %s. Will try the next port." %e.strerror
            continue
           
        if ser:
            print 'Serial Connection opened on port %s' %ser.name
            break

    # give time to open serial port              
    time.sleep(1.5)

    if not ser:
        print >> sys.stderr, "Could not connect to any of the serial ports! Will exit now."
        sys.exit(1) 

    step_on = False 
    # list with timestamps of steps in the last TIME_WINDOW seconds 
    recent_steps = []
    start_time = time.time()
    current_time = start_time
    if VERBOSITY:   
        print "Start Time: %d" %start_time
    last_timestamp = 0
    recent_steps = []
    speed_list = []
    
    while True:

        try:        
            value = ser.readline().strip()
            if len(value) == 0: continue
            value = value.replace(os.linesep, '')
            last_timestamp = current_time
            current_time = time.time() - start_time
            current_time_str = "%0.4f" %(current_time % 1000)
            current_time = float(current_time_str)
            if VERBOSITY:
                print current_time_str 
            if current_time > DURATION:
                break

        except serial.SerialException as e:
            print >> sys.stderr, ("Serial Exception: %s" %e.strerror)
            current_time = time.time() - start_time
            if current_time > DURATION:
                break
            else:
                continue

        except serial.SerialTimeoutException as e:
            print >> sys.stderr, ("SerialTimeoutException: %s" %e.strerror)
            current_time = time.time() - start_time
            if current_time > DURATION:
                break
            else:
                continue

        except OSError as e:
            print >> sys.stderr, ("OSError: %s" %e.strerror)
            current_time = time.time() - start_time
            if current_time > DURATION:
                break
            else:
                continue

        # every second, remove old entries from recent_steps and recalculate speed (in steps per minute) 
        if (int(current_time) - int(last_timestamp)) >= 1:
            recent_steps = [step for step in recent_steps if (current_time - step < TIME_WINDOW)]
            #check if there were any steps in the last 1.5 seconds and if not, declare the person to be stopped 
            if len([step for step in recent_steps if (current_time - step < 1.5)]) == 0: 
                print "%f Person stopped!" %current_time
            speed = len(recent_steps) * (60 / TIME_WINDOW) 
            speed_list.append(speed)
            #print recent_steps
            if (not STEPS) and VERBOSITY:
                print "walking at %d steps per minute" %speed

        if (not step_on) and value >= THRESHOLD_STEP:
            if STEPS:
                print "%f Step!" %current_time 
            step_on = True 
            recent_steps.append(current_time) 
            
        if step_on and value <= THRESHOLD_NO_STEP:
            step_on = False   
    
    print "Walk Detection finished!"

    if not STEPS:
        print "\nMeasured speeds:"
        for speed in speed_list: 
            print speed
        print "Average speed: %d" %(sum(speed_list) / len(speed_list))


if __name__ == '__main__':

    description = """

        Read sensor values from an Arduino with a Piezo sensor.\n\n
        This script will read in values from a serial connection with the Arduino and calculate the walking speed or the number of steps."""

    epilog = 'Written for python 2.7.3 on a Linux system.\n\n'
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('--onlysteps', help='only count the number of steps, do not print the speed', action='store_true')
    parser.add_argument('--step', help='threshold value to start a new step (default: 500', type=int, default=500)
    parser.add_argument('--nostep', help='threshold value to stop a started step (default:200)', type=int, default=200)
    parser.add_argument('--timewindow', help='time window in seconds to calculate the speed (default: 3)', type=int, default=3)
    parser.add_argument('--duration', help='duration of the sample record in seconds (default: 30)', type=int, default=30)
    parser.add_argument('--verbose', '-v', help='verbose output', action='store_true')
    
    args = parser.parse_args()
    #print args
    STEPS = args.onlysteps 
    THRESHOLD_STEP = args.step
    THRESHOLD_NO_STEP = args.nostep 
    TIME_WINDOW = args.timewindow
    VERBOSITY = args.verbose
    DURATION = args.duration

    walk_detection(STEPS, THRESHOLD_STEP, THRESHOLD_NO_STEP, TIME_WINDOW, DURATION, VERBOSITY)
    

