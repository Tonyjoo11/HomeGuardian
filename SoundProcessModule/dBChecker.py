import numpy as np
from scipy.io import wavfile
import os
import glob
class dBChecker:
	def __init__(self):
		"""
		dBChecker 클래스 초기화.

		:param file_path: 데시벨을 계산할 .wav 파일 경로
		"""
		# self.file_path = file_path

	def read_audio_file(self):
		"""
		지정된 .wav 파일에서 오디오 데이터를 읽어 반환.

		:return: 샘플링 속도, 오디오 데이터 (numpy 배열)
		"""
		print(f"dBc::Reading audio data from {self.file_path}...")
		sample_rate, audio_data = wavfile.read(self.file_path)
		return sample_rate, audio_data

	def calculate_decibel(self, audio_data):
		"""
		입력된 오디오 데이터의 데시벨(dB) 수준을 계산.

		:param audio_data: 오디오 데이터 (numpy 배열)
		:return: 계산된 데시벨 수준 (float)
		"""
		# 스테레오 데이터인 경우 첫 번째 채널만 사용
		if len(audio_data.shape) > 1:
			audio_data = audio_data[:, 0]

		# RMS 계산 후 dB 변환
		rms = np.sqrt(np.mean(audio_data**2))
		db_level = 20 * np.log10(rms) if rms > 0 else -np.inf  # 로그 계산을 위해 rms가 0보다 클 때만 계산
		return db_level

	def check_decibel(self):
		"""
		.wav 파일을 읽고 데시벨 수준을 계산하여 반환.

		:return: 데시벨 수준 (float)
		"""
		_, audio_data = self.read_audio_file()
		db_level = self.calculate_decibel(audio_data)
		# print(f"Measured dB level: {db_level:.2f} dB")
		return db_level

def main():
    folder_path = "./record"  # 검사할 폴더 경로
    wav_files = glob.glob(os.path.join(folder_path, "*.wav"))  # 폴더 내 모든 .wav 파일 경로 목록
    
    # 모든 .wav 파일에 대해 데시벨 계산
    for wav_file in wav_files:
        checker = dBChecker(wav_file)
        db_level = checker.check_decibel()
        print(f"File: {wav_file} - dB Level: {db_level:.2f} dB")

# if __name__ == "__main__":
#     main()
