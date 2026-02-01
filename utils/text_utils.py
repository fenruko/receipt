import arabic_reshaper
from bidi.algorithm import get_display

def fix_text(text):
    if not text:
        return ""
    try:
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception:
        return text
