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

def main():
    KEY_PATH = '/Users/yutorse/travel_photos_python/.env/trip-timeline-28131-firebase-adminsdk-u4wq6-6d1ede5eda.json'
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    group_name = "test1"

    images = [
        {
            "gps": { "latitude": 35.0276244, "longitude": 135.7837774 },
            "date": "2023-03-15T02:00:000Z",
            "id": "hogehogehoge",
            "url": "https://firebasestorage.googleapis.com/v0/b/trip-timeline-28131.appspot.com/o/1%2F95A9m-ckz9FICQYAJFvhw?alt=media&token=07281d1c-5e34-41b4-94b3-bb88915bed3b"
        },
        {
            "gps": { "latitude": 35.0276244, "longitude": 135.7837774 },
            "date": "2023-03-15T01:10:000Z",
            "id": "fuga",
            "url": "https://firebasestorage.googleapis.com/v0/b/trip-timeline-28131.appspot.com/o/1%2F95A9m-ckz9FICQYAJFvhw?alt=media&token=07281d1c-5e34-41b4-94b3-bb88915bed3b"
        },
        {
            "gps": { "latitude": 35.0276244, "longitude": 134.7837774 },
            "date": "2023-03-15T02:15:000Z",
            "id": "fuga",
            "url": "https://firebasestorage.googleapis.com/v0/b/trip-timeline-28131.appspot.com/o/1%2F95A9m-ckz9FICQYAJFvhw?alt=media&token=07281d1c-5e34-41b4-94b3-bb88915bed3b"
        },
        {
            "gps": { "latitude": 35.0276244, "longitude": 135.7837774 },
            "date": "2023-03-16T00:00:000Z",
            "id": "fuga",
            "url": "https://firebasestorage.googleapis.com/v0/b/trip-timeline-28131.appspot.com/o/1%2FMiUuvWAwcPZSl8IWa3tpA?alt=media&token=de854312-1b16-4d4b-b900-7a3554e143e0"
        },
        {
            "gps": { "latitude": 35.0276244, "longitude": 135.7837774 },
            "date": "2023-03-17T21:00:000Z",
            "id": "fuga",
            "url": "https://firebasestorage.googleapis.com/v0/b/trip-timeline-28131.appspot.com/o/1%2FgsVD6U0lT7EMM8crgSYi3?alt=media&token=f59a95dc-26b2-421e-a350-07d41d9ebf02"
        }
    ]
    groups = grouping_photos(images)

    for i in range(len(images)):
        db.collection("groups_test").document(f"{group_name}").collection("all_photos").document(f"{i}").set(images[i])

    for i in range(len(groups)):
        for j in range(len(groups[i])):
            db.collection("groups_test").document(f"{group_name}").collection("grouping_photos").document(f"{i}").collection(f"{i}").document(f"{j}").set(groups[i][j])


if __name__ == '__main__':
    main()
