import base64
import io
import pyautogui
from astronverse.picker import Rect


def screenshot(rect: Rect):
    """
    截取桌面图片
    """
    if not rect:
        return ""
    if rect.area() == 0:
        return ""
    st = pyautogui.screenshot(region=(rect.left, rect.top, rect.width(), rect.height()))
    img_byte_arr = io.BytesIO()
    st.save(img_byte_arr, format="PNG")
    img_byte_arr = img_byte_arr.getvalue()
    base64_image = base64.b64encode(img_byte_arr).decode("utf-8")
    return base64_image
