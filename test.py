from io import BytesIO
from urllib import request

from PIL import Image

res = request.urlopen("https://cdn.icon-icons.com/icons2/844/PNG/512/Google_Chrome_icon-icons.com_67098.png").read()
img = Image.open(BytesIO(res)).resize((16, 16))

for n in range(128, 155):
    img.save(f"assets/Sprites/{n}.png")
