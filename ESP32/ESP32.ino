#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <DHT.h>

#define DHTPIN 4       // DHT sensor connected to GPIO4
#define DHTTYPE DHT11  // Change to DHT22 if using it
#define MQ135_PIN 34   // MQ135 sensor connected to GPIO34 (Analog pin)

DHT dht(DHTPIN, DHTTYPE);
const char* ssid = "oppo";
const char* password = "12345678";

AsyncWebServer server(80);

void setup() {
    Serial.begin(115200);
    WiFi.begin(ssid, password);
    
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected to WiFi");
    Serial.print("ESP32 IP Address: ");
    Serial.println(WiFi.localIP());

    dht.begin();

    // Handle HTTP GET request
    server.on("/data", HTTP_GET, [](AsyncWebServerRequest *request) {
        float temperature = dht.readTemperature();
        float humidity = dht.readHumidity();
        int airQuality = analogRead(MQ135_PIN); // Read MQ135 sensor value
        
        if (isnan(temperature) || isnan(humidity)) {
            request->send(500, "text/plain", "Failed to read from DHT sensor");
            return;
        }

        String json = "{\"temperature\": " + String(temperature) + ", \"humidity\": " + String(humidity) + ", \"airQuality\": " + String(airQuality) + "}";
        request->send(200, "application/json", json);
    });

    server.begin();
}

void loop() {
}
