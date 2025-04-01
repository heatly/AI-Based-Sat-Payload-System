#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "oppo";
const char* password = "12345678";
const char* serverIP = "192.168.64.65";  // Replace with ESP32's IP Address

WiFiClient client;

void setup() {
    Serial.begin(115200);
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("Connected to WiFi");
}

void loop() {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        String serverPath = "http://" + String(serverIP) + "/data";

        http.begin(client, serverPath);
        int httpResponseCode = http.GET();
        
        if (httpResponseCode > 0) {
            String payload = http.getString();
            Serial.println(payload);  // ✅ Send JSON to Serial
            
            // Parse JSON response
            StaticJsonDocument<200> doc;
            DeserializationError error = deserializeJson(doc, payload);
            
            if (!error) {
                float temperature = doc["temperature"];
                float humidity = doc["humidity"];
                int airQuality = doc["airQuality"];
                
                Serial.print("Temperature: ");
                Serial.print(temperature);
                Serial.println(" °C");
                Serial.print("Humidity: ");
                Serial.print(humidity);
                Serial.println(" %");
                Serial.print("Air Quality: ");
                Serial.println(airQuality);
            } else {
                Serial.println("Failed to parse JSON");
            }
        } else {
            Serial.print("Error in HTTP request: ");
            Serial.println(httpResponseCode);
        }

        http.end();
    } else {
        Serial.println("WiFi not connected");
    }

    delay(5000);  // Fetch data every 5 seconds
}
