import SoundProcessModule.SoundDataDivider as sdd
import SoundProcessModule.SoundToImageConverter as stoi
import SoundProcessModule.SiameseClassifier as siamese
# import SoundProcessModule.dBChecker as dbc
# import UI as tui
import os
import sounddevice as sd
import asyncio
import keyboard
recording=True
def main():
	print("Welcome To HomeGuardian")
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	loop.create_task(start_soundProcess())

	# ESC 키를 눌렀을 때 루프 종료
	keyboard.on_press_key("esc", lambda _: stop_soundProcess(loop))
	
	try:
		loop.run_forever()
	except KeyboardInterrupt:
		print("KeyboardInterrupt 발생")
	finally:
		loop.close()





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
		trainer.train_model(data_path=data_path, epochs=10, batch_size=32, learning_rate=0.001)
	else:
		print("siamese::저장된 모델을 불러왔습니다.")

	
	task = asyncio.create_task(loop_soundProcess(divider,converter,trainer,record_folder,img_folder,count))
	try:
		while not task.done():
			await asyncio.sleep(1)
	except asyncio.CancelledError:
		print("start_soundProcess 종료")
	finally:
		task.cancel()
		await task

async def loop_soundProcess(divider,converter,trainer,record_folder,img_folder,count):
	
	try:
		while True:
			# 사운드 저장
			cur_recordname=divider.record_one(count)
			# print(count)
			# print(cur_recordname)
			# print(os.path.join(record_folder,cur_recordname))
			
			# 멜-스펙트로그램으로 전환하여 저장
			converter.save_mel_spectrogram(filepath=os.path.join(record_folder,cur_recordname),filename=cur_recordname)
			count+=1

			# 전환한 이미지를 예측
			isFireAlarm=trainer.predict_similarity(img_folder+"/"+cur_recordname.replace('.wav', '.png'), "dataset/fire_alarm/reference.png", threshold=0.4)
			await asyncio.sleep(1)
			if isFireAlarm:
				raise_fireAlarm()

			# 이미지와 사운드가 20개 이상이면, 기존 것 삭제
			
			if len(os.listdir(record_folder)) > 20:
				print("파일 20개 초과, 삭제")
				os.remove(record_folder+"/"+f"recording_{count-20}.wav")
				os.remove(img_folder+"/"+f"recording_{count-20}.png")

	except Exception as e:
		print(f"Error in loop_soundProcess: {e}")
		raise

def stop_soundProcess(loop):
	print("loop stopped")
	for task in asyncio.all_tasks(loop):
		task.cancel()
	loop.stop()

if __name__ == '__main__':
	main()

def raise_fireAlarm():
	print("FIRE_ALARM")
