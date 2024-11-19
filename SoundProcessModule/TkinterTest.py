import os
import random
import pandas as pd
from pytubefix import YouTube
from moviepy.editor import AudioFileClip
import csv
class AudioSetDownloader:
	def __init__(self, csv_path, output_folder='fire_alarm_clips', non_fire_alarm_folder='non_fire_alarm'):
		self.csv_path = csv_path
		self.output_folder = output_folder
		self.non_fire_alarm_folder = non_fire_alarm_folder
		self.fire_alarm_label = '/m/01b_21'  # Fire alarm 레이블 ID

		# 저장 폴더 생성
		if not os.path.exists(self.output_folder):
			os.makedirs(self.output_folder)
		if not os.path.exists(self.non_fire_alarm_folder):
			os.makedirs(self.non_fire_alarm_folder)

	def load_data(self):
		# CSV 파일 로드 및 화재 경보 레이블 필터링
		data = pd.read_csv(self.csv_path, quotechar='"', comment='#')
		

		# 결과 출력
		return data

	def download_audio_clip(self, youtube_id, start_time, end_time, output_path):
		url = f'https://www.youtube.com/watch?v={youtube_id}'
		
		try:
			# YouTube 오디오 다운로드
			yt = YouTube(url)
			stream = yt.streams.filter(only_audio=True).first()
			
			if stream is None:
				print(f"No audio stream found for {url}")
				return
			
			audio_file = stream.download(filename='temp_audio.mp4')

			# 특정 구간 오디오 자르기
			audio_clip = AudioFileClip(audio_file).subclip(start_time, end_time)
			audio_clip.write_audiofile(output_path, codec='pcm_s16le')  # WAV로 저장
			
			# 임시 파일 삭제
			audio_clip.close()
			os.remove(audio_file)
			print(f"Downloaded and saved: {output_path}")
		
		except Exception as e:
			print(f"Failed to download {url}: {e}")

	def download_fire_alarm_clips(self):
		# 화재 경보 데이터 로드
		fire_alarm_data, _ = self.load_data()
		
		for _, row in fire_alarm_data.iterrows():
			youtube_id = row['YTID']
			start_time = row['start_seconds']
			end_time = row['end_seconds']
			output_path = os.path.join(self.output_folder, f"{youtube_id}_{start_time}_{end_time}.wav")
			
			# 오디오 클립 다운로드 및 저장
			self.download_audio_clip(youtube_id, start_time, end_time, output_path)

	def download_random_non_fire_alarm_clips(self, num_clips=50):
		# 화재 경보가 아닌 데이터 로드
		non_fire_alarm_data = self.load_data()

		# 50개의 랜덤 샘플 선택
		random_samples = non_fire_alarm_data.sample(n=num_clips, random_state=42)
		
		for _, row in random_samples.iterrows():
			youtube_id = row['YTID']
			start_time = row['start_seconds']
			end_time = row['end_seconds']
			output_path = os.path.join(self.non_fire_alarm_folder, f"{youtube_id}_{start_time}_{end_time}.wav")
			
			# 오디오 클립 다운로드 및 저장
			self.download_audio_clip(youtube_id, start_time, end_time, output_path)

# 실행 예시
def main():
	csv_path = 'balanced_train_segments.csv'  # AudioSet CSV 파일 경로
	downloader = AudioSetDownloader(csv_path=csv_path,output_folder='rand_segments_clips')

	# 화재 경보 데이터를 다운로드합니다.

	# 50개의 랜덤한 non-fire-alarm 데이터를 다운로드합니다.
	downloader.download_random_non_fire_alarm_clips(num_clips=20)


if __name__ == '__main__':
	main()
