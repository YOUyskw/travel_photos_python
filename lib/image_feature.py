import torch
import torchvision.transforms as transforms
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
import numpy as np
from PIL import Image
import io, urllib.request
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta

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
    images_data = []
    dates = []
    for image in images:
        date_utc = datetime.fromisoformat(image["createdAt"].isoformat())
        date_jst = date_utc + timedelta(hours=9)
        dates.append(date_jst)
    sort_index = np.argsort(dates)
    images_sorted = [images[i] for i in sort_index]

    for image in images_sorted:
        try:
            img = urllib.request.urlopen(image["downloadUrl"]).read()
            bin_img = io.BytesIO(img)
        except Exception as e:
            print(e)
        images_data.append(Image.open(bin_img))

    wrapped_images = []
    wrapped_urls = set()

    for i in range(len(images_sorted)):
        if i == 0:
            wrapped_images.append(images_sorted[i])
            wrapped_urls.add(images_sorted[i]["downloadUrl"])
        else:
            if not(are_images_similar(images_data[i-1], images_data[i], similarity_th, model)):
                wrapped_images.append(images_sorted[i])
                wrapped_urls.add(images_sorted[i]["downloadUrl"])
    return wrapped_images, wrapped_urls

def main(group_id="2"):
    # Firestore への接続 -----------------
    KEY_PATH = '.env/trip-timeline-28131-firebase-adminsdk-u4wq6-6d1ede5eda.json'
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    # -----------------------------------

    # 写真の読み出し -----------------------
    photos_firestore = db.collection("group").document(f"{group_id}").collection("photo").get()
    grouping_photos_firestore = db.collection("group").document(f"{group_id}").collection("grouping_photo").document("1").collection("1").get()
    photos = []
    photo_id_dict = {}
    urls = set()
    for photo in photos_firestore:
        url = photo.to_dict()["downloadUrl"]
        urls.add(url)
        photo_id_dict[f"{url}"] = photo.id
        photos.append(photo.to_dict())

    # 類似している写真を1つにまとめる
    wrapped_photos, wrapped_urls = wrap_images(photos)

    # 写真の削除 -------------------------
    delete_urls = urls - wrapped_urls
    delete_ids = {photo_id_dict[f"{delete_url}"] for delete_url in delete_urls}
    for delete_url in delete_urls:
        delete_photo_id = photo_id_dict[f"{delete_url}"]
        db.collection("group").document(f"{group_id}").collection("photo").document(f"{delete_photo_id}").delete()
    album_id = 0
    is_delete_not_finished = True
    while(is_delete_not_finished):
        grouping_photos_firestore = db.collection("group").document(f"{group_id}").collection("grouping_photo").document(f"{album_id}").collection(f"{album_id}").get()
        for photo in grouping_photos_firestore:
            id = photo.id
            if id in delete_ids:
                db.collection("group").document(f"{group_id}").collection("grouping_photo").document(f"{album_id}").collection(f"{album_id}").document(f"{id}").delete()
        if grouping_photos_firestore == []: is_delete_not_finished = False
        album_id += 1

    # 写真の書き込み -----------------------
    for photo in wrapped_photos:
        url = photo["downloadUrl"]
        photo_id = photo_id_dict[f"{url}"]
        db.collection("group").document(f"{group_id}").collection("photo").document(f"{photo_id}").set(photo)
    # ------------------------------------


if __name__ == "__main__":
    main()





