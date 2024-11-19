import SoundProcessModule.SoundDataDivider as sdd
import SoundProcessModule.SoundToImageConverter as stoi
# import SoundProcessModule.SiameseClassifier as siamese
# import SoundProcessModule.dBChecker as dbc
# import UI as tui
import os
import sounddevice as sd
def main():
	print("Welcome To Home Guardian")
	device_id = 1
	record_folder="record"
	if not os.path.exists(record_folder):
		os.mkdir(record_folder)
	divider = sdd.SoundDataDivider(device_id=1, sample_rate=44100, 
								duration=5, interval=6,save_folder=record_folder)
	# print(sd.query_devices())

	converter = stoi.SoundToImageConverter(input_folder=record_folder,output_folder="spectrogram")
	recording=True
	count = 0
	try:
		while recording:
			cur_recordname=divider.record_one(count)
			# print(count)
			# print(cur_recordname)
			# print(os.path.join(record_folder,cur_recordname))
			converter.save_mel_spectrogram(filepath=os.path.join(record_folder,cur_recordname),filename=cur_recordname)
			count+=1

	except KeyboardInterrupt:
		print("Stopped by keyboardinterrupt")
if __name__ == '__main__':
	main()
