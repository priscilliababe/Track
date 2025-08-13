from flask import Flask, render_template_string, request, send_file
from PIL import Image, ImageDraw, ImageFont
import io, os, glob, base64

app = Flask(__name__)

# --- Base directory ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Images and font in the same folder ---
IMAGE_DIR = BASE_DIR
FONT_FILES = glob.glob(os.path.join(BASE_DIR, "*.ttf"))
if not FONT_FILES:
    raise FileNotFoundError("No .ttf font found in the folder.")
FONT_PATH = FONT_FILES[0]

# --- Images configuration ---
IMAGES = [
    {"number": 1, "file": "1.jpg", "font_size": 115, "color": (255, 255, 255), "position": (300, 1060)},
    {"number": 2, "file": "2.jpg", "font_size": 115, "color": (255, 255, 255), "position": (300, 1080)},
    {"number": 3, "file": "3.jpg", "font_size": 85,  "color": (255, 255, 255), "position": (300, 1110)},
    {"number": 4, "file": "4.jpg", "font_size": 115, "color": (0, 0, 0),     "position": (260, 860)},
    {"number": 5, "file": "5.jpg", "font_size": 80,  "color": (255, 255, 255), "position": (100, 1132)},
    {"number": 6, "file": "6.jpg", "font_size": 115, "color": (255, 255, 255), "position": (200, 1052)},
    {"number": 7, "file": "7.jpg", "font_size": 100, "color": (0, 0, 0),      "position": (260, 910)},
    {"number": 8, "file": "8.jpg", "font_size": 80,  "color": (255, 255, 255), "position": (180, 1010)},
    {"number": 9, "file": "9.jpg", "font_size": 75,  "color": (0, 0, 0),      "position": (510, 535)},
    {"number":10,"file": "10.jpg","font_size": 75,  "color": (0, 0, 0),      "position": (350, 660)},
    {"number":11,"file": "11.jpg","font_size": 75,  "color": (0, 0, 0),      "position": (650, 400)},
    {"number":12,"file": "12.jpg","font_size": 115,"color": (255, 255, 255),"position": (230, 880)},
]

# --- Serve background.jpg dynamically ---
@app.route("/background.jpg")
def background():
    return send_file(os.path.join(BASE_DIR, "background.jpg"))

# --- HTML Template ---
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>🏮 Print Phone Number 🏮</title>
<style>
body {
    font-family: 'Arial', sans-serif;
    background-image: url('/background.jpg');
    background-size: 100vw 50vh;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
    text-align: center;
    margin: 0;
    padding: 0;
}
header { background: rgba(255,236,217,0.9); padding: 30px; font-size: 2em; color: #ff4500; }
form {
    margin: 60px auto;
    padding: 40px;
    border-radius: 40px;
    background: rgba(255,228,181,0.9);
    width: 350px;
    box-shadow: 0 8px 16px rgba(0,0,0,0.2);
}
input[type=text] {
    padding: 12px;
    font-size: 1em;
    border-radius: 10px;
    border: 1px solid #ffa500;
    width: 90%;
}
button {
    padding: 12px 20px;
    font-size: 1em;
    border-radius: 12px;
    border: none;
    background: #ff6347;
    color: white;
    cursor: pointer;
    margin-top: 10px;
}
button:hover { background: #ff4500; }
.container {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    margin-top: 20px;
}
.card {
    margin: 15px;
    text-align: center;
    max-width: 250px;
}
img {
    max-width: 100%;
    border-radius: 15px;
    box-shadow: 3px 3px 12px rgba(0,0,0,0.3);
}
.download-btn {
    background: #32cd32;
    color: white;
    text-decoration: none;
    padding: 8px 15px;
    border-radius: 10px;
    margin-top: 8px;
    display: inline-block;
}
.download-btn:hover { background: #228b22; }
footer {
    margin-top: 40px;
    font-size: 1em;
    color: #ff6347;
}
</style>
</head>
<body>
<header>🏮 Print Phone Number on Images 🏮</header>
<form method="post">
<input type="text" name="phone" placeholder="Enter Phone Number" required>
<br>
<button type="submit">Generate Images</button>
</form>
{% if images %}
<div class="container">
{% for img, num in images %}
<div class="card">
<img src="data:image/jpeg;base64,{{ img }}">
<a href="data:image/jpeg;base64,{{ img }}" download="image{{ num }}.jpg" class="download-btn">Download</a>
</div>
{% endfor %}
</div>
<footer>🏮 Designed beautifully for your images 🏮</footer>
{% endif %}
</body>
</html>
"""

# --- Generate images in memory ---
def generate_image(phone_number, img_info):
    img_path = os.path.join(IMAGE_DIR, img_info["file"])
    image = Image.open(img_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(FONT_PATH, img_info["font_size"])
    x, y = img_info["position"]
    for offset in [(0,0),(1,0),(0,1),(1,1)]:
        draw.text((x+offset[0], y+offset[1]), phone_number, font=font, fill=img_info["color"])
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str, img_info["number"]

# --- Flask route ---
@app.route("/", methods=["GET", "POST"])
def index():
    images_data = []
    if request.method == "POST":
        phone = request.form.get("phone")
        if phone:
            for img_info in IMAGES:
                images_data.append(generate_image(phone, img_info))
    return render_template_string(HTML, images=images_data)

if __name__ == "__main__":
    app.run(debug=True, port=5000)