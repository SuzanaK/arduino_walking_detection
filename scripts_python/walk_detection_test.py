#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import time
import os
import sys
import argparse

"""
Read in a sample of sensor values recorded from an Arduino with a Piezo
sensor. 

This script will read in values with their timestamps from a given
file and calculate the walking speed or the number of steps.

"""

def walk_detection(STEPS, THRESHOLD_STEP, THRESHOLD_NO_STEP, TIME_WINDOW, FILENAME, VERBOSITY): 

    try:
        fh = open(FILENAME,'r')
    except Error as e:
        print >> sys.stderr, "Error when opening file " + FILENAME + ": " + e.strerror
        
    lines = fh.readlines()
    #print len(lines)

    step_on = False 
    # number of steps in the last n seconds
    # list with timestamps of steps in the last TIME_WINDOW seconds 
    recent_steps = []
    speed_list = []
    start_time = 0
    current_time = 0
    last_timestamp = 0
    i = 0

    while i < len(lines):

            line = lines[i].strip()
            if len(line) == 0: continue
            content = line.split('\t')
            if len(content) != 2: 
                print >> sys.stderr, "Invalid data in line %d" %i
                continue 
            try:
                value = int(content[1])
                last_timestamp = current_time
                current_time = float(content[0])
                
            except ValueError:
                print >> sys.stderr, "No valid values!"
                print >> sys.stderr, "Value: %s" %content[1]
                print >> sys.stderr, "timestamp: %s" %content[0]
                i += 1
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
                if not STEPS and VERBOSITY:
                    print "walking at %d steps per minute"%speed

            if (not step_on) and value >= THRESHOLD_STEP:
                if STEPS:
                    print "%f Step!" %current_time 
                step_on = True 
                recent_steps.append(current_time) 
            
            if step_on and value <= THRESHOLD_NO_STEP:
                step_on = False 

            i += 1

    try:
        fh.close()
    except Error as e:
        print >> sys.stderr, "Error when closing file " + FILENAME + ": " + e.strerror
    
    if not STEPS:
        print "\nMeasured speeds:"
        for speed in speed_list: 
            print speed
        print "Average speed: %d" %(sum(speed_list) / len(speed_list))

if __name__ == '__main__':

    description = """

        Read in a sample of sensor values recorded from an Arduino with a Piezo sensor.\n\n
        This script will read in values with their timestamps from a given file and calculate the walking speed or the number of steps."""

    epilog = 'Written for python 2.7.3 on a Linux system.\n\n'
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('--onlysteps', help='only count the number of steps, do not print the speed', action='store_true')
    parser.add_argument('--step', help='threshold value to start a new step (default: 500', type=int, default=500)
    parser.add_argument('--nostep', help='threshold value to stop a started step (default:200)', type=int, default=200)
    parser.add_argument('--timewindow', help='time window in seconds to calculate the speed (default: 3)', type=int, default=3)
    parser.add_argument('--filename', help='name of the input file')
    parser.add_argument('--verbose', '-v', help='print each line while recording', action='store_true')
    
    args = parser.parse_args()
    #print args
    STEPS = args.onlysteps 
    THRESHOLD_STEP = args.step
    THRESHOLD_NO_STEP = args.nostep 
    TIME_WINDOW = args.timewindow
    FILENAME = args.filename 
    VERBOSITY = args.verbose

    walk_detection(STEPS, THRESHOLD_STEP, THRESHOLD_NO_STEP, TIME_WINDOW, FILENAME, VERBOSITY)
    

