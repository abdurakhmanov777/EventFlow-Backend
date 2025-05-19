import segno
import io
from typing import Optional
from aiogram.types import BufferedInputFile
from segno import QRCode

async def qr_user(code):
    buffer = await create_qr_bytes(code, dark='darkblue', light='white')
    return BufferedInputFile(buffer.read(), filename='qr.png')

async def create_qr_bytes(
    data: str,
    scale: int = 20,
    dark: str = 'black',
    light: Optional[str] = None,
    border: int = 4,
    file_format: str = 'png'  # Можно: 'png', 'svg', 'pdf'
) -> io.BytesIO:
    '''
    Создаёт QR-код и возвращает его как BytesIO (например, для отправки через Telegram API).

    :param data: Данные для кодирования.
    :param scale: Масштаб изображения.
    :param dark: Цвет тёмных модулей.
    :param light: Цвет фона (если None — прозрачный).
    :param border: Размер отступа вокруг QR-кода.
    :param file_format: Формат изображения: 'png', 'svg', 'pdf'.
    :return: BytesIO-объект с изображением QR-кода.
    '''
    qr: QRCode = segno.make_qr(data)
    buffer = io.BytesIO()
    qr.save(buffer, kind=file_format, scale=scale, dark=dark, light=light, border=border)
    buffer.seek(0)
    return buffer
