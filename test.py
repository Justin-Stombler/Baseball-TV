# import requests
# from PIL import Image, ImageDraw
# import io

# DEVICE_IP = "192.168.175.78"
# BASE = f"http://{DEVICE_IP}"

# img = Image.new("RGB", (240, 240), color=(20, 20, 20))
# draw = ImageDraw.Draw(img)
# draw.rectangle([20, 90, 220, 150], fill=(223, 70, 1))
# draw.text((60, 108), "HELLO", fill=(255, 255, 255))

# buf = io.BytesIO()
# img.save(buf, format="JPEG", quality=95)
# buf.seek(0)

# # first switch to theme 11
# r = requests.get(BASE + "/set?theme=11", timeout=2)
# print(f"set theme: {r.status_code}")

# # then push the image
# r = requests.post(BASE + "/image", files={"file": ("test.jpg", buf, "image/jpeg")}, timeout=5)
# print(f"push image: {r.status_code}")

import requests
from PIL import Image, ImageDraw
import io

DEVICE_IP = "192.168.178.75"
BASE = f"http://{DEVICE_IP}"

img = Image.new("RGB", (240, 240), color=(20, 20, 20))
draw = ImageDraw.Draw(img)
draw.rectangle([20, 90, 220, 150], fill=(223, 70, 1))
draw.text((60, 108), "HELLO", fill=(255, 255, 255))

buf = io.BytesIO()
img.save(buf, format="JPEG", quality=95)
buf.seek(0)

r = requests.post(
    BASE + "/doUpload?dir=/image/",
    files={"file": ("test.jpg", buf, "image/jpeg")},
    timeout=10
)
print(f"Status: {r.status_code}")
print(f"Body: {r.text}")