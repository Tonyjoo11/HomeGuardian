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
        return None  # 토큰 파일이 없으면 None 반환

# 토큰을 파일에 저장
def save_tokens(access_token, refresh_token):
    with open("tokens.json", "w") as file:
        json.dump({"access_token": access_token, "refresh_token": refresh_token}, file)  # JSON 형식으로 저장

# 카카오 로그인 URL 생성
def get_auth_url():
    client_id = '9de4f4eef8be61e9e9bec94d7d8cfe7e'  # 카카오 REST API 키
    redirect_uri = 'http://localhost:8080/callback'  # 인증 후 리디렉션될 URI
    auth_url = f"https://kauth.kakao.com/oauth/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"
    return auth_url

# 인증 후 access_token과 refresh_token을 얻기
def get_tokens_from_code(authorization_code):
    """사용자가 로그인 후 제공된 authorization_code를 통해 access_token을 얻습니다."""
    client_id = '9de4f4eef8be61e9e9bec94d7d8cfe7e'  # 카카오 REST API 키
    redirect_uri = 'http://localhost:8080/callback'  # 인증 후 리디렉션될 URI
    url = "https://kauth.kakao.com/oauth/token"
    data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'code': authorization_code  # 로그인 후 제공된 authorization_code
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens['access_token']
        refresh_token = tokens['refresh_token']
        save_tokens(access_token, refresh_token)  # 발급받은 토큰을 저장
        return access_token, refresh_token
    else:
        print("Failed to get tokens:", response.json())
        return None, None

# 저장된 refresh_token을 사용해 access_token 갱신
def refresh_access_token(refresh_token):
    """refresh_token을 사용하여 새로운 access_token을 발급받습니다."""
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

# 카카오톡 친구 목록 가져오기
def get_friends(access_token):
    url = "https://kapi.kakao.com/v1/api/talk/friends"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        friends = response.json()['elements']
        return friends
    else:
        print("Failed to fetch friends:", response.json())
        return []

# 친구에게 메시지 보내기
def send_message_to_friend(friend_id, access_token):
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "template_object": json.dumps({
            "object_type": "text",
            "text": "텍스트 영역입니다. 최대 200자 표시 가능합니다.",
            "link": {
                "web_url": "https://developers.kakao.com",
                "mobile_web_url": "https://developers.kakao.com"
            },
            "button_title": "바로 확인"
        })
    }

    # 친구에게 메시지 전송
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        print("메시지 전송 완료")
    else:
        print("메시지 전송 실패:", response.json())

# 인증된 토큰으로 메시지 전송
def send_message():
    tokens = load_tokens()  # 저장된 토큰을 읽어옵니다.

    if not tokens:  # 토큰이 없으면 인증을 받으라는 메시지 출력
        print("No tokens found, please authenticate first.")
        auth_url = get_auth_url()  # 인증 URL 생성
        print(f"Please visit this URL to authenticate: {auth_url}")
        authorization_code = input("Enter the authorization code: ")  # 사용자로부터 인증 코드를 입력받음
        access_token, refresh_token = get_tokens_from_code(authorization_code)  # 토큰을 발급받음
        if not access_token:
            print("Failed to get access token.")
            return

    else:
        access_token = tokens['access_token']
        refresh_token = tokens['refresh_token']

    # access_token이 만료되었으면 refresh_token으로 갱신
    # 만약 access_token으로 API 호출 시 '401 Unauthorized'가 발생하면 refresh_token을 사용해 새로 갱신
    test_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {
        "Authorization": f"Bearer {access_token}"  # 헤더에 access_token 추가
    }
    test_response = requests.post(test_url, headers=headers)  # 메시지 전송 테스트
    if test_response.status_code == 401:  # access_token이 만료된 경우
        print("Access token expired, refreshing...")
        access_token, refresh_token = refresh_access_token(refresh_token)  # 토큰 갱신
        if not access_token:  # 갱신이 실패하면 종료
            print("Failed to refresh access token.")
            return
        save_tokens(access_token, refresh_token)  # 갱신된 토큰 저장

    # 카카오톡 친구 목록 가져오기
    friends = get_friends(access_token)
    if not friends:
        print("친구 목록을 가져오지 못했습니다.")
        return
    
    print("친구 목록:", friends)
    
    # 첫 번째 친구에게 메시지 전송 (친구 목록 중 하나를 선택)
    friend_id = friends[0]['id']  # 친구 목록에서 첫 번째 친구의 ID를 사용
    send_message_to_friend(friend_id, access_token)

# 실행
send_message()  # 메시지를 보내는 함수 실행
