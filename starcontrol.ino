#include <Arduino.h>

const int POT_PIN = A0; // Вход для потенциометра (крутилки)

void setup() {
  Serial.begin(115200); // Открываем порт на высокой скорости
  while (!Serial) { ; } // Ждем подключения
}

void loop() {
  int potValue = analogRead(POT_PIN);
  
  // Переводим значение датчика в угол от 0 до 2*PI
  float angle = (potValue / 1023.0) * (2.0 * PI);
  
  // Отправляем угол в порт для Python
  Serial.println(angle);
  
  delay(16); // Задержка под 60 кадров в секунду
}
