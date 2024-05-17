// Налаштовуємо з'єднання
int buttonPin = 2; // Провід, що йде до кнопки на геймпаді

void setup() {
  pinMode(buttonPin, OUTPUT);
  Serial.begin(115200); // 115200/9600
}

void loop() {
  char data = Serial.read();
  
  if (data == 'L') {
    digitalWrite(buttonPin, LOW); // Натиснути кнопку
  }
  
  if (data == 'H') {
    digitalWrite(buttonPin, HIGH); // Відпустити кнопку
  }
}