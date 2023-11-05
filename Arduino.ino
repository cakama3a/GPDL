// Налаштовуємо з'єднання
const int buttonPin1 = 2; // Перший провід, що йде до кнопки на геймпаді
const int buttonPin2 = 3; // Другий провід, що йде до кнопки на геймпаді
const int afterPress = 32; // Час між перемиканнями HIGH і LOW (100 мс призводить до дивних показників)
unsigned long startTime;

void setup() {
  pinMode(buttonPin1, OUTPUT);
  pinMode(buttonPin2, OUTPUT);
  Serial.begin(115200); // 115200/9600
}

void loop() {
  delay(afterPress);
  digitalWrite(buttonPin1, LOW); // Замикаємо контакт, натискаємо кнопку
  Serial.println("LOW"); // Відправляємо пайтону що кнопка натиснута
  char data = Serial.read();
  if (data == 'H') {
    digitalWrite(buttonPin1, HIGH);
    Serial.println("HIGH");
  }
}