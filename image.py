from io import BytesIO
from typing import List
import requests
import random
import re
from base64 import b64encode
from PIL import Image, ImageFont, ImageDraw
from secrets import flaticon_key


fonts = [
    "fonts/razed.ttf",
    "fonts/marons.ttf",
    "fonts/unimate.ttf",
    "fonts/captain.ttf",
    "fonts/bebasneue.ttf",
    "fonts/prototype.ttf",
    "fonts/airstrike.ttf"
]
ICON_SIZE = 128
GENERIC_IMG = f"https://image.flaticon.com/icons/png/{ICON_SIZE}/263/263146.png"


def auth() -> str:
    auth = requests.post("https://api.flaticon.com/v2/app/authentication", {"apikey": flaticon_key})
    token = auth.json()["data"]["token"]
    return token


def get_png(words: List[str]) -> str:
    headers = {"Authorization": "Bearer " + auth()}

    done = False
    word_index = 0
    while not done:
        searchq = requests.get(f"https://api.flaticon.com/v2/search/icons/priority?q={words[word_index]}", headers=headers)
        try:
            pngurl = searchq.json()["data"][0]["images"]["png"][str(ICON_SIZE)]
        except IndexError:
            word_index += 1
            if word_index >= len(words):
                done = True
                pngurl = GENERIC_IMG
        else:
            done = True
    return pngurl


def split_word(word: str) -> List[str]:
    return re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', word)).split()


def gen_logo(name: str) -> Image:
    if len(name) > 20:
        disp_name = ''.join([word[0] for word in name.split()])
    else:
        disp_name = name

    # split the name into words, taking into account camelCase
    words = split_word(name)
    
    pngurl = get_png(words)
    png = requests.get(pngurl)
    icon = Image.open(BytesIO(png.content))

    font = ImageFont.truetype(random.choice(fonts), 36)
    text_width, text_height = font.getsize(disp_name)

    if random.random() < 0.4:
        # layout for the icon above the text
        image_dimensions = (max(ICON_SIZE, text_width),
                            ICON_SIZE + 20 + text_height)
        text_pos = (max(0, image_dimensions[0] // 2 - text_width // 2),
                    138)
        icon_pos = (max(0, image_dimensions[0] // 2 - ICON_SIZE // 2),
                    0)
    else:
        # layout for the icon to the left of the text
        image_dimensions = (ICON_SIZE + 20 + text_width,
                            ICON_SIZE)
        text_pos = (ICON_SIZE + 10,
                    ICON_SIZE // 2-18)
        icon_pos = (0, 0)

    image = Image.new("RGBA", image_dimensions)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, image_dimensions[0], image_dimensions[1]),
                    fill=(255, 255, 255, 255))
    draw.text(text_pos, disp_name, font=font, fill=(0, 0, 0, 255))
    image.paste(icon, icon_pos, icon.convert("RGBA"))

    byteimage = BytesIO()
    image.save(byteimage, format="PNG")
    encoded = b64encode(byteimage.getvalue())
    mime = "image/png"
    uri = "data:%s;base64,%s" % (mime, encoded.decode())

    return uri
