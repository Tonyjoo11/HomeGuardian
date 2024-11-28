import os
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt

"""
AudioSegmenter 모듈
파일에 미리 저장해 둔 학습 사운드를 5초 단위로 자르고, 이를 멜-스펙트로그램 이미지로 저장한다

"""

class AudioSegmenter:
	def __init__(self, input_folder='audio_files', output_folder='segmented_spectrograms', segment_duration=5):
		self.input_folder = input_folder
		self.output_folder = output_folder
		self.segment_duration = segment_duration  # seconds (5 seconds)
		
		if not os.path.exists(self.output_folder):
			os.makedirs(self.output_folder)

	def process_audio_files(self):
		for filename in os.listdir(self.input_folder):
			filepath = os.path.join(self.input_folder, filename)
			if filename.endswith('.wav'):
				self.segment_and_convert(filepath, filename)

	def segment_and_convert(self, filepath, filename):
		# librosa로 오디오 파일 로드
		y, sr = librosa.load(filepath, sr=None)  # 원본 샘플링 레이트 유지
		
		# 오디오를 5초 단위로 분할하고 각 부분을 멜 스펙트로그램 이미지로 저장
		num_segments = len(y) // (self.segment_duration * sr)
		
		for i in range(num_segments):
			start_sample = i * self.segment_duration * sr
			end_sample = start_sample + (self.segment_duration * sr)
			segment = y[start_sample:end_sample]
			
			# 멜 스펙트로그램 생성 및 저장
			self.save_mel_spectrogram(segment, sr, filename, i)

	def save_mel_spectrogram(self, samples, sample_rate, filename, segment_index):
		try:
			# 멜 스펙트로그램 생성
			S = librosa.feature.melspectrogram(y=samples, sr=sample_rate, n_mels=128, fmax=8000)
			S_dB = librosa.power_to_db(S, ref=np.max)

			# 멜 스펙트로그램을 이미지로 저장
			plt.figure(figsize=(2.56, 2.56), dpi=100)  # 256x256 크기 설정
			librosa.display.specshow(S_dB, sr=sample_rate, fmax=8000, cmap='viridis')
			plt.axis('off')  # 축을 제거
			segment_name = f"{filename.replace('.wav', '')}_segment_{segment_index}.png"
			spectrogram_path = os.path.join(self.output_folder, segment_name)
			plt.savefig(spectrogram_path, bbox_inches='tight', pad_inches=0)
			plt.close()
			print(f"Saved mel spectrogram: {spectrogram_path}")
		except Exception as e:
			print(f"멜 스펙트로그램 저장 실패: {segment_index}, 오류: {e}")

def main():

	input_folder='train dataset/beep'
	output_folder='train dataset/beep_spectrogram'
	# AudioSegmenter 객체 생성
	segmenter = AudioSegmenter(input_folder=input_folder, output_folder=output_folder, segment_duration=5)
	
	# 오디오 파일을 5초 단위로 분할하고 멜 스펙트로그램으로 변환하여 저장
	segmenter.process_audio_files()
	print("모든 오디오 파일이 5초 단위로 분할되어 멜 스펙트로그램 이미지로 저장되었습니다.")

if __name__ == '__main__':
	main()
