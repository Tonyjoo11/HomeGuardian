import os
import json
import requests
from urllib.parse import quote

# 카카오 REST API 관련 변수
AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
CLIENT_ID = "9de4f4eef8be61e9e9bec94d7d8cfe7e"  # 자신의 REST API 키
REDIRECT_URI = "https://localhost:5000"  # 리디렉션 URI

# 카카오 API URL
FRIENDS_URL = "https://kapi.kakao.com/v1/api/talk/friends"  # 친구 목록 API
MESSAGE_URL = "https://kapi.kakao.com/v1/api/talk/friends/message/default/send"  # 메시지 보내기 API

# 저장된 토큰을 파일에서 읽기
def load_tokens():
	if os.path.exists("UI/tokens.json"):
		with open("UI/tokens.json", "r") as file:
			return json.load(file)
	else:
		return None

# 토큰을 파일에 저장
def save_tokens(access_token, refresh_token):
	with open("tokens.json", "w") as file:
		json.dump({"access_token": access_token, "refresh_token": refresh_token}, file)

# 인증 코드로 access_token과 refresh_token 발급
def get_tokens_from_code(auth_code):
	url = "https://kauth.kakao.com/oauth/token"
	params = {
		"grant_type": "authorization_code",
		"client_id": CLIENT_ID,
		"redirect_uri": REDIRECT_URI,
		"code": auth_code,  # 인증 코드
	}
	response = requests.post(url, data=params)
	tokens = response.json()

	if response.status_code == 200:
		# 인증 성공, tokens.json 파일에 저장
		save_tokens(tokens["access_token"], tokens.get("refresh_token"))
		print("Tokens saved:", tokens)
		return tokens
	else:
		print("Failed to get tokens:", tokens)
		return None

# 저장된 refresh_token을 사용해 access_token 갱신
def refresh_access_token(refresh_token):
	url = "https://kauth.kakao.com/oauth/token"
	params = {
		"grant_type": "refresh_token",
		"client_id": CLIENT_ID,
		"refresh_token": refresh_token,
	}
	response = requests.post(url, data=params)
	data = response.json()
	if response.status_code == 200:
		print("Access token refreshed:", data)
		new_access_token = data.get("access_token")
		new_refresh_token = data.get("refresh_token", refresh_token)  # refresh_token이 갱신되지 않으면 기존 값 유지
		save_tokens(new_access_token, new_refresh_token)
		return new_access_token
	else:
		print("Failed to refresh access token:", data)
		return None

# 카카오 친구 목록을 가져오는 함수
def get_friends_list(access_token):
	headers = {"Authorization": f"Bearer {access_token}"}
	response = requests.get(FRIENDS_URL, headers=headers)

	if response.status_code == 200:
		friends = response.json().get('elements', [])
		if not friends:
			print("No friends found.")
			return None
		return friends
	else:
		print("Failed to get friends:", response.json())
		return None

# 친구에게 메시지를 보내는 함수
def send_message_to_friend(friend_id, access_token, text):
	headers = {"Authorization": f"Bearer {access_token}"}
	data = {
		"receiver_uuids": json.dumps([friend_id]),  # 친구 ID 리스트
		"template_object": json.dumps({
			"object_type": "text",
			"text": text,
			"link": {
				"web_url": "https://developers.kakao.com",  # 웹 URL
				"mobile_web_url": "https://developers.kakao.com"  # 모바일 웹 URL
			},
			"button_title": "바로 확인"
		})
	}
	response = requests.post(MESSAGE_URL, headers=headers, data=data)
	if response.status_code == 200:
		print("Message sent successfully!")
	else:
		print("Failed to send message:", response.json())

# 인증된 토큰으로 메시지 전송
def send_message():
	tokens = load_tokens()

	if not tokens:
		print("No tokens found, please authenticate first.")
		return

	access_token = tokens.get("access_token")
	refresh_token = tokens.get("refresh_token")

	# access_token 만료 여부 테스트
	test_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
	headers = {"Authorization": f"Bearer {access_token}"}
	test_response = requests.post(test_url, headers=headers)
	
	# access_token이 만료되었을 경우 refresh_token으로 갱신
	if test_response.status_code == 401:
		print("Access token expired, refreshing...")
		access_token = refresh_access_token(refresh_token)
		if not access_token:
			print("Failed to refresh access token. Exiting.")
			return
		headers = {"Authorization": f"Bearer {access_token}"}

	# 친구 목록을 가져옵니다.
	friends = get_friends_list(access_token)
	if not friends:
		print("No friends to send the message to.")
		return

	# 친구 리스트에서 원하는 친구를 선택 (예시로 첫 번째 친구)
	friend_id = friends[0]['uuid']  # 첫 번째 친구의 UUID를 선택
	print(f"Sending message to: {friends[0]['profile_nickname']}")

	# 친구에게 메시지 보내기
	msg_str="청각장애인 함유상 님의 집에서 긴급 상황이 발생했습니다!\n 신속히 출동해 주시기 바랍니다!\n 주소:서울특별시 동작구 상도동 사당로 50"
			

	send_message_to_friend(friend_id, access_token, msg_str)

# 사용자에게 인증 코드 입력 받기
def authenticate():
	print_auth_url()  # 인증 URL 출력
	auth_code = input("Enter the authorization code from the Kakao login: ")
	tokens = get_tokens_from_code(auth_code)

	if tokens:
		send_message()

# 카카오 로그인 URL을 자동 생성하여 출력
def print_auth_url():
	# 인증 URL에 'friends' 스코프 추가
	auth_url = f"{AUTH_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={quote(REDIRECT_URI)}&scope=friends"
	print(f"Please visit the following URL to authenticate and get the authorization code:\n{auth_url}")

# 실행
if __name__ == "__main__":
	tokens = load_tokens()
	if not tokens:
		print("No tokens found. Please authenticate.")
		authenticate()  # 인증 코드 받기
	else:
		send_message()  # 이미 토큰이 있는 경우 메시지 전송
