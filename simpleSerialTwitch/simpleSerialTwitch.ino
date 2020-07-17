#include <ArduinoJson.h>
#include <Adafruit_NeoPixel.h>

#define PIN        6

Adafruit_NeoPixel pixels(30, PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  Serial.begin(115200);
  pixels.begin();
  while(!Serial) {
  }
}

void loop() {
  int     size_ = 0;
  String  payload;
  while ( !Serial.available()  ){}
  if ( Serial.available() )
    payload = Serial.readStringUntil( '\n' );
  DynamicJsonDocument doc(512);

  DeserializationError   error = deserializeJson(doc, payload);
  if (error) {
    Serial.println(error.c_str()); 
    return;
  }
  
  //Serial.println(doc["data"].size());
  //Serial.println(quantity);

  int position = doc["position"];
  String status = doc["status"];

  Serial.println(status);
  
  if(status == "start"){
    //pixels.clear();
    //pixels.show();
  }

  // method to show leds
  
  for (int i = 0; i < doc["data"].size(); i++) {
    String data = doc["data"][i];
    int r = doc["data"][i]["color"]["r"];
    int g = doc["data"][i]["color"]["g"];
    int b = doc["data"][i]["color"]["b"];
    Serial.println(data);
    Serial.println(position + i);
    pixels.setPixelColor(position + i, pixels.Color(r, g, b));
  }

  Serial.println(status);

  // method to clear all leds following the active ones
  
  if(status == "end"){

    int last_led = doc["data"].size() + position;

    for (int i = last_led; i != 31; i++) {
      //Serial.println(i);
      pixels.setPixelColor(i, pixels.Color(0, 0, 0));
    }
    
    pixels.show();
  }
  
  delay(20);
}
