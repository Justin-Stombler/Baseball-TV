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
    request_timeout = float(os.environ.get("DEVICE_TIMEOUT", "20"))
    max_retries = int(os.environ.get("UPLOAD_RETRIES", "3"))

    if not DEVICE_IP:
        print("error pushing image: DEVICE_IP is not set")
        return filename

    uploaded = False

    for attempt in range(1, max_retries + 1):
        try:
            r = requests.post(
                f"http://{DEVICE_IP}/doUpload?dir=/image/",
                files={"file": (f"{filename}", image, "image/jpeg")},
                timeout=request_timeout
            )
            print(f"pushed as {filename}: {r.status_code}")
            uploaded = True
            break
        except requests.exceptions.InvalidHeader:
            print(f"uploaded {filename} ok (device returned bad header)")
            uploaded = True
            break
        except requests.exceptions.ReadTimeout as e:
            print(f"timeout pushing {filename} (attempt {attempt}/{max_retries}): {e}")
        except Exception as e:
            print(f"error pushing {filename} (attempt {attempt}/{max_retries}): {e}")

    if not uploaded:
        print(f"giving up on {filename} after {max_retries} attempts")
        return filename

    try:
        requests.get(f"http://{DEVICE_IP}/set?theme=11", timeout=request_timeout)
        requests.get(f"http://{DEVICE_IP}/set?img=/image/{filename}", timeout=request_timeout)
    except Exception as e:
        print(f"uploaded {filename} but failed to switch display: {e}")
    
    return filename

##Second function is to delete the image when desired, as the goal is to keep minimal files on the device at all times
def delete(filename: str = "output.jpg") -> None:

    DEVICE_IP = os.environ.get('DEVICE_IP')

    try:
        r = requests.get(f"http://{DEVICE_IP}/delete?file=/image/{filename}", timeout=10)
        print(f"deleted {filename}: {r.status_code}")
    except Exception as e:
        print(f"error deleting {filename}: {e}")
