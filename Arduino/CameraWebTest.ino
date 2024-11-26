#include <WiFi.h>
#include <WiFiClient.h>
#include "esp_camera.h"

// 카메라 모델 선택
#define CAMERA_MODEL_AI_THINKER
#include "camera_pins.h"

// Wi-Fi 설정
const char* ssid = "AndroidHotspot7754";
const char* password = "12345678";

// TCP 서버 설정
WiFiServer tcpServer(5000);
WiFiClient tcpClient;

uint8_t rx_buf[1024];
uint16_t rx_len = 0;
uint8_t tx_buf[1024];
uint16_t tx_len = 0;

// 함수 선언 (정의는 app_httpd.cpp에서 이루어집니다)
void startCameraServer();
void setupLedFlash(int pin);

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  // 카메라 설정
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_UXGA;
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  if (config.pixel_format == PIXFORMAT_JPEG) {
    if (psramFound()) {
      config.jpeg_quality = 10;
      config.fb_count = 2;
      config.grab_mode = CAMERA_GRAB_LATEST;
    } else {
      config.frame_size = FRAMESIZE_SVGA;
      config.fb_location = CAMERA_FB_IN_DRAM;
    }
  } else {
    config.frame_size = FRAMESIZE_240X240;
  }

  // 카메라 초기화
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  sensor_t *s = esp_camera_sensor_get();
  if (s->id.PID == OV3660_PID) {
    s->set_vflip(s, 1);
    s->set_brightness(s, 1);
    s->set_saturation(s, -2);
  }

  if (config.pixel_format == PIXFORMAT_JPEG) {
    s->set_framesize(s, FRAMESIZE_QVGA);
  }

  // Wi-Fi 연결
  WiFi.begin(ssid, password);
  WiFi.setSleep(false);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected.");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  // 카메라 서버 시작
  startCameraServer();

  Serial.print("Camera Ready! Use 'http://");
  Serial.print(WiFi.localIP());
  Serial.println("' to connect");

  // TCP 서버 시작
  tcpServer.begin();
  tcpServer.setNoDelay(true);
}

void loop() {
  // TCP 클라이언트 연결 처리
  if (tcpServer.hasClient()) {
    if (!tcpClient || !tcpClient.connected()) {
      tcpClient = tcpServer.available();
      Serial.println("Accept new Connection ...");
    } else {
      WiFiClient temp = tcpServer.available();
      temp.stop();
      Serial.println("Reject new Connection ...");
    }
  }

  if (!tcpClient || !tcpClient.connected()) {
    delay(100);
    return;
  }

  while (tcpClient.connected()) {
    if (tcpClient.available()) {
      while (tcpClient.available()) {
        rx_buf[rx_len] = tcpClient.read();
        rx_len++;
      }
      Serial.write(rx_buf, rx_len);
      rx_len = 0;
    }
    if (Serial.available()) {
      while (Serial.available()) {
        tx_buf[tx_len] = Serial.read();
        tx_len++;
      }
      tcpClient.write(tx_buf, tx_len);
      tx_len = 0;
    }
    delay(1);
  }
}
