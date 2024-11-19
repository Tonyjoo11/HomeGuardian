import os
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
from pydub import AudioSegment

class SoundToImageConverter:
	def __init__(self, input_folder='record', output_folder='spectrogram'):
		self.input_folder = input_folder
		self.output_folder = output_folder
		if not os.path.exists(self.output_folder):
			os.makedirs(self.output_folder)

	def convert_to_spectrogram(self):
		for filename in os.listdir(self.input_folder):
			filepath = os.path.join(self.input_folder, filename)
			if filename.endswith('.wav'):
				self.save_mel_spectrogram(filepath, filename)

	def save_mel_spectrogram(self, filepath, filename):
		# WAV 파일을 읽고 멜 스펙트로그램 생성 및 저장
		try:
			y, sr = librosa.load(filepath, sr=None)  # 원본 샘플링 레이트 유지
			S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
			S_dB = librosa.power_to_db(S, ref=np.max)

			# 멜 스펙트로그램을 이미지로 저장
			plt.figure(figsize=(2.56, 2.56), dpi=100)  # 256x256 크기 설정
			librosa.display.specshow(S_dB, sr=sr, fmax=8000, cmap='viridis')
			plt.axis('off')  # 축을 제거합니다
			spectrogram_path = os.path.join(self.output_folder, filename.replace('.wav', '.png'))
			plt.savefig(spectrogram_path, bbox_inches='tight', pad_inches=0)
			plt.close()
			print(f"Saved mel spectrogram: {spectrogram_path}")
		except Exception as e:
			print(f"멜 스펙트로그램 저장 실패: {filename}, 오류: {e}")

# 사용 예시
def main():
	
	input_folder='fire_alarm_clips'
	output_folder='fire_alarm_clips_spectrogram'
	if not os.path.exists(output_folder):
		os.makedirs(output_folder)
	
	# SoundToImageConverter 객체 생성
	converter = SoundToImageConverter(input_folder=input_folder, output_folder=output_folder)
	
	# WAV 파일을 스펙트로그램 이미지로 변환
	converter.convert_to_spectrogram()
	
	print("모든 WAV 파일이 스펙트로그램 이미지로 변환되었습니다.")

# if __name__ == '__main__':
# 	main()
