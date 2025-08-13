from flask import Flask, request, render_template_string
from PIL import Image, ImageDraw, ImageFont
import io, base64, requests, os
from urllib.parse import urljoin

app = Flask(__name__)

# ---- GitHub raw base (adjust branch if needed) ----
RAW_BASE = "https://raw.githubusercontent.com/priscilliababe/Track/main/"

# ---- Try to fetch a font from the repo; fallback to PIL default ----
CANDIDATE_FONTS = [
    "Roboto-Regular.ttf", "Roboto-Bold.ttf", "Inter-Regular.ttf", "Arial.ttf"
]

def fetch_bytes(url: str) -> bytes:
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    return r.content

def get_font(size: int) -> ImageFont.FreeTypeFont:
    for fname in CANDIDATE_FONTS:
        try:
            font_bytes = fetch_bytes(urljoin(RAW_BASE, fname))
            return ImageFont.truetype(io.BytesIO(font_bytes), size)
        except Exception:
            continue
    # fallback
    return ImageFont.load_default()

# ---- Image layout (same coordinates/colors as you used) ----
IMAGES = [
    {"number": 1,  "file": "1.jpg",  "font_size": 115, "color": (255,255,255), "position": (300, 1060)},
    {"number": 2,  "file": "2.jpg",  "font_size": 115, "color": (255,255,255), "position": (300, 1080)},
    {"number": 3,  "file": "3.jpg",  "font_size": 85,  "color": (255,255,255), "position": (300, 1110)},
    {"number": 4,  "file": "4.jpg",  "font_size": 115, "color": (0,0,0),       "position": (260, 860)},
    {"number": 5,  "file": "5.jpg",  "font_size": 80,  "color": (255,255,255), "position": (100, 1132)},
    {"number": 6,  "file": "6.jpg",  "font_size": 115, "color": (255,255,255), "position": (200, 1052)},
    {"number": 7,  "file": "7.jpg",  "font_size": 100, "color": (0,0,0),       "position": (260, 910)},
    {"number": 8,  "file": "8.jpg",  "font_size": 80,  "color": (255,255,255), "position": (180, 1010)},
    {"number": 9,  "file": "9.jpg",  "font_size": 75,  "color": (0,0,0),       "position": (510, 535)},
    {"number": 10, "file": "10.jpg", "font_size": 75,  "color": (0,0,0),       "position": (350, 660)},
    {"number": 11, "file": "11.jpg", "font_size": 75,  "color": (0,0,0),       "position": (650, 400)},
    {"number": 12, "file": "12.jpg", "font_size": 115, "color": (255,255,255), "position": (230, 880)},
]

