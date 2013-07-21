arduino_walking_detection
=========================

Detect steps with a piezo sensor connected to an Arduino 


Arduino: Arduino Mega 2560  
Sensor: Piezo Element 1,3kHz 48nF (PLS 3112)
Additional Element: 1 Mega Ohm Resistor 

Arduino IDE: 1.0.4
Python 2.7.3

How to plot the results from the sample file:  

    import matplotlib.pyplot as plt
    plt.plotfile('piezo_sensor_sample_30_sec.csv', delimiter='\t', cols=(0, 1))
    plt.show()



