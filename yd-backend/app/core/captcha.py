"""图形验证码生成与校验。

- 用 Pillow 生成 PNG 字节流
- captcha_id（UUID）作为 key 存到 Redis（key 形如 `captcha:{uuid}`）
- 校验成功后立即删除 key（防重放）
"""
import io
import random
import string
import uuid

from PIL import Image, ImageDraw, ImageFont

_DEFAULT_LEN = 4
_DEFAULT_SIZE = (90, 36)
_DEFAULT_CHARS = string.ascii_uppercase + string.digits  # 去除易混淆 0/O, 1/I/L


def generate_captcha_png(length: int = _DEFAULT_LEN, size: tuple[int, int] = _DEFAULT_SIZE) -> tuple[str, bytes]:
    """生成图形验证码。

    Returns:
        (text, png_bytes)：text 是正确文本（开发/调试用，生产环境不应返回给前端）
    """
    text = "".join(random.choices(_DEFAULT_CHARS, k=length))
    img = Image.new("RGB", size, (250, 250, 250))
    draw = ImageDraw.Draw(img)

    # 字体：尝试加载默认字体（避免 PIL.ImageFont.truetype 在 Windows 缺失字体报错）
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except OSError:
        font = ImageFont.load_default()

    # 字符间距 + 干扰
    w, h = size
    for i, ch in enumerate(text):
        x = 12 + i * 18
        y = 4 + random.randint(-2, 4)
        draw.text((x, y), ch, fill=(60, 60, 60), font=font)

    # 干扰线
    for _ in range(3):
        x1 = random.randint(0, w)
        y1 = random.randint(0, h)
        x2 = random.randint(0, w)
        y2 = random.randint(0, h)
        draw.line([(x1, y1), (x2, y2)], fill=(180, 180, 180), width=1)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return text, buf.getvalue()


def new_captcha_id() -> str:
    """生成 captcha_id（UUID4）。"""
    return uuid.uuid4().hex


__all__ = ["generate_captcha_png", "new_captcha_id"]
