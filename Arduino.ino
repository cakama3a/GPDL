// 3.0.8
int buttonPin; // Variable to store the pin number for the button

void setup() {
  Serial.begin(115200); // Initialize serial communication at 115200 baud rate
  while (!Serial) {
    ; // Wait for the serial port to be ready
  }
  
  pinMode(5, INPUT); // Disable pin 5, because it only serves as a connection contact
  pinMode(2, INPUT);
  pinMode(8, INPUT);

  // Wait for data from Python to set the buttonPin
  while (Serial.available() == 0) {
    ; // Do nothing
  }
  
  buttonPin = Serial.parseInt(); // Receive pin number from Python
  pinMode(buttonPin, OUTPUT); // Set buttonPin as an output
}

void loop() {
  if (Serial.available() > 0) {
    char data = Serial.read(); // Read incoming data from serial
    
    // Act based on the received character
    if (data == 'L') {
      pinMode(buttonPin, OUTPUT); // Enable pin
      digitalWrite(buttonPin, LOW); // Press the button
    } else if (data == 'H') {
      pinMode(buttonPin, INPUT); // Disable pin
      //digitalWrite(buttonPin, HIGH); // Release the button
    }
  }
}
