from datetime import datetime
import get_exif, reverse_geocoding, image_feature
import numpy as np
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights

model = efficientnet_b0(weights=EfficientNet_B0_Weights.DEFAULT, progress=True)
model.eval()

def grouping_photos(image_paths, distance_th=None, time_th=3600, similarity_th=0.9): # time_th: second
    date_format = "%Y:%m:%d %H:%M:%S"
    dates = []
    date_groups = []

    gps_dict = {}

    # 入力写真のExif情報をなめる ----
    for image_path in image_paths:
        image = get_exif.ExifImage(image_path)
        date_str = image.get_date()
        datetime_object = datetime.strptime(date_str, date_format)
        dates.append(datetime_object)
        gps_str = image.get_gps().split(",")
        gps_dict[image_path] = [gps_str[0], gps_str[1]]
    # --------------------------

    # 時系列ソート処理 ----------
    sort_index = np.argsort(dates)
    dates_sorted = [dates[i] for i in sort_index]
    image_paths_sorted = [image_paths[i] for i in sort_index]
    # ------------------


    # 類似度が高い写真を1つにまとめる
    image_paths_wrapped = []
    for i in range(len(image_paths_sorted)):
        if i == 0:
            image_paths_wrapped.append(image_paths_sorted[i])
        else:
            print(image_feature.get_image_similarity(image_paths_sorted[i-1], image_paths_sorted[i], model))
            if not(image_feature.are_images_similar(image_paths_sorted[i-1], image_paths_sorted[i], similarity_th, model)):
                image_paths_wrapped.append(image_paths_sorted[i])


    # 時系列のグルーピング
    date_group = []
    for i in range(len(image_paths_sorted)):
        if i == 0:
            date_group.append(image_paths_sorted[i])
        else:
            time_diff = (dates_sorted[i] - dates_sorted[i-1]).total_seconds()
            if time_diff <= time_th:
                date_group.append(image_paths_sorted[i])
            else:
                date_groups.append(date_group)
                date_group = []
                date_group.append(image_paths_sorted[i])
    if date_group != []:
        date_groups.append(date_group)

    # 写真が撮られた場所を求める
    locations = []
    for date_group in date_groups:
        latitude, longitude = gps_dict[date_group[0]][0], gps_dict[date_group[0]][1]
        location = reverse_geocoding.get_location(latitude, longitude)
        locations.append(location)

    # 場所のグルーピング
    # TODO

# grouping_photos(["hoge.JPG", "fuga.JPG", "piyo.JPG"])