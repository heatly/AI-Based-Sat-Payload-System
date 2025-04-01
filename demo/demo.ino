#include <ArduinoJson.h>
#include <DHT.h>

#define DHTPIN 4        // DHT11 sensor pin
#define DHTTYPE DHT11   // Define sensor type
DHT dht(DHTPIN, DHTTYPE);

#define MQ135_PIN 34    // Air quality sensor pin
#define LDR_PIN 35      // Light intensity sensor pin

void setup() {
    Serial.begin(115200);
    dht.begin();
}

void loop() {
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    int air_quality = analogRead(MQ135_PIN);
    int light_intensity = analogRead(LDR_PIN);

    // Scale air quality (0-1023) to percentage
    float air_quality_scaled = map(air_quality, 0, 1023, 0, 100);
    
    // Scale light intensity (0-4095) to realistic values
    float light_intensity_scaled = map(light_intensity, 0, 4095, 0, 2000);

    // Create JSON object
    StaticJsonDocument<200> doc;
    doc["temperature"] = temperature;
    doc["humidity"] = humidity;
    doc["air_quality"] = air_quality_scaled;
    doc["light_intensity"] = light_intensity_scaled;

    // Serialize JSON and send over Serial
    String jsonData;
    serializeJson(doc, jsonData);
    Serial.println(jsonData);

    delay(2000); // Send data every 2 seconds
}
