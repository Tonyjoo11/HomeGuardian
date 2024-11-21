import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Dataset
from PIL import Image
import numpy as np
from torch.nn.functional import pairwise_distance


class SpectrogramDataset(Dataset):
	def __init__(self, root_dir, transform=None):
		self.root_dir = root_dir
		self.transform = transform
		self.data = []
		self.labels = []

		# fire_alarm과 non_fire_alarm 폴더의 데이터를 로드
		for label, sub_dir in enumerate(['fire_alarm', 'non_fire_alarm']):
			sub_dir_path = os.path.join(root_dir, sub_dir)
			for filename in os.listdir(sub_dir_path):
				file_path = os.path.join(sub_dir_path, filename)
				self.data.append(file_path)
				self.labels.append(label)
		
	def __len__(self):
		return len(self.data)

	def __getitem__(self, idx):
		image_path = self.data[idx]
		label = self.labels[idx]
		image = Image.open(image_path)

		if self.transform:
			image = self.transform(image)

		return image, label

class SiameseNetwork(nn.Module):
	def __init__(self):
		super(SiameseNetwork, self).__init__()
		self.cnn = nn.Sequential(
			nn.Conv2d(1, 64, kernel_size=3, stride=2, padding=1),
			nn.ReLU(),
			nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1),
			nn.ReLU(),
			nn.Conv2d(128, 256, kernel_size=3, stride=2, padding=1),
			nn.ReLU(),
		)
		self.fc = nn.Sequential(
			nn.Linear(256 * 16 * 16, 512),
			nn.ReLU(),
			nn.Linear(512, 256),
		)

	def forward_once(self, x):
		x = self.cnn(x)
		x = x.view(x.size(0), -1)
		x = self.fc(x)
		return x

	def forward(self, input1, input2):
		output1 = self.forward_once(input1)
		output2 = self.forward_once(input2)
		return output1, output2

def contrastive_loss(output1, output2, label, margin=1.0):
	euclidean_distance = pairwise_distance(output1, output2)
	loss = (1 - label) * torch.pow(euclidean_distance, 2) + \
		   label * torch.pow(torch.clamp(margin - euclidean_distance, min=0.0), 2)
	return torch.mean(loss)

class SiameseTrainer:
	def __init__(self, model_path='siamese_model.pth'):
		self.model_path = model_path
		self.model = SiameseNetwork()

		if os.path.exists(self.model_path):
			self.model.load_state_dict(torch.load(self.model_path))
			print(f"SiaClassifi::모델을 '{self.model_path}'에서 불러왔습니다.")
		else:
			print("SiaClassifi::새 모델을 생성합니다.")

	def train_model(self, data_path, epochs=10, batch_size=32, learning_rate=0.001):
		transform = transforms.Compose([
			transforms.Grayscale(num_output_channels=1),
			transforms.Resize((128, 128)),
			transforms.ToTensor()
		])
		
		dataset = SpectrogramDataset(root_dir=data_path, transform=transform)
		dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

		optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)

		for epoch in range(epochs):
			running_loss = 0.0
			for i, (img1, label1) in enumerate(dataloader):
				# Positive/negative pair 생성
				img2, label2 = dataset[np.random.randint(0, len(dataset))]
				
				# img2가 텐서인지 확인하고, 텐서가 아닌 경우에만 transform 적용
				if not isinstance(img2, torch.Tensor):
					img2 = transform(img2)
				
				img2 = img2.unsqueeze(0)  # 배치 차원 추가
				# 레이블이 같으면 0, 다르면 1로 설정
				label = torch.tensor([1.0] if label1[0].item() != label2 else [0.0]).float()
				
				optimizer.zero_grad()
				output1, output2 = self.model(img1, img2)
				loss = contrastive_loss(output1, output2, label)
				loss.backward()
				optimizer.step()
				running_loss += loss.item()

			print(f"SiaClassifi::Epoch [{epoch+1}/{epochs}], Loss: {running_loss / len(dataloader):.4f}")

		torch.save(self.model.state_dict(), self.model_path)
		print("SiaClassifi::Siamese 모델이 저장되었습니다.")

	def predict_similarity(self, image_path, reference_image_path, threshold=0.5):
		transform = transforms.Compose([
			transforms.Grayscale(num_output_channels=1),
			transforms.Resize((128, 128)),
			transforms.ToTensor()
		])
		
		image1 = transform(Image.open(image_path)).unsqueeze(0)
		image2 = transform(Image.open(reference_image_path)).unsqueeze(0)

		with torch.no_grad():
			output1, output2 = self.model(image1, image2)
			distance = pairwise_distance(output1, output2).item()
			isSim=bool()
			if distance < threshold:
				print(f"SiaClassifi::{image_path} 은 유사합니다. 유사도 거리: {distance:.4f}")
				return True
			else:
				print(f"SiaClassifi::{image_path} 은 유사하지 않습니다. 유사도 거리: {distance:.4f}")
				return False
			

# 사용 예시
def main():
	data_path = 'dataset'  # fire_alarm과 non_fire_alarm 폴더가 포함된 경로
	trainer = SiameseTrainer()

	if not os.path.exists(trainer.model_path):
		trainer.train_model(data_path=data_path, epochs=10, batch_size=32, learning_rate=0.001)
	else:
		print("SiaClassifi::저장된 모델을 불러왔습니다.")

	# 유사도 예측 (참고 이미지와 비교)
	for filename in os.listdir("test"):
		trainer.predict_similarity("test/"+filename, "dataset/fire_alarm/reference.png", threshold=0.4)

	

# if __name__ == '__main__':
# 	main()
