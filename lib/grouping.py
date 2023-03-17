from datetime import datetime
import reverse_geocoding
import numpy as np
import firebase_admin
from firebase_admin import credentials, firestore

def grouping_photos(images, distance_th=None, time_th=3600): # time_th: second
    dates = []
    groups = []

    # データの前処理 -----------
    for image in images:
        date_str = image["date"]
        date_str = date_str.replace('Z', '+09:00')
        date = datetime.fromisoformat(date_str)
        dates.append(date)
        latitude, longitude = image["gps"]["latitude"], image["gps"]["longitude"]
        location = reverse_geocoding.get_location(latitude, longitude)
        image["location"] = location
    # -----------------------

    # 時系列ソート処理 ----------
    sort_index = np.argsort(dates)
    dates_sorted = [dates[i] for i in sort_index]
    images_sorted = [images[i] for i in sort_index]
    # ------------------

    # 時系列 & 場所 のグルーピング
    group = []
    for i in range(len(images_sorted)):
        if i == 0:
            group.append(images_sorted[i])
        else:
            time_diff = (dates_sorted[i] - dates_sorted[i-1]).total_seconds()
            if time_diff <= time_th and images_sorted[i-1]["location"] == images_sorted[i]["location"]:
                group.append(images_sorted[i])
            else:
                groups.append(group)
                group = []
                group.append(images_sorted[i])
    if group != []:
        groups.append(group)

    return groups

def main(group_id="test1"):
    # Firestore への接続 -----------------
    KEY_PATH = '.env/trip-timeline-28131-firebase-adminsdk-u4wq6-6d1ede5eda.json'
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    # -----------------------------------

    # 写真の読み出し -----------------------
    photos_firestore = db.collection("group").document(f"{group_id}").collection("photo").get()
    photos = []
    for photo in photos_firestore:
        photos.append(photo.to_dict())
    # -----------------------------------

    # 写真のグルーピング
    groups = grouping_photos(photos)

    # 写真の書き込み -----------------------
    for i in range(len(photos)):
        db.collection("group").document(f"{group_id}").collection("photo").document(f"{i}").set(photos[i])

    for i in range(len(groups)):
        for j in range(len(groups[i])):
            db.collection("group").document(f"{group_id}").collection("photo").document(f"{i}").collection(f"{i}").document(f"{j}").set(groups[i][j])
    # ------------------------------------

if __name__ == '__main__':
    main()
    # main(group_id)
