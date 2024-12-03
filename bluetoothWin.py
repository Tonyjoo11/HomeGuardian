import asyncio
import bluetooth
from bleak import BleakClient, BleakError

# BLE 장치의 MAC 주소와 Characteristic UUID
BLE_MAC_ADDRESS = "CE:04:78:05:29:87"  # BLE 장치 MAC 주소
CHARACTERISTIC_UUID = "00000000-0000-0000-0000-000000000000"  # BLE 특성 UUID
server_mac_address = "2C:CF:67:12:22:8E"
port = 1  # RFCOMM 기본 포트

class BLEManager:
	def __init__(self):
		self.client = None
		self.is_connected = False

	async def connect_and_keep_alive(self):
		"""
		BLE Peripheral에 연결을 유지하는 루프.
		연결이 끊어지면 자동으로 재연결 시도.
		"""
		while not self.is_connected:
			try:
				print(f"Attempting to connect to {BLE_MAC_ADDRESS}...")
				self.client = BleakClient(BLE_MAC_ADDRESS)
				await self.client.connect()
				self.is_connected = True
				print(f"Connected to device at {BLE_MAC_ADDRESS}")

			except BleakError as e:
				print(f"Connection failed: {e}")
				self.is_connected = False
				print("Retrying in 5 seconds...")
				await asyncio.sleep(5)

	async def write_characteristic(self, data):
		"""
		BLE 특성에 데이터를 씁니다.
		"""
		if self.is_connected and self.client:
			try:
				await self.client.write_gatt_char(CHARACTERISTIC_UUID, data.encode("utf-8"))
				print(f"Data sent: {data}")
			except BleakError as e:
				print(f"Error during data write: {e}")
		else:
			print("Cannot write data: Not connected to the device.")

async def main():
	ble_manager = BLEManager()
	client_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
	client_socket.connect((server_mac_address, port))
	# BLE 연결 시도 (완료될 때까지 대기)
	await ble_manager.connect_and_keep_alive()

	# 메인 루프: 사용자 입력을 BLE에 쓰기
	try:
		while True:
			try:
				while True:
					message = "ACK"
					client_socket.send(message.encode('utf-8'))
					print(f"Sent: {message}")

					response = client_socket.recv(1024)
					print(f"Received: {response.decode('utf-8')}")

					# send_msg = input("Enter data to send over BLE (or 'exit' to quit): ")
					send_msg = str(response.decode('utf-8'))
					if send_msg.lower() == "exit":
						print("Exiting program...")
						break
					await ble_manager.write_characteristic(send_msg)

			except KeyboardInterrupt:
				print("Program interrupted.")
			except Exception as e:
				print(f"ERR: {e}")
				
	finally:
		print("Shutting down BLE connection...")    
		client_socket.close()
		if ble_manager.client and ble_manager.client.is_connected:
			await ble_manager.client.disconnect()

# 실행
asyncio.run(main())
