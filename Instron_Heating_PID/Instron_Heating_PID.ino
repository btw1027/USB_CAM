//https://www.bc-robotics.com/tutorials/using-a-tmp36-temperature-sensor-with-arduino/
//https://www.electronoobs.com/eng_arduino_tut24_2.php
//https://www.oddwires.com/using-a-mosfet-to-control-a-dc-motor/

int sensorPin = A0;  //This is the Arduino Pin that will read the sensor output
int mosfetPin = 7;
int sensorInput;    //The variable we will use to store the sensor input  
double read_temp;        //The variable we will use to store temperature in degrees.
double set_temperature = 27;
double PID_error = 0;
double previous_error = 0;
unsigned long duration = 10000; // in millis = 0.1 Hz
unsigned long elapsedTime, currentTime, previousTime;
double PID_value = 0;

//PID constants
double kp = 100;   double ki = 1;   double kd = 1000.0;
double PID_p = 0;    double PID_i = 0;    double PID_d = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600); //Start the Serial Port at 9600 baud (default)
  //set digital pin 7 to output to control MOSFET
  pinMode(mosfetPin, OUTPUT);
  digitalWrite(mosfetPin, LOW);
  previousTime = millis();
}

void loop() {


  unsigned long currentTime = millis(); 
  if (currentTime - previousTime >= duration)
  { 

    double read_temp = read_temp_sensor();
    //Next we calculate the error between the setpoint and the real value
    double PID_error = set_temperature - read_temp;
    //Calculate the P value
    PID_p = kp * PID_error;
    //Calculate the I value in a range on +-3
    if (-3 < PID_error < 3)
    {
      PID_i = PID_i + (ki * PID_error);
    }
    
    elapsedTime = (currentTime - previousTime) / 1000;
    previousTime = currentTime;
    currentTime = millis();
    //Now we can calculate the D value
    PID_d = kd * ((PID_error - previous_error) / elapsedTime);
    //Final total PID value is the sum of P + I + D
    PID_value = PID_p + PID_i + PID_d;
    
    previous_error = PID_error;     //Remember to store the previous error for next loop.
//
//    Serial.print("PID P: ");
//    Serial.println(PID_p);
//    Serial.print("PID I: ");
//    Serial.println(PID_i);
//    Serial.print("PID D: ");
//    Serial.println(PID_d);
//    Serial.print("PID VALUE: ");
//    Serial.println(PID_value);
    
    double delay_time = duration * PID_value / 100;
    
      //We define PWM range between 0 and 100
    if(delay_time < 0)
    {    delay_time = 0;    }
    if(delay_time > duration)  
    {    delay_time = duration;  }
    
//    Serial.print("delay: ");
//    Serial.println(delay_time);
    digitalWrite(mosfetPin, HIGH);
    delay(delay_time);
    digitalWrite(mosfetPin, LOW);
    
    
    


    
    
  }
}
  

double read_temp_sensor() {
  sensorInput = analogRead(A0);    //read the analog sensor and store it
  read_temp = (double)sensorInput / 1024;       //find percentage of input reading
  read_temp = read_temp * 5;                 //multiply by 5V to get voltage
  read_temp = read_temp - 0.5;               //Subtract the offset
  read_temp = read_temp * 100;               //Convert to degrees Celsius

//  Serial.print("Current Temperature: ");
  Serial.println(read_temp);
  return read_temp;
}
