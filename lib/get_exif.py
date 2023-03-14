from PIL import Image
import PIL.ExifTags as ExifTags

# image_path -> io.BytesIO(requests.get(url).content

class ExifImage:
    def __init__(self, image_path):
        self.img = Image.open(image_path)
        dict = self.img._getexif()
        self.exif = {ExifTags.TAGS.get(key, key): dict[key] for key in dict}

    def print(self):
        if self.exif:
            for k, v in self.exif.items():
                print(k, ":", v)
        else:
            print("exif info is not recorded.")

    def __convert(self, v):
        d = float(v[0])
        m = float(v[1])
        s = float(v[2])
        return d + (m / 60.0) + (s / 3600.0)

    def get_gps(self):
        if "GPSInfo" in self.exif:
            gps_tags = self.exif["GPSInfo"]
        else:
            gps_tags = {}
        gps = {}
        if gps_tags:
            for tag in gps_tags:
                gps[ExifTags.GPSTAGS.get(tag, tag)] = gps_tags[tag]
            latitude = self.__convert(gps["GPSLatitude"])
            lat_ref = gps["GPSLatitudeRef"]
            if lat_ref != "N":
                latitude = 0 - latitude
            longitude = self.__convert(gps["GPSLongitude"])
            lon_ref = gps["GPSLongitudeRef"]
            if lon_ref != "E":
                longitude = 0 - longitude
            return '{:.06f}'.format(latitude) + "," + '{:.06f}'.format(longitude)
        else:
            return "gps is not recorded."

    def get_date(self):
        if "DateTimeOriginal" in self.exif:
            return self.exif["DateTimeOriginal"]
