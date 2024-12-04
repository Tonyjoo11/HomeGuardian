# selenium_model.py

import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# 전역 변수
driver = None
predictions = {}

def setup_chrome_driver():
    global driver
    if driver is None:
        chrome_options = Options()
        chrome_options.add_argument("--use-fake-ui-for-media-stream")  # 마이크 접근 자동 허용
        driver = webdriver.Chrome(options=chrome_options)

def open_local_html(html_file_path):
    html_file = os.path.abspath(html_file_path)
    driver.get("file://" + html_file)

def start_model(html_file_path):
    global driver
    setup_chrome_driver()
    open_local_html(html_file_path)
    # "Start" 버튼 클릭하여 모델 초기화 및 예측 시작
    start_button = driver.find_element(By.XPATH, "//button[text()='Start']")
    start_button.click()

def update_predictions():
    global predictions
    try:
        label_container = driver.find_element(By.ID, "label-container")
        labels = label_container.find_elements(By.TAG_NAME, "div")
        current_predictions = {}
        for label in labels:
            text = label.text
            try:
                class_name, score = text.split(": ")
                current_predictions[class_name] = float(score)
            except ValueError:
                continue  # 예상치 못한 포맷의 텍스트는 무시
        predictions = current_predictions
    except Exception as e:
        print("예측 수집 중 오류 발생:", e)

def get_current_predictions():
    return predictions

def stop_model():
    global driver
    if driver is not None:
        # 예측 중지
        driver.execute_script("recognizer.stopListening();")
        # 드라이버 종료
        driver.quit()
        driver = None
