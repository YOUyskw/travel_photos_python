import torch
import torchvision.transforms as transforms
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
import numpy as np
from PIL import Image
import io, urllib.request

torch.manual_seed(0)
model = efficientnet_b0(weights=EfficientNet_B0_Weights.DEFAULT, progress=True)
model.eval()

def load_image(image):
    image = image.convert('RGB')
    image = image.resize((224, 224), resample=Image.BILINEAR)
    return image

def preprocess_image(image):
    preprocess = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    return preprocess(image).unsqueeze(0)

def extract_features(image, model):
    image = load_image(image)
    x = preprocess_image(image)
    with torch.no_grad():
        for name, module in model._modules.items():
            if name == 'classifier': break
            x = module(x)
        features = torch.squeeze(x).numpy()
    return features

def get_image_similarity(image1, image2, model):
    features1 = extract_features(image1, model)
    features2 = extract_features(image2, model)
    similarity = np.dot(features1, features2) / (np.linalg.norm(features1) * np.linalg.norm(features2))
    return similarity

def are_images_similar(image1, image2, threshold, model):
    similarity = get_image_similarity(image1, image2, model)
    return similarity >= threshold

def wrap_images(images, similarity_th=0.9):
    '''
    Parameters: images
    [
        {
            "gps": { "latitude": 34.00, "longitude": 135.00 },
            "date": "2023-03-15T00:00:000Z",
            "id": "hogehogehoge",
            "url": "https://firestore.example.com/dsadsadas"
        },
        {
            "gps": { "latitude": 34.00, "longitude": 135.00 },
            "date": "2023-03-15T00:00:000Z",
            "id": "hogehogehoge",
            "url": "https://firestore.example.com/dsadsadas"
        },
    ]
    '''
    images_data = []
    for image in images:
        try:
            img = urllib.request.urlopen(image["url"]).read()
            bin_img = io.BytesIO(img)
        except Exception as e:
            print(e)
        images_data.append(Image.open(bin_img))

    wrapped_images = []

    for i in range(len(images)):
        if i == 0:
            wrapped_images.append(images[i])
        else:
            if not(are_images_similar(images_data[i-1], images_data[i], similarity_th, model)):
                wrapped_images.append(images[i])
    return wrapped_images

if __name__ == "__main__":
    '''
    images = [
        {
            "gps": { "latitude": 34.00, "longitude": 135.00 },
            "date": "2023-03-15T00:00:000Z",
            "id": "hogehogehoge",
            "url": "https://firebasestorage.googleapis.com/v0/b/trip-timeline-28131.appspot.com/o/1%2F95A9m-ckz9FICQYAJFvhw?alt=media&token=07281d1c-5e34-41b4-94b3-bb88915bed3b"
        },
        {
            "gps": { "latitude": 34.00, "longitude": 135.00 },
            "date": "2023-03-15T00:00:000Z",
            "id": "fuga",
            "url": "https://firebasestorage.googleapis.com/v0/b/trip-timeline-28131.appspot.com/o/1%2F95A9m-ckz9FICQYAJFvhw?alt=media&token=07281d1c-5e34-41b4-94b3-bb88915bed3b"
        },
        {
            "gps": { "latitude": 34.00, "longitude": 135.00 },
            "date": "2023-03-15T00:00:000Z",
            "id": "fuga",
            "url": "https://firebasestorage.googleapis.com/v0/b/trip-timeline-28131.appspot.com/o/1%2FMiUuvWAwcPZSl8IWa3tpA?alt=media&token=de854312-1b16-4d4b-b900-7a3554e143e0"
        },
        {
            "gps": { "latitude": 34.00, "longitude": 135.00 },
            "date": "2023-03-15T00:00:000Z",
            "id": "fuga",
            "url": "https://firebasestorage.googleapis.com/v0/b/trip-timeline-28131.appspot.com/o/1%2FgsVD6U0lT7EMM8crgSYi3?alt=media&token=f59a95dc-26b2-421e-a350-07d41d9ebf02"
        }
    ]
    '''
    wrapped_images = wrap_images(images)




