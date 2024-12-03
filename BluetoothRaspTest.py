import bluetooth
from bleak import BleakClient
import asyncio
# 블루투스 서버 주소 (라즈베리파이 MAC 주소 입력)
server_mac_address = "2C:CF:67:12:22:8E"
port = 1  # RFCOMM 기본 포트
DEVICE_MAC_ADDRESS = "CE:04:78:05:29:87"  # 아두이노의 BLE MAC 주소
SERVICE_UUID = "6f742e01-ec6e-4621-a0db-7511cc6c46ad"  # 아두이노 서비스 UUID
CHARACTERISTIC_UUID = "00000000-0000-0000-0000-000000000000"  # 특성 UUID
RECONNECT_DELAY = 5

# 블루투스 소켓 생성 및 연결

async def write_data_to_peripheral(data_to_write,client):
    # Peripheral에 연결
	# print(f"Connected to device at {DEVICE_MAC_ADDRESS}")

	# 데이터 쓰기
	# data_to_write = input()  # 아두이노에 보낼 데이터
	await client.write_gatt_char(CHARACTERISTIC_UUID, data_to_write.encode("utf-8"))
	print(f"Data sent: {data_to_write}")
async def main():
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
			async with BleakClient(DEVICE_MAC_ADDRESS) as client:
				await write_data_to_peripheral(str(response.decode('utf-8')),client)
		except KeyboardInterrupt:
			break


	client_socket.close()

asyncio.run(main())