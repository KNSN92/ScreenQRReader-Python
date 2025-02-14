import subprocess as sp
import tempfile as temp
from os.path import getsize
import typing
import cv2
import numpy as np
# from urllib.parse import urlparse


def capture_screen() -> cv2.typing.MatLike:
    with temp.NamedTemporaryFile(mode="w+", suffix=".png") as t:
        sp.run(["screencapture", "-i", t.name])
        if getsize(t.name) == 0:
            return None
        image = cv2.imread(t.name, cv2.IMREAD_COLOR)
    return image


def read_qrcode(image: cv2.typing.MatLike) -> tuple[typing.Sequence[str], cv2.typing.MatLike]:
    qrd = cv2.QRCodeDetectorAruco()
    _, qrcontents, points, _ = qrd.detectAndDecodeMulti(image)
    return qrcontents, points

def capture_qr():
    image = capture_screen()
    if image is None:
        return None, CaptureQRResponse.STATUS_CANCEL_CAPTURE
    qrcontents, _ = read_qrcode(image)
    if len(qrcontents) >= 1:
        qrcontent = qrcontents[0]
        if len(qrcontent) > 0:
            return qrcontent, CaptureQRResponse.STATUS_SUCCESS
        else:
            return None, CaptureQRResponse.STATUS_INVALID
    else:
        return None, CaptureQRResponse.STATUS_NOT_FOUND

# def is_url(text):
#     text = text.strip()
#     return text.startswith("http://") or text.startswith("https://")

class CaptureQRResponse:
    STATUS_SUCCESS = 0
    STATUS_NOT_FOUND = 1
    STATUS_INVALID = 2
    STATUS_CANCEL_CAPTURE = 3