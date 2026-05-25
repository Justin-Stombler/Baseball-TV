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

# after the upload, tell the device to display the file


try:
    r = requests.post(
        f"http://{DEVICE_IP}/doUpload?dir=/image/",
        files={"file": ("test.jpg", buf, "image/jpeg")},
        timeout=10
    )
    print(f"pushed: {r.status_code}")
except requests.exceptions.InvalidHeader:
    print("uploaded ok (device returned bad header)")
except Exception as e:
    print(f"actual error: {e}")