from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from config import FONT_PATH, INPUT_IMAGE_PATH


async def create_text_image(
    text: str
) -> BytesIO:
    image = Image.open(INPUT_IMAGE_PATH)
    draw = ImageDraw.Draw(image)

    # Подбор размера шрифта
    font_size = int(image.height * 0.5)
    font = ImageFont.truetype(FONT_PATH, size=font_size)

    # Центрирование текста
    bbox = draw.textbbox((0, 0), text, font=font)
    text_x = (image.width - (bbox[2] - bbox[0])) / 2
    text_y = (image.height - (bbox[3] - bbox[1])) * 0.4

    font_color = (255, 255, 255)
    draw.text((text_x, text_y), text, font=font, fill=font_color)

    # Сохраняем в буфер
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer




# async def create_text_image(
#     text: str
# ) -> BytesIO:
#     image = Image.open(INPUT_IMAGE_PATH).convert("RGB")
#     draw = ImageDraw.Draw(image)

#     # Подбор размера шрифта
#     font_size = int(image.height * 0.5)
#     font = ImageFont.truetype(FONT_PATH, size=font_size)

#     # Центрирование текста
#     bbox = draw.textbbox((0, 0), text, font=font)
#     text_x = (image.width - (bbox[2] - bbox[0])) / 2
#     text_y = (image.height - (bbox[3] - bbox[1])) * 0.4

#     # Определяем средний цвет под областью текста
#     text_area = image.crop((text_x, text_y, text_x + (bbox[2] - bbox[0]), text_y + (bbox[3] - bbox[1])))
#     r, g, b = text_area.resize((1, 1)).getpixel((0, 0))  # усреднённый цвет
#     brightness = (0.299 * r + 0.587 * g + 0.114 * b)

#     # Выбираем цвет текста: если фон тёмный — белый, иначе чёрный
#     if brightness < 128:
#         font_color = (255, 255, 255)
#     else:
#         font_color = (0, 0, 0)

#     draw.text((text_x, text_y), text, font=font, fill=font_color)

#     # Сохраняем в буфер
#     buffer = BytesIO()
#     image.save(buffer, format='PNG')
#     buffer.seek(0)
#     return buffer
