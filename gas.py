import RPi.GPIO as GPIO  # Raspberry Pi의 GPIO 핀을 제어하기 위한 라이브러리 임포트
import time  # 시간 관련 함수 사용을 위한 라이브러리 임포트

# GPIO 핀 설정
GAS_SENSOR_PIN = 17 

# 설정 초기화
GPIO.setmode(GPIO.BCM)  # 핀 번호를 BCM(보드의 핀 번호 대신 칩 번호) 방식으로 설정
GPIO.setup(GAS_SENSOR_PIN, GPIO.IN)  # 지정한 핀을 입력 모드로 설정 (가스 센서에서 값 읽기)

# 가스 수치 체크 함수
def read_gas_value():
    gas_value = GPIO.input(GAS_SENSOR_PIN)  
    return gas_value 

# 특정 수치를 넘으면 데이터를 다른 파일로 전송하는 함수
def check_and_send_data():
    while True:  
        gas_value = read_gas_value() 
        print(f"현재 가스 수치: {gas_value}")
        
        if gas_value == 1: 
            send_to_file(gas_value)  
        
        time.sleep(1)

# 데이터를 다른 파일로 전송하는 함수
def send_to_file(value):
    with open("gas_alert.txt", "w") as file:
        file.write(f"gas occrurs.\n")  
    print("경고 메시지가 파일로 전송되었습니다.") 

# 메인 프로그램 실행
# if __name__ == "__main__":
#     try:
#         check_and_send_data() 
#     except KeyboardInterrupt:
#         print("프로그램 종료")
#     finally:
#         GPIO.cleanup()
