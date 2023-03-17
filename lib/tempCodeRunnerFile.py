    for i in range(len(groups)):
        for photo in groups[i]:
            url = photo["downloadUrl"]
            photo_id = photo_id_dict[f"{url}"]
            db.collection("group").document(f"{group_id}").collection("grouping_photo").document(f"{i}").collection(f"{i}").document(f"{photo_id}").set(photo)
