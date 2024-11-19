import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import time
import os

class SoundDataDivider:
	def __init__(self, device_id, sample_rate=44100, duration=5, interval=10):
		"""
		SoundDataDivider 클래스 초기화.

		:param device_name: 녹음에 사용할 마이크 장치 이름
		:param sample_rate: 오디오 샘플링 속도 (Hz)
		:param duration: 녹음 시간 (초)
		:param interval: 파일 저장 간격 (초)
		"""
		
		# self.device_name = device_name
		print(sd.query_devices())
		self.sample_rate = sample_rate
		self.duration = duration
		self.interval = interval
		self.device_id = device_id#self.get_device_id_by_name(device_name)
		self.recording = False

	
	def record_audio(self,filename, duration, sample_rate,device):
		print(f"Recording {duration} seconds on device {device}...")
		audio_data = sd.rec(int(duration *sample_rate), samplerate=sample_rate,
						channels=1, dtype='int16',device=device)
		sd.wait()
		write(filename,sample_rate, audio_data)
		print(f"Saved {filename}")


	def start_recording(self):
		self.recording=True
		count = 0
		try:
			while self.recording:
				filename = f"record/recording_{count}.wav"
				self.record_audio(filename, self.duration, self.sample_rate, device=self.device_id)
				count+=1
				time.sleep(max(0,self.interval-self.duration))

		except KeyboardInterrupt:
			print("Recoding stopped")
	def stop_recording(self):
			"""
			상시 녹음을 중지.
			"""
			self.recording = False
			print("Recording stopped.")

def main():
	# 장치 ID, 녹음 속도, 녹음 시간, 간격 설정
	device_name = ""  # 사용할 마이크의 이름으로 변경
	device_id = 1
	sample_rate = 44100
	duration = 5
	interval = 10
	
	# 저장 폴더 경로
	save_folder = "record"
	
	# 폴더가 존재하지 않으면 생성
	if not os.path.exists(save_folder):
		os.makedirs(save_folder)
	
	# SoundDataDivider 인스턴스 생성
	divider = SoundDataDivider(device_id=device_id, sample_rate=sample_rate, duration=duration, interval=interval)
	
	# 녹음 시작
	try:
		divider.start_recording()
	except KeyboardInterrupt:
		divider.stop_recording()

# if __name__ == "__main__":
# 	main()