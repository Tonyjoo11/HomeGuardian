import bluetooth
# from bluetoothNanoTest import write_data_to_peripheral

# 블루투스 소켓 설정
server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_socket.bind(("", bluetooth.PORT_ANY))
server_socket.listen(1)

port = server_socket.getsockname()[1]
print(f"Listening for connections on port {port}")

# 클라이언트 연결 대기
client_socket, address = server_socket.accept()
print(f"Accepted connection from {address}")

# 데이터 수신
while True:
	try:
		data = client_socket.recv(1024)  # 1024는 최대 버퍼 크기
		if not data:
			break
		print(f"Received: {data.decode('utf-8')}")  # 디코딩하여 문자열로 출력
		client_socket.send("Window: Rasp Acknowledged".encode('utf-8'))  # 응답 메시지 전송
		
		# write_data_to_peripheral(str(data.decode('utf-8')))
	except Exception as e:
		print(f"Error: {e}")
		break

client_socket.close()
server_socket.close()
