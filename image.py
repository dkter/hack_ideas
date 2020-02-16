from base64 import b64encode
from io import BytesIO
from typing import List, Tuple
import requests
import random
import re

from PIL import Image, ImageFont, ImageDraw
import numpy as np

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
colours = [
    (0, 0, 0),
    (155, 89, 182),
    (46, 204, 113),
    (230, 126, 34),
    (231, 76, 60),
    (26, 188, 156),
    (44, 62, 80)
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
        searchq = requests.get(f"https://api.flaticon.com/v2/search/icons/priority?q={words[word_index]}",
                               headers=headers)
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


def is_greyscale(image: Image) -> bool:
    width, height = image.size
    for x in range(width):
        for y in range(height):
            r, g, b, a = image.getpixel((x, y))
            if r != g != b:
                return False
    return True


def swap_colour(image: Image) -> tuple:
    new_colour = random.choice(colours)

    data = np.array(image)
    red, green, blue, alpha = data.T

    if random.random() < 0.4:
        background = False
        black_areas = (red <= 10) & (green <= 10) & (blue <= 10)
        data[..., :-1][black_areas.T] = new_colour
    else:
        # coloured background, white text+icon
        background = True
        white_areas = (red >= 245) & (green >= 245) & (blue >= 245)
        data[..., :-1][white_areas.T] = new_colour
        black_areas = (red <= 10) & (green <= 10) & (blue <= 10)
        data[..., :-1][black_areas.T] = (255, 255, 255)

    return Image.fromarray(data), new_colour, background


def gen_logo(name: str) -> Image:
    if len(name) > 20:
        disp_name = ''.join([word[0] for word in name.split()])
    else:
        disp_name = name

    # split the name into words, taking into account camelCase
    words = split_word(name)

    pngurl = get_png(words)
    png = requests.get(pngurl)
    icon = Image.open(BytesIO(png.content)).convert("RGBA")

    colour = (0, 0, 0)
    background = False
    if is_greyscale(icon):
        icon, colour, background = swap_colour(icon)

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
                    ICON_SIZE // 2 - 18)
        icon_pos = (0, 0)

    image = Image.new("RGBA", image_dimensions)
    draw = ImageDraw.Draw(image)
    if background:
        text_fill = (255, 255, 255, 255)
        back_fill = colour + (255,)
    else:
        text_fill = colour + (255,)
        back_fill = (255, 255, 255, 255)
    draw.rectangle((0, 0, image_dimensions[0], image_dimensions[1]),
                    fill=back_fill)
    draw.text(text_pos, disp_name, font=font, fill=text_fill)
    image.paste(icon, icon_pos, icon)


    byteimage = BytesIO()
    image.save(byteimage, format="PNG")
    encoded = b64encode(byteimage.getvalue())
    mime = "image/png"
    uri = "data:%s;base64,%s" % (mime, encoded.decode())

    return uri
