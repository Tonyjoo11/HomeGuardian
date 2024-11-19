import SoundProcessModule.SoundDataDivider as sdd
import SoundProcessModule.SoundToImageConverter as stoi
import SoundProcessModule.SiameseClassifier as siamese
import SoundProcessModule.dBChecker as dbc
import UI as tui



def main():
	print("Welcome To Home Guardian")
	device_id = 1
	
	divider = sdd.SoundDataDivider(device_id=1, sample_rate=44100, 
								duration=5, interval=10,save_folder="record")
	try:
		divider.start_recording()
	except KeyboardInterrupt:
		divider.stop_recording()
	
	converter = stoi.SoundToImageConverter()
if __name__ == '__main__':
	main()
