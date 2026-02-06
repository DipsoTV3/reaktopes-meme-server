from flask import Flask, request, send_file
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import textwrap

app = Flask(__name__)

@app.route("/meme", methods=["POST"])
def meme():
    if "photo" not in request.files:
        return {"error": "no photo"}, 400

    photo = request.files["photo"]
    text = request.form.get("text", "Привет 🐶")
    premium = request.form.get("premium", "0") == "1"

    img = Image.open(photo.stream).convert("RGB")
    W, H = img.size

    bar_h = int(H * 0.22)
    out = Image.new("RGB", (W, H + bar_h), (0, 0, 0))
    out.paste(img, (0, 0))

    draw = ImageDraw.Draw(out)

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", size=int(H * 0.05))
        small = ImageFont.truetype("DejaVuSans.ttf", size=int(H * 0.028))
    except:
        font = ImageFont.load_default()
        small = ImageFont.load_default()

    # --- ТЕКСТ МЕМА ---
    lines = textwrap.wrap(text, width=26)
    y = H + 12

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (W - tw) // 2

        for ox in (-2, -1, 0, 1, 2):
            for oy in (-2, -1, 0, 1, 2):
                draw.text((x + ox, y + oy), line, font=font, fill="black")

        draw.text((x, y), line, font=font, fill="white")
        y += th + 10

    # --- WATERMARK (только если НЕ premium) ---
    if not premium:
        watermark = "🐾 ReaktoPes"
        wb = draw.textbbox((0, 0), watermark, font=small)
        ww, wh = wb[2] - wb[0], wb[3] - wb[1]
        wx = W - ww - 12
        wy = H + bar_h - wh - 10

        draw.text((wx, wy), watermark, font=small, fill=(200, 200, 200))

    bio = BytesIO()
    out.save(bio, "JPEG", quality=95)
    bio.seek(0)

    return send_file(bio, mimetype="image/jpeg")

@app.route("/")
def index():
    return "ReaktoPes meme server is running 🐶"
