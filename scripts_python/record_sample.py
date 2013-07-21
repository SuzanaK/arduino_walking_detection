#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""usage: record_sample.py [-h] [--version] [--duration DURATION]
                        [--filename FILENAME] [--verbose]

Record a sample of sensor values from an Arduino with a Piezo sensor. 

This script will connect to a serial port, read in values and save them with a
timestamp in a .csv file.

WARNING: The serial monitor of the Arduino IDE must be closed, otherwise the 
serial port will be temporarily unavailable, and some values will be lost!


optional arguments:
  -h, --help           show this help message and exit
  --version            show program's version number and exit
  --duration DURATION  duration of the sample record in seconds (default: 30)
  --filename FILENAME  name of the output file
  --verbose, -v        print each line while recording

Written for python 2.7.3 on a Linux system."""

import time
import os
import serial
import sys
import datetime
import argparse 
import matplotlib.pyplot as plt

def record_sample(DURATION, FILENAME, VERBOSITY):

    
    try:
        fh = open(FILENAME,'w')
    except OSError as e:
        print "OSError when opening file: %s" %e.strerror
        sys.exit(1)

   # try multiple port names because Linux has a problem here 
    PORTS = ['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2', '/dev/ttyACM3', '/dev/ttyACM4']

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
        print >> sys.stderr, "Could not connect to any of the serial ports!"
        sys.exit(1) 

    start_time = time.time()
    current_time = start_time
    #print start_time

    print "Ready to record samples for %s seconds!" %DURATION

    while True:

        try:        
            value = ser.readline().strip()
            if len(value) == 0: continue
            #print 'value: %s' %value
            value = value.replace(os.linesep, '')
            current_time = time.time() - start_time
            #print "%0.4f" %current_time
                
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

        # FILE OUTPUT (has to be outside the first try/catch block because otherwise 
        # a value without timestamp will be printed in case of Serial Exceptions
        try:
            current_time_str = "%0.4f" %(current_time % 1000)
            line = current_time_str + '\t' + value + '\n'
            if VERBOSITY:
                print line 
            fh.write(line)
        except IOError as e:
            print >> sys.stderr, "IOError with writing line: %s" %e.strerror
         
    
    try:
        fh.close()
    except IOError as e:
        print >> sys.stderr, "IOError when closing fle: %s" %e.strerror
    print "Recording finished and saved in file %s!" %FILENAME



if __name__ == '__main__':

    description = """

        Record a sample of sensor values from an Arduino with a Piezo sensor.\n\n
        This script will connect to a serial port, read in values and save them with a timestamp in a .csv file. 
        WARNING: The serial monitor of the Arduino IDE must be closed, otherwise the serial port will be temporarily unavailable, and 
        some values will be lost!"""

    epilog = 'Written for python 2.7.3 on a Linux system.\n\n'
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('--duration', help='duration of the sample record in seconds (default: 30)', type=int, default=30)
    parser.add_argument('--filename', help='name of the output file', default='piezo_sensor_sample.csv')
    parser.add_argument('--verbose', '-v', help='print each line while recording', action='store_true')


    args = parser.parse_args()
    DURATION = args.duration
    FILENAME = args.filename 
    VERBOSITY = args.verbose

    # add timestamp to default filename
    if FILENAME == 'piezo_sensor_sample.csv':
        timestamp = str(datetime.datetime.now())
        FILENAME = 'piezo_sensor_sample_' + str(DURATION) + '_seconds_' + timestamp + '.csv'
    record_sample(DURATION, FILENAME, VERBOSITY)
    

    

    
