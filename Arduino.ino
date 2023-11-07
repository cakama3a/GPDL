// Налаштовуємо з'єднання
int buttonPin1 = 2; // Перший провід, що йде до кнопки на геймпаді
int buttonPin2 = 3; // Другий провід, що йде до кнопки на геймпаді

void setup() {
  pinMode(buttonPin1, OUTPUT);
  pinMode(buttonPin2, OUTPUT);
  Serial.begin(115200); // 115200/9600
}

void loop() {
  char data = Serial.read();
  if (data == 'L') {
    digitalWrite(buttonPin1, LOW);
  }
  if (data == 'H') {
    digitalWrite(buttonPin1, HIGH);
  }
}