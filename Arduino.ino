// Налаштовуємо з'єднання
const int buttonPin1 = 2; // Перший провід, що йде до кнопки на геймпаді
const int buttonPin2 = 3; // Другий провід, що йде до кнопки на геймпаді
const int afterPress = 200; // Час між перемиканнями HIGH і LOW (100 мс призводить до дивних показників)
unsigned long startTime;

void setup() {
  pinMode(buttonPin1, OUTPUT);
  pinMode(buttonPin2, INPUT_PULLUP);
  digitalWrite(buttonPin2, LOW); // встановлюємо постійне джерело живлення на одному з пінів
  Serial.begin(115200); // 115200/9600
  Serial.setTimeout(1000); // Встановлюємо таймаут для 
}

void loop() {
  //delayMicroseconds(random(0, 1000)); // Даємо час для завершення будь-якої раніше запущеної послідовної передачі
  digitalWrite(buttonPin1, LOW); // Замикаємо контакт, натискаємо кнопку
  unsigned long start_time = micros(); // зберігаємо час натискання кнопки
  while (!Serial.available()) {} // Очікуємо на наявність даних у послідовному порту
  // Отримуємо відповідь data від Пайтон коду
  String data = Serial.readStringUntil('\n');
  // Якщо повернулася правильна відповідь
  if (data == "pong") {
    // Фіксуємо час прийняття сигналу
    unsigned long current_time = micros() - 1000; // Відіймаю затримку між Ардуіною та Пайтоном (від 1000 до 3300)
    // Розрахунок часу
    unsigned long elapsed_time = current_time - start_time;
    // Округлення до сотих мілісекунд
    float rounded_time = round(elapsed_time / 10.0) / 100.0;
    // Пишемо в пайтон час
    Serial.println(rounded_time, 2);
    digitalWrite(buttonPin1, HIGH);
    delay(afterPress);
  }
}