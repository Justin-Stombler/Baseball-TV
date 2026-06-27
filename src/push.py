import random
import requests
import io
import os
from dotenv import load_dotenv
from PIL import Image, ImageDraw

load_dotenv()

##First function is to push a rendered image to the device
def push(image: bytes, filename: str = None) -> str:

    if not filename:
        filename = f"{random.randint(10000, 99999)}.jpg"

    DEVICE_IP = os.environ.get('DEVICE_IP')

    try:
        r = requests.post(
            f"http://{DEVICE_IP}/doUpload?dir=/image/",
            files={"file": (f"{filename}", image, "image/jpeg")},
            timeout=10
        )
        print(f"pushed as {filename}: {r.status_code}")

    except requests.exceptions.InvalidHeader:
        print(f"uploaded {filename} ok (device returned bad header)")
    except Exception as e:
        print(f"error pushing {filename}: {e}")

    requests.get(f"http://{DEVICE_IP}/set?theme=11", timeout=10)
    requests.get(f"http://{DEVICE_IP}/set?img=/image/{filename}", timeout=10)
    
    return filename

##Second function is to delete the image when desired, as the goal is to keep minimal files on the device at all times
def delete(filename: str = "output.jpg") -> None:

    DEVICE_IP = os.environ.get('DEVICE_IP')

    try:
        r = requests.get(f"http://{DEVICE_IP}/delete?file=/image/{filename}", timeout=10)
        print(f"deleted {filename}: {r.status_code}")
    except Exception as e:
        print(f"error deleting {filename}: {e}")
