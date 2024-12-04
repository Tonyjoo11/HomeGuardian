from SoundProcessModule import SoundDataDivider as sdd
from SoundProcessModule import SoundToImageConverter as stoi
from SoundProcessModule import SiameseClassifier as siamese
from SoundProcessModule import dBChecker as dbc
import UI.UI as ui
import os
import sounddevice as sd
import asyncio
# import keyboard
import BluetoothRaspTest as brt
from selenium_model_async import AsyncModel  # 이미 임포트되어 있음

recording = True

async def main():
	global app
	print("Welcome To HomeGuardian")

	# ESC 키를 눌렀을 때 루프 종료
	loop = asyncio.get_event_loop()

	# Bluetooth 설정
	server_socket, port = brt.create_server_socket()
	client_socket, address = await wait_for_client_connection(server_socket)
	red_callback = create_red_callback(client_socket)
	yellow_callback = create_yellow_callback(client_socket)
	off_callback = create_off_callback(client_socket)

	# UI 앱 초기화
	app = ui.App(
		stop_callback=stop_soundProcess,
		loop=loop,
		red_callback=red_callback,
		yellow_callback=yellow_callback,
		off_callback=off_callback
	)

	# AsyncModel 초기화 및 시작
	model = AsyncModel("test.html")
	await model.start()

	# 모델 예측 업데이트를 위한 태스크 생성
	model_task = asyncio.create_task(run_model_predictions(model))

	try:
		# 앱 이벤트 루프와 모델 예측 업데이트를 동시에 실행
		await asyncio.gather(
			app.tkinter_event_loop(),  # Tkinter 이벤트 루프
			model_task,                # 모델 예측 업데이트 태스크
			# sound_task,              # 추가 비동기 작업 실행 (주석 처리된 상태)
		)
	except KeyboardInterrupt:
		print("KeyboardInterrupt 발생")
	except Exception as e:
		print(f"Error: {e}")
	finally:
		# 리소스 정리
		await model.stop()  # 모델 중지
		brt.close_server_socket(server_socket)

async def run_model_predictions(model):
	"""
	모델의 예측을 주기적으로 업데이트하고 결과를 처리하는 함수
	"""
	try:
		while True:
			await asyncio.sleep(1)  # 1초마다 예측 업데이트
			await model.update_predictions()
			predictions = model.get_current_predictions()
			print("현재 예측값:", predictions)
			if predictions['Class 2']>0.9:
				raise_fireAlarm()
			# 예측 결과에 따른 추가 로직을 여기에 추가할 수 있습니다.
	except asyncio.CancelledError:
		# 태스크가 취소될 때의 처리
		pass

def create_red_callback(client_socket):
	async def red_callback():
		if client_socket:
			try:
				await brt.handle_client_communication(client_socket, "RED")
			except Exception as e:
				print(f"Error while sending Bluetooth fire signal: {e}")
		else:
			print("Client socket is not connected.")
	return red_callback

def create_yellow_callback(client_socket):
	async def yellow_callback():
		if client_socket:
			try:
				await brt.handle_client_communication(client_socket, "YELLOW")
			except Exception as e:
				print(f"Error while sending Bluetooth fire signal: {e}")
		else:
			print("Client socket is not connected.")
	return yellow_callback

def create_off_callback(client_socket):
	async def off_callback():
		if client_socket:
			try:
				await brt.handle_client_communication(client_socket, "OFF")
			except Exception as e:
				print(f"Error while sending Bluetooth fire signal: {e}")
		else:
			print("Client socket is not connected.")
	return off_callback

async def wait_for_client_connection(server_socket):
	print("Waiting for a client to connect...")
	while True:
		try:
			client_socket, address = await brt.accept_client_connection(server_socket)
			print(f"Client connected from {address}")
			return client_socket, address
		except Exception as e:
			print(f"Connection attempt failed: {e}. Retrying...")
			await asyncio.sleep(2)  # 2초 대기 후 다시 시도

def raise_fireAlarm():
	global app
	app.show_fire_screen()

# def stop_soundProcess():
	# 필요한 경우 사운드 처리 중지를 위한 로직을 추가하세요.
	# pass

if __name__ == '__main__':
	asyncio.run(main())
