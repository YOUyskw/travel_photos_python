from datetime import datetime, timedelta
import reverse_geocoding
import numpy as np
import firebase_admin
from firebase_admin import credentials, firestore

def grouping_photos(photos, distance_th=None, time_th=3600): # time_th: second
    dates = []
    groups = []

    # データの前処理 -----------
    for photo in photos:
        date_utc = datetime.fromisoformat(photo["createdAt"].isoformat())
        date_jst = date_utc + timedelta(hours=9)
        dates.append(date_jst)
        latitude, longitude = photo["location"]["latitude"], photo["location"]["longitude"]
        try:
            location_name = reverse_geocoding.get_location(latitude, longitude)
            photo["location_name"] = location_name
        except:
            photo["location_name"] = "位置不明"
    # -----------------------

    # 時系列ソート処理 ----------
    sort_index = np.argsort(dates)
    dates_sorted = [dates[i] for i in sort_index]
    photos_sorted = [photos[i] for i in sort_index]
    # ------------------

    # 時系列 & 場所 のグルーピング
    group = []
    for i in range(len(photos_sorted)):
        if i == 0:
            group.append(photos_sorted[i])
        else:
            time_diff = (dates_sorted[i] - dates_sorted[i-1]).total_seconds()
            if time_diff <= time_th and photos_sorted[i-1]["location_name"] == photos_sorted[i]["location_name"]:
                group.append(photos_sorted[i])
            else:
                groups.append(group)
                group = []
                group.append(photos_sorted[i])
    if group != []:
        groups.append(group)

    return groups

def main(group_id="2"):
    # Firestore への接続 -----------------
    KEY_PATH = '.env/trip-timeline-28131-firebase-adminsdk-u4wq6-6d1ede5eda.json'
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    # -----------------------------------

    # 写真の読み出し -----------------------
    photos_firestore = db.collection("group").document(f"{group_id}").collection("photo").get()
    photos = []
    photo_id_dict = {}
    for photo in photos_firestore:
        url = photo.to_dict()["downloadUrl"]
        photo_id_dict[f"{url}"] = photo.id
        photos.append(photo.to_dict())

    # -----------------------------------

    # 写真のグルーピング
    groups = grouping_photos(photos)

    # 写真の書き込み -----------------------
    for photo in photos:
        url = photo["downloadUrl"]
        photo_id = photo_id_dict[f"{url}"]
        db.collection("group").document(f"{group_id}").collection("photo").document(f"{photo_id}").set(photo)

    for i in range(len(groups)):
        for photo in groups[i]:
            url = photo["downloadUrl"]
            photo_id = photo_id_dict[f"{url}"]
            db.collection("group").document(f"{group_id}").collection("grouping_photo").document(f"{i}").collection(f"{i}").document(f"{photo_id}").set(photo)
    # ------------------------------------

if __name__ == '__main__':
    main()
    # main(group_id)
