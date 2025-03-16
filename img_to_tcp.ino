#include <HardwareSerial.h>
#include <fpm.h>
#include <WiFi.h>

HardwareSerial fserial(1);  // Use UART1 for the fingerprint sensor
FPM finger(&fserial);
FPMSystemParams params;

// Wi-Fi setup
const char* ssid = "Redmi 10 Prime";        // Replace with your network SSID
const char* password = "01223334";  // Replace with your network password

IPAddress tcpServerIp(192, 168, 85, 186);  // Change to your server's IP address
unsigned int tcpServerPort = 9999;     // Use port 9999 for TCP

WiFiClient tcpClient;  // Create a WiFiClient instance

void setup() {
  Serial.begin(57600);
  fserial.begin(57600, SERIAL_8N1, 25, 32);  // UART settings for fingerprint sensor

  Serial.println("Initializing fingerprint sensor...");
  if (!finger.begin()) {
    Serial.println("Did not find fingerprint sensor :(");
    while (1) yield();  // Ensure the watchdog doesn't reset the device in an infinite loop
  }

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
    yield();  // Allow background tasks like Wi-Fi handling
  }
  Serial.println("Connected to Wi-Fi");
}

void loop() {
  sendDataToTcpServer();
  delay(5000);  // Wait for 5 seconds before the next reading
}

void sendDataToTcpServer() {
  // Attempt to connect to TCP server
  if (!tcpClient.connect(tcpServerIp, tcpServerPort)) {
    Serial.println("Connection to TCP server failed.");
    return;
  }

  // Continuously wait for the finger to be placed
  Serial.println("\r\nPlace a finger.");
  FPMStatus status;
  unsigned long startTime = millis();
  unsigned long captureDuration = 5000;  // Set capture duration to 5 seconds

  while (millis() - startTime < captureDuration) {  // Capture for a set duration
    status = finger.getImage();
    if (status == FPMStatus::NOFINGER) {
      Serial.print(".");
      delay(500);  // Wait for a short period to avoid flooding the serial output
      yield();     // Prevent watchdog reset while waiting for a finger
    } else if (status == FPMStatus::OK) {
      Serial.println("\nImage taken.");

      // Download the fingerprint image
      status = finger.downloadImage();
      if (status == FPMStatus::OK) {
        Serial.println("Starting image stream...");
        uint32_t totalRead = 0;
        uint16_t readLen = 0;

        while (true) {
          bool readComplete = false;
          bool ret = finger.readDataPacket(NULL, &tcpClient, &readLen, &readComplete);

          if (!ret) {
            Serial.println("Failed to read data packet.");
            break;
          }

          // Check if the reading is complete
          if (readComplete) {
            break;
          }

          totalRead += readLen;
          yield();  // Yield during the data packet read operation to avoid long blocking
        }

        Serial.print(totalRead);
        Serial.println(" bytes transferred.");

      } else {
        Serial.printf("Error downloading image: 0x%X\n", (uint16_t)status);
      }

    } else {
      Serial.printf("Error taking image: 0x%X\n", (uint16_t)status);
      yield();  // Allow background processes in case of an error
    }

    yield();  // Prevent blocking in the loop
  }

  tcpClient.stop();
  Serial.println("Capture session ended.");
}
