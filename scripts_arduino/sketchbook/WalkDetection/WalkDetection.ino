/*
  AnalogReadSerial
  Reads an analog input on pin 1, prints the result if it is higher than 0.
 */

// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
}


// the loop routine runs over and over again forever:
void loop() {
  // read the input on analog pin 1:
  int sensorValue = analogRead(1);
  
  // sensorValue is between 0 and 1023 (analog to digital conversion (ADC))
if(sensorValue > 0) {
  Serial.println(sensorValue);
}
  delay(1);        // delay in between reads for stability in miliseconds
}
