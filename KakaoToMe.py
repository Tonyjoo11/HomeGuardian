import os
import json
import requests
from PyKakao import Message

# 서비스 키로 API 객체 생성
API = Message(service_key="9de4f4eef8be61e9e9bec94d7d8cfe7e")  # 자신의 카카오 REST API 키 입력

# 저장된 토큰을 파일에서 읽기
def load_tokens():
    if os.path.exists("tokens.json"):
        with open("tokens.json", "r") as file:
            return json.load(file)
    else:
        return None

# 토큰을 파일에 저장
def save_tokens(access_token, refresh_token):
    with open("tokens.json", "w") as file:
        json.dump({"access_token": access_token, "refresh_token": refresh_token}, file)

# 저장된 refresh_token을 사용해 access_token 갱신
def refresh_access_token(refresh_token):
    url = "https://kauth.kakao.com/oauth/token"
    params = {
        'grant_type': 'refresh_token',
        'client_id': '9de4f4eef8be61e9e9bec94d7d8cfe7e',  # 자신의 REST API 키
        'refresh_token': refresh_token
    }
    response = requests.post(url, data=params)
    data = response.json()
    if response.status_code == 200:
        return data.get('access_token'), data.get('refresh_token')
    else:
        print("Failed to refresh access token:", data)
        return None, None

# 인증된 토큰으로 메시지 전송
def send_message():
    tokens = load_tokens()

    if not tokens:
        print("No tokens found, please authenticate first.")
        return

    access_token = tokens['access_token']
    refresh_token = tokens['refresh_token']

    # access_token이 만료되었으면 refresh_token으로 갱신
    # 만약 access_token으로 API 호출 시 '401 Unauthorized'가 발생하면 refresh_token을 사용해 새로 갱신
    test_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    test_response = requests.post(test_url, headers=headers)
    if test_response.status_code == 401:  # access_token이 만료된 경우
        print("Access token expired, refreshing...")
        access_token, refresh_token = refresh_access_token(refresh_token)
        if not access_token:
            print("Failed to refresh access token.")
            return
        save_tokens(access_token, refresh_token)

    # API에 새로운 access_token 설정
    API.set_access_token(access_token)

    # 메시지 유형 - 텍스트
    message_type = "text"
    text = "텍스트 영역입니다. 최대 200자 표시 가능합니다."
    link = {
        "web_url": "https://developers.kakao.com",
        "mobile_web_url": "https://developers.kakao.com"
    }
    button_title = "바로 확인"

    # 메시지 보내기
    API.send_message_to_me(
        message_type=message_type,
        text=text,
        link=link,
        button_title=button_title,
    )

    print("메시지 전송 완료")

# 실행
send_message()
