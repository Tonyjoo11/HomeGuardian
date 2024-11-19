import os
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from PIL import Image

class EnhancedAutoencoder(nn.Module):
	def __init__(self):
		super(EnhancedAutoencoder, self).__init__()
		
		# 인코더
		self.encoder = nn.Sequential(
			nn.Conv2d(1, 64, kernel_size=3, stride=2, padding=1),
			nn.ReLU(),
			nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1),
			nn.ReLU(),
			nn.Conv2d(128, 256, kernel_size=3, stride=2, padding=1),
			nn.ReLU(),
		)
		
		# 디코더
		self.decoder = nn.Sequential(
			nn.ConvTranspose2d(256, 128, kernel_size=3, stride=2, padding=1, output_padding=1),
			nn.ReLU(),
			nn.ConvTranspose2d(128, 64, kernel_size=3, stride=2, padding=1, output_padding=1),
			nn.ReLU(),
			nn.ConvTranspose2d(64, 1, kernel_size=3, stride=2, padding=1, output_padding=1),
			nn.Sigmoid(),
		)

	def forward(self, x):
		encoded = self.encoder(x)
		decoded = self.decoder(encoded)
		return decoded

# SSIM 손실 함수 정의
def ssim_loss(x, y):
	C1, C2 = 0.01 ** 2, 0.03 ** 2
	mu_x = F.avg_pool2d(x, 3, 1, padding=1)
	mu_y = F.avg_pool2d(y, 3, 1, padding=1)
	sigma_x = F.avg_pool2d(x * x, 3, 1, padding=1) - mu_x * mu_x
	sigma_y = F.avg_pool2d(y * y, 3, 1, padding=1) - mu_y * mu_y
	sigma_xy = F.avg_pool2d(x * y, 3, 1, padding=1) - mu_x * mu_y
	SSIM_n = (2 * mu_x * mu_y + C1) * (2 * sigma_xy + C2)
	SSIM_d = (mu_x ** 2 + mu_y ** 2 + C1) * (sigma_x + sigma_y + C2)
	ssim_map = SSIM_n / SSIM_d
	return torch.clamp((1 - ssim_map) / 2, 0, 1).mean()

class SpectrogramClassifier:
	def __init__(self, model_path='fire_alarm_autoencoder.pth'):
		self.model_path = model_path
		self.autoencoder = EnhancedAutoencoder()

		# 모델이 존재하면 로드
		if os.path.exists(self.model_path):
			self.autoencoder.load_state_dict(torch.load(self.model_path))
			print(f"모델을 '{self.model_path}'에서 불러왔습니다.")
		else:
			print(f"새 모델이 생성되었습니다.")

	def train_model(self, data_path, epochs=10, batch_size=32, learning_rate=0.001, fire_alarm_weight=4):
		# 데이터 전처리 및 로드
		transform = transforms.Compose([
			transforms.Grayscale(num_output_channels=1),
			transforms.Resize((128, 128)),
			transforms.ToTensor()
		])
		train_data = datasets.ImageFolder(root=data_path, transform=transform)
		train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True)

		# 옵티마이저 정의
		optimizer = optim.Adam(self.autoencoder.parameters(), lr=learning_rate)

		# 학습 루프
		self.autoencoder.train()
		for epoch in range(epochs):
			running_loss = 0.0
			for images, labels in train_loader:
				optimizer.zero_grad()
				outputs = self.autoencoder(images)
				
				# `fire_alarm` 데이터는 SSIM 손실로 학습하고, `non_fire_alarm`에는 페널티 적용
				is_fire_alarm = (labels == 0)  # fire_alarm 레이블이 0이라고 가정
				fire_loss = ssim_loss(outputs[is_fire_alarm], images[is_fire_alarm]) if is_fire_alarm.any() else 0
				non_fire_loss = (1 - ssim_loss(outputs[~is_fire_alarm], images[~is_fire_alarm])) if (~is_fire_alarm).any() else 0
				
				# `fire_alarm_weight`를 사용해 fire_alarm 손실을 강화하고, non_fire_alarm 손실을 조정
				loss = fire_loss * fire_alarm_weight + non_fire_loss
				loss.backward()
				optimizer.step()
				running_loss += loss.item()

			print(f"Epoch [{epoch+1}/{epochs}], Loss: {running_loss/len(train_loader):.4f}")

		# 학습 완료 후 모델 저장
		torch.save(self.autoencoder.state_dict(), self.model_path)
		print("오토인코더 모델이 저장되었습니다.")

	def predict_similarity(self, image_path, threshold=0.1):
		# 예측을 위한 이미지 로딩 및 전처리
		transform = transforms.Compose([
			transforms.Grayscale(num_output_channels=1),
			transforms.Resize((128, 128)),
			transforms.ToTensor()
		])

		image = Image.open(image_path)
		image = transform(image).unsqueeze(0)  # 배치 차원 추가

		# 모델을 평가 모드로 전환
		self.autoencoder.eval()

		with torch.no_grad():
			output = self.autoencoder(image)
			reconstruction_error = ssim_loss(output, image).item()

			if reconstruction_error < threshold:
				print(f"{image_path} 는 화재 경보 소리와 유사합니다.")
			else:
				print(f"{image_path} 는 화재 경보 소리와 유사하지 않습니다.")
			print(f"재구성 오류: {reconstruction_error:.4f}")


# 사용 예시
def main():
	data_path = 'dataset'  # 화재 경보 소리 이미지 폴더 경로
	classifier = SpectrogramClassifier()

	# 모델이 존재하지 않으면 학습을 시작합니다.
	if not os.path.exists(classifier.model_path):
		classifier.train_model(data_path=data_path, epochs=20, batch_size=128, learning_rate=0.005)
	else:
		print("저장된 모델을 불러왔습니다.")

	# 유사도 예측
	
	for filename in os.listdir("test"):
		classifier.predict_similarity("test/" + filename, threshold=0.1)

# if __name__ == '__main__':
# 	main()

