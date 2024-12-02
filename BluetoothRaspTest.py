import bluetooth
from bluetoothNanoTest import write_data_to_peripheral
import asyncio
# 블루투스 서버 주소 (라즈베리파이 MAC 주소 입력)
server_mac_address = "2C:CF:67:12:22:8E"
port = 1  # RFCOMM 기본 포트


# 블루투스 소켓 생성 및 연결
client_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
client_socket.connect((server_mac_address, port))
print(f"Connected to {server_mac_address}")
while True:
	try:
		# 데이터 전송
		message = "ACK"
		client_socket.send(message.encode('utf-8'))
		print(f"Sent: {message}")

		# 서버로부터 응답 수신
		response = client_socket.recv(1024)
		print(f"Received: {response.decode('utf-8')}")
		asyncio.run(write_data_to_peripheral(str(response.decode('utf-8'))))
	except KeyboardInterrupt:
		break


client_socket.close()