# ---- HTML templates (inline; page 1 = form, page 2 = gallery) ----
HOME_HTML = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>🏮 Print Phone Number 🏮</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{
  --lantern:#ff4d2d; --peach:#ffe4b5; --cream:#fff7f0; --amber:#ffa500; --leaf:#32cd32;
}
*{box-sizing:border-box}
body{
  margin:0; font-family:system-ui, -apple-system, Arial, sans-serif;
  min-height:100dvh; display:grid; place-items:center;
  background: radial-gradient(1200px 600px at 50% -20%, #ffd6c9 0, #ffeede 30%, var(--cream) 60%, #fff 100%);
}
.card{
  width:min(92vw,420px); background:rgba(255,228,181,.9);
  border-radius:28px; padding:28px; box-shadow:0 16px 40px rgba(0,0,0,.15);
  border:2px solid rgba(255,77,45,.15); backdrop-filter:blur(4px);
}
h1{
  margin:0 0 12px; font-weight:800; letter-spacing:.3px; color:#ff4500; text-align:center;
}
h1::before{content:"🏮"; margin-right:.35em; filter:drop-shadow(0 2px 2px rgba(0,0,0,.2))}
p{margin:0 0 18px; color:#a64500; text-align:center}
label{display:block; font-weight:600; margin:10px 0 6px; color:#a03a00}
input[type=text]{
  width:100%; padding:14px 16px; border-radius:14px; border:2px solid var(--amber);
  font-size:16px; outline:none; background:#fffefb;
}
input[type=text]:focus{border-color:#ff4500; box-shadow:0 0 0 4px rgba(255,77,45,.15)}
button{
  margin-top:16px; width:100%; padding:14px 18px; border:0; border-radius:16px;
  background:linear-gradient(180deg, #ff7a59, #ff4d2d); color:#fff; font-weight:800;
  letter-spacing:.3px; cursor:pointer; transition:transform .06s ease;
  box-shadow:0 10px 20px rgba(255,77,45,.35), inset 0 1px 0 rgba(255,255,255,.35);
}
button:hover{transform:translateY(-1px)}
button:active{transform:translateY(0)}
.footer{margin-top:14px; text-align:center; color:#ff6347}
.footer::after{content:"  🏮"; filter:drop-shadow(0 2px 2px rgba(0,0,0,.2))}
</style>
</head>
<body>
  <form class="card" method="post" action="/generate">
    <h1>Print Phone Number</h1>
    <p>Enter a number and I’ll place it on all images.</p>
    <label for="phone">Phone number</label>
    <input id="phone" name="phone" type="text" placeholder="+1234567890" required>
    <button type="submit">Generate Images</button>
    <div class="footer">Beautifully lit with lantern vibes</div>
  </form>
</body>
</html>
"""

GALLERY_HTML = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>🏮 Your Images 🏮</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{ --lantern:#ff4d2d; --peach:#ffe4b5; --cream:#fff7f0; --leaf:#32cd32; }
*{box-sizing:border-box}
body{margin:0; font-family:system-ui, -apple-system, Arial, sans-serif; background:var(--cream)}
header{
  position:sticky; top:0; z-index:2; background:rgba(255,228,181,.95); backdrop-filter:blur(6px);
  padding:14px 18px; display:flex; align-items:center; justify-content:space-between;
  border-bottom:1px solid rgba(255,77,45,.15)
}
.title{font-weight:900; color:#ff4500; letter-spacing:.3px}
.title::before{content:"🏮"; margin-right:.35em}
.back{
  text-decoration:none; padding:10px 14px; border-radius:12px; background:#ff7a59; color:#fff; font-weight:700;
  box-shadow:0 6px 14px rgba(255,77,45,.25);
}
.grid{
  padding:18px; display:grid; gap:16px;
  grid-template-columns:repeat(auto-fill, minmax(220px, 1fr));
}
.card{
  background:#fff; border-radius:18px; overflow:hidden; box-shadow:0 10px 24px rgba(0,0,0,.12);
  border:1px solid rgba(255,77,45,.12); display:flex; flex-direction:column;
}
.card img{display:block; width:100%; height:auto}
.actions{padding:12px; display:flex; gap:10px}
.download{
  flex:1; text-align:center; text-decoration:none; padding:12px 10px; border-radius:12px; font-weight:800;
  background:linear-gradient(180deg, #39d239, #2eb82e); color:#fff; box-shadow:0 8px 18px rgba(46,184,46,.28);
}
footer{padding:24px; text-align:center; color:#ff6347}
footer::after{content:"  🏮"; filter:drop-shadow(0 2px 2px rgba(0,0,0,.2))}
</style>
</head>
<body>
<header>
  <div class="title">Your Generated Images</div>
  <a class="back" href="/">Back</a>
</header>

<main class="grid">
  {% for img_b64, num in images %}
  <div class="card">
    <img src="data:image/jpeg;base64,{{ img_b64 }}" alt="image {{num}}">
    <div class="actions">
      <a class="download" href="data:image/jpeg;base64,{{ img_b64 }}" download="image{{num}}.jpg">Download</a>
    </div>
  </div>
  {% endfor %}
</main>

<footer>All set! Tap to download any image.</footer>
</body>
</html>
"""

# ---- Image processing ----
def render_image_with_text(phone: str, spec: dict) -> str:
    # fetch image bytes from GitHub
    img_url = urljoin(RAW_BASE, spec["file"])
    img_bytes = fetch_bytes(img_url)

    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    draw = ImageDraw.Draw(image)
    font = get_font(spec["font_size"])

    x, y = spec["position"]
    # "Bold" effect via small offsets
    for dx, dy in [(0,0),(1,0),(0,1),(1,1)]:
        draw.text((x+dx, y+dy), phone, font=font, fill=spec["color"])

    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=92)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

# ---- Routes ----
@app.get("/")
def home():
    return render_template_string(HOME_HTML)

@app.post("/generate")
def generate():
    phone = request.form.get("phone", "").strip()
    if not phone:
        # simple guard; send back home if empty
        return render_template_string(HOME_HTML)

    images_b64 = []
    for spec in IMAGES:
        try:
            img_b64 = render_image_with_text(phone, spec)
            images_b64.append((img_b64, spec["number"]))
        except Exception as e:
            # If a particular image fails (missing in repo, etc.), skip it gracefully
            print(f"Skip {spec['file']}: {e}")

    return render_template_string(GALLERY_HTML, images=images_b64)

if __name__ == "__main__":
    # For hosting providers, often they set PORT env. Locally, defaults to 5000.
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
