#define LED 13
String str;

unsigned long previousMillis = 0;
const long interval = 5000;    // 設定間隔時間，5000ms
bool hasRun = false;           // 標記是否已經執行過
char chr;

void setup() {
  pinMode(LED, OUTPUT);
  Serial.begin(9600);

  // 初始延遲 8 秒
  delay(8000);
}

void loop() {
  unsigned long currentMillis = millis();

  // 檢查是否已經達到時間間隔並且尚未執行過
  if (currentMillis - previousMillis >= interval && !hasRun) {
    previousMillis = currentMillis;
    Serial.println("Call CallGCPLogAndArduinoBack.py");
    hasRun = true;  // 標記為已經執行過
  }

  // 檢查是否有串口輸入
  if (Serial.available()) {
    // 讀取傳入的字串直到"\n"結尾
    str = Serial.readStringUntil('\n');

    if (str == "LED_ON") {           // 若字串值是 "LED_ON" 開燈
        digitalWrite(LED, HIGH);     // 開燈
        Serial.println("LED is ON"); // 回應訊息給電腦
    } else if (str == "LED_OFF") {
        digitalWrite(LED, LOW);
        Serial.println("LED is OFF");
    }
  }
}
