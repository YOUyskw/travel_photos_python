import torch
import torchvision.transforms as transforms
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
import numpy as np
from PIL import Image

torch.manual_seed(0)

def load_image(image_path):
    image = Image.open(image_path)
    image = image.convert('RGB')
    image = image.resize((224, 224), resample=Image.BILINEAR)
    return image

def preprocess_image(image):
    preprocess = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    return preprocess(image).unsqueeze(0)

def extract_features(image_path, model):
    image = load_image(image_path)
    x = preprocess_image(image)
    with torch.no_grad():
        for name, module in model._modules.items():
            if name == 'classifier': break
            x = module(x)
        features = torch.squeeze(x).numpy()
    return features

def get_image_similarity(image_path1, image_path2, model):
    features1 = extract_features(image_path1, model)
    features2 = extract_features(image_path2, model)
    similarity = np.dot(features1, features2) / (np.linalg.norm(features1) * np.linalg.norm(features2))
    return similarity

def are_images_similar(image_path1, image_path2, threshold, model):
    similarity = get_image_similarity(image_path1, image_path2, model)
    return similarity >= threshold

model = efficientnet_b0(weights=EfficientNet_B0_Weights.DEFAULT, progress=True)
model.eval()

