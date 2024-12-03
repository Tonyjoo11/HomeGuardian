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

recording=True
async def main():
	print("Welcome To HomeGuardian")

	# ESC 키를 눌렀을 때 루프 종료
	
	loop = asyncio.get_event_loop()

	sound_task = asyncio.create_task(start_soundProcess())	
	
	# keyboard.on_press_key("esc", lambda _: stop_soundProcess(loop))
	server_socket, port = brt.create_server_socket()
	client_socket, address = await wait_for_client_connection(server_socket)
	red_callback = create_red_callback(client_socket)
	yellow_callback = create_yellow_callback(client_socket)
	off_callback = create_off_callback(client_socket)
	
	app = ui.App(stop_callback=stop_soundProcess,
			loop=loop,
			red_callback= red_callback,
			yellow_callback= yellow_callback,
			off_callback= off_callback
			)
	
	try:
		await asyncio.gather(
			app.tkinter_event_loop(),  # Tkinter 이벤트 루프
			sound_task,  # 추가 비동기 작업 실행
		)
	except KeyboardInterrupt:
		print("KeyboardInterrupt 발생")
	except Exception as e:
		print(f"Error:{e}")
	finally:
		# loop.close()
		brt.close_server_socket(server_socket)


def create_red_callback(client_socket):
	"""
	비동기 `send_bluetooth_fire`를 동기 콜백처럼 사용할 수 있는 래퍼를 반환합니다.
	"""
	async def red_callback():
		if client_socket:
			try:
				await brt.handle_client_communication(client_socket,"RED")
			except Exception as e:
				print(f"Error while sending Bluetooth fire signal: {e}")
		else:
			print("Client socket is not connected.")
	return red_callback

def create_yellow_callback(client_socket):
	"""
	비동기 `send_bluetooth_fire`를 동기 콜백처럼 사용할 수 있는 래퍼를 반환합니다.
	"""
	async def yellow_callback():
		if client_socket:
			try:
				await brt.handle_client_communication(client_socket,"YELLOW")
			except Exception as e:
				print(f"Error while sending Bluetooth fire signal: {e}")
		else:
			print("Client socket is not connected.")
	return yellow_callback

def create_off_callback(client_socket):
	"""
	비동기 `send_bluetooth_fire`를 동기 콜백처럼 사용할 수 있는 래퍼를 반환합니다.
	"""
	async def off_callback():
		if client_socket:
			try:
				await brt.handle_client_communication(client_socket,"OFF")
			except Exception as e:
				print(f"Error while sending Bluetooth fire signal: {e}")
		else:
			print("Client socket is not connected.")
	return off_callback

async def wait_for_client_connection(server_socket):
	"""
	클라이언트가 연결될 때까지 무한히 대기합니다.
	:param server_socket: 블루투스 서버 소켓
	:return: 연결된 클라이언트 소켓과 주소
	"""
	print("Waiting for a client to connect...")
	while True:
		try:
			client_socket, address = await brt.accept_client_connection(server_socket)
			print(f"Client connected from {address}")
			return client_socket, address
		except Exception as e:
			print(f"Connection attempt failed: {e}. Retrying...")
			await asyncio.sleep(2)  # 2초 대기 후 다시 시도

async def start_soundProcess():
	global recording
	recording=True
	device_id = 1
	record_folder="record"	
	if not os.path.exists(record_folder):
		os.mkdir(record_folder)
	divider = sdd.SoundDataDivider(device_id=1, sample_rate=44100, 
								duration=5, interval=6,save_folder=record_folder)
	
	# print(sd.query_devices())
	img_folder="spectrogram"
	converter = stoi.SoundToImageConverter(input_folder=record_folder,output_folder="spectrogram")
	count = 0

	data_path = 'dataset'
	trainer = siamese.SiameseTrainer()
	if not os.path.exists(trainer.model_path):
		# 인공지능 모델 생성
		trainer.train_model(data_path=data_path, epochs=30, batch_size=32, learning_rate=0.001)
	else:
		print("siamese::저장된 모델을 불러왔습니다.")

	
	task = asyncio.create_task(
		loop_soundProcess(divider,converter,trainer,record_folder,img_folder,count))
	try:
		while not task.done():
			await asyncio.sleep(0.1)
	except Exception as e:
		print(f"start_soundProcess 종료:{e}")
	finally:
		task.cancel()
		await task

async def loop_soundProcess(divider,converter,trainer,record_folder,img_folder,count):
	try:
		dBchecker = dbc.dBChecker()
	
		while True:
			# 사운드 저장
			cur_recordname = await divider.record_one(count)


			dBchecker.file_path = os.path.join(record_folder,cur_recordname)
			dB = dBchecker.check_decibel()
			print(f"dBc: {cur_recordname}:{dB}dB")
			# 멜-스펙트로그램으로 전환하여 저장
			converter.save_mel_spectrogram(
				filepath=os.path.join(record_folder,cur_recordname),
				filename=cur_recordname)
			count+=1

			# 전환한 이미지를 예측
			reference = "dataset/fire_alarm/reference.png"
			isFireAlarm=trainer.predict_similarity(
				os.path.join(img_folder,cur_recordname.replace('.wav', '.png')),
				  reference, 
				  threshold=0.4)
			await asyncio.sleep(0.1)
			if isFireAlarm:
				raise_fireAlarm()

			# 이미지와 사운드가 20개 이상이면, 기존 것 삭제
			
			if count > 20:
				print("파일 20개 초과, 삭제")
				os.remove(record_folder+"/"+f"recording_{count-20}.wav")
				os.remove(img_folder+"/"+f"recording_{count-20}.png")

	except Exception as e:
		print(f"Error in loop_soundProcess: {e}")
		raise

def stop_soundProcess(loop):
	print("loop stopped")
	tasks = [task for task in asyncio.all_tasks(loop) if not task.done()]
	for task in tasks:
		task.cancel()
	loop.stop()

def raise_fireAlarm():
	print("FIRE_ALARM")

if __name__ == '__main__':
	asyncio.run(main())

