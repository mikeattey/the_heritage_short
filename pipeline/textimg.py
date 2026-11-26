"""Render text to transparent PNGs with Pillow. Used instead of FFmpeg's drawtext/subtitles filters,
which are missing from common builds (Homebrew's FFmpeg 9.1 has neither; see FAILURES.md F4)."""
from PIL import Image, ImageDraw, ImageFont

LATIN = "/System/Library/Fonts/Helvetica.ttc"
ETHIOPIC = "/System/Library/Fonts/Supplemental/KefaIII.ttf"  # Helvetica has no Ethiopic glyphs


def _wrap(draw, text, font, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur); cur = word
    return lines + [cur]


def text_image(text, font_path, size, max_w, fill=(255, 255, 255, 255), stroke=(0, 0, 0, 255), stroke_w=4):
    """Return an RGBA image of centred, wrapped text with an outline."""
    font = ImageFont.truetype(font_path, size)
    lines = _wrap(ImageDraw.Draw(Image.new("RGBA", (1, 1))), text, font, max_w)
    lh = int(size * 1.3)
    pad = stroke_w + 6
    img = Image.new("RGBA", (max_w + 2 * pad, lh * len(lines) + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        tw = d.textlength(line, font=font)
        d.text(((img.width - tw) / 2, pad + i * lh), line, font=font, fill=fill,
               stroke_width=stroke_w, stroke_fill=stroke)
    return img


def subtitle_png(text, path, w, h):
    """English subtitle sized for the frame (16:9 or 9:16)."""
    size = max(34, h // 22) if w > h else max(40, w // 20)
    text_image(text, LATIN, size, int(w * 0.86)).save(path)


def end_card_png(text, subline, path, w, h):
    """Full-frame end card: 'Made with AI' plus the proverb in Amharic script."""
    bg = Image.new("RGB", (w, h), (0, 0, 0))
    big = text_image(text, LATIN, h // 16, int(w * 0.8), stroke_w=0)
    bg.paste(big, ((w - big.width) // 2, h // 2 - big.height - h // 40), big)
    if subline:
        small = text_image(subline, ETHIOPIC, h // 24, int(w * 0.8), fill=(232, 194, 122, 255), stroke_w=0)
        bg.paste(small, ((w - small.width) // 2, h // 2 + h // 40), small)
    bg.save(path)
