import json, math, subprocess, numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import os
LAND = os.environ.get('LAND') == '1'
W, H, FPS = (1920, 1080, 30) if LAND else (1080, 1920, 30)
TX = 540 if LAND else W / 2
B = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
F = lambda s: ImageFont.truetype(B, s)
import sys, os; os.chdir(sys.argv[1])
lines = json.load(open("script.json")); durs = json.load(open("durs.json"))
DARK = (14, 6, 30)
PAL = [((18, 8, 48), (150, 20, 120)), ((6, 20, 50), (0, 120, 140)), ((30, 6, 50), (200, 40, 120)),
       ((10, 10, 40), (90, 40, 170)), ((20, 6, 30), (220, 80, 40)), ((6, 14, 40), (30, 90, 200)), ((18, 8, 48), (150, 20, 120))]

def grad(a, b):
    g = np.linspace(0, 1, H)[:, None]
    arr = (np.array(a)[None, None] * (1 - g[..., None]) + np.array(b)[None, None] * g[..., None])
    return Image.fromarray(np.repeat(arr, W, 1).astype(np.uint8))

def palm(d, x, base, h, lean, s=1):
    tx, ty = x + lean, base - h
    d.line([(x, base), (tx, ty)], fill=DARK, width=int(30 * s))
    for a in range(0, 360, 40):
        an = math.radians(a); ex, ey = tx + math.cos(an) * 200 * s, ty + math.sin(an) * 80 * s + 50 * s
        d.line([(tx, ty), ((tx + ex) / 2, ty - 25 * s + (ey - ty) / 3), (ex, ey)], fill=DARK, width=int(22 * s), joint="curve")

def neon(img, draw_fn, blur=18):
    g = Image.new("RGB", img.size, 0); draw_fn(ImageDraw.Draw(g))
    img = ImageChops.add(img.convert("RGB"), g.filter(ImageFilter.GaussianBlur(blur)))
    draw_fn(ImageDraw.Draw(img)); return img

def art(kind):
    S = 1000; im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if kind == "sun":
        m = Image.new("L", (S, S), 0); md = ImageDraw.Draw(m); md.ellipse([180, 180, 820, 820], fill=255)
        for i in range(7): y = 560 + i * 40; md.rectangle([0, y, S, y + 6 + i * 4], fill=0)
        sun = Image.new("RGBA", (S, S), (255, 170, 80, 255)); im.paste(sun, (0, 0), m)
        palm(d, 120, 820, 560, 50); palm(d, 880, 820, 480, -60)
    elif kind == "island":
        pts = [(430, 120), (560, 150), (640, 300), (700, 480), (760, 650), (720, 800), (600, 860), (520, 780), (470, 600), (380, 450), (330, 260)]
        d.polygon(pts, fill=(0, 200, 170, 255), outline=(200, 255, 245, 255), width=8)
        for x, y in [(690, 760), (480, 330), (600, 520), (430, 220)]: d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=(255, 60, 200, 255))
        for i, (x, y) in enumerate([(770, 880), (820, 905), (870, 925)]): d.ellipse([x - 18, y - 12, x + 18, y + 12], fill=(0, 200, 170, 255))
    elif kind == "skyline":
        import random; random.seed(3)
        x = 40
        while x < 960:
            w = random.randint(70, 130); h = random.randint(250, 720)
            d.rectangle([x, 900 - h, x + w, 900], fill=(25, 10, 50, 255), outline=(255, 70, 200, 255), width=5)
            for wy in range(900 - h + 30, 880, 50):
                for wx in range(x + 15, x + w - 15, 30):
                    if random.random() < .5: d.rectangle([wx, wy, wx + 12, wy + 20], fill=(0, 230, 255, 255))
            x += w + 12
        d.rectangle([0, 900, S, S], fill=(0, 60, 90, 255))
    elif kind == "regions":
        regs = ["VICE CITY", "LEONIDA KEYS", "GRASSRIVERS", "PORT GELLHORN", "AMBROSIA", "MOUNT KALAGA"]
        cols = [(0, 230, 255), (255, 70, 200), (120, 255, 120), (255, 180, 60), (180, 120, 255), (255, 255, 120)]
        for i, r in enumerate(regs):
            y = 60 + i * 150; c = cols[i]
            d.rounded_rectangle([90, y, 910, y + 120], 30, fill=(20, 10, 45, 230), outline=c + (255,), width=6)
            d.text((500, y + 60), r, font=F(62), fill=c + (255,), anchor="mm")
    elif kind == "size":
        d.rectangle([80, 520, 380, 820], fill=(90, 90, 120, 255)); d.text((230, 670), "GTA 5", font=F(64), fill=(255, 255, 255, 255), anchor="mm")
        d.rectangle([450, 400, 870, 820], fill=(255, 70, 200, 255)); d.text((660, 610), "GTA 6", font=F(90), fill=(255, 255, 255, 255), anchor="mm")
        d.text((500, 920), "~2X AREA", font=F(70), fill=(0, 230, 255, 255), anchor="mm")
    elif kind == "pad":
        d.rounded_rectangle([150, 380, 850, 720], 170, fill=(30, 20, 60, 255), outline=(0, 230, 255, 255), width=10)
        d.ellipse([300, 470, 400, 570], outline=(255, 255, 255, 255), width=10); d.ellipse([600, 520, 700, 620], outline=(255, 255, 255, 255), width=10)
        for dx, dy, c in [(720, 440, (255, 70, 200)), (780, 490, (120, 255, 120)), (660, 490, (0, 230, 255))]: d.ellipse([dx - 25, dy - 25, dx + 25, dy + 25], fill=c + (255,))
        d.text((500, 840), "PS5  |  XBOX SERIES X|S", font=F(58), fill=(255, 255, 255, 255), anchor="mm")
    elif kind == "price":
        for x, y, t, col in [(130, 260, "$79.99", (0, 230, 255)), (470, 520, "$99.99", (255, 70, 200))]:
            d.rounded_rectangle([x, y, x + 400, y + 220], 40, fill=(25, 12, 55, 255), outline=col + (255,), width=10)
            d.ellipse([x + 30, y + 90, x + 70, y + 130], fill=col + (255,)); d.text((x + 230, y + 110), t, font=F(90), fill=(255, 255, 255, 255), anchor="mm")
    elif kind == "box":
        d.rounded_rectangle([280, 150, 720, 780], 30, fill=(30, 14, 60, 255), outline=(255, 70, 200, 255), width=10)
        d.rounded_rectangle([340, 470, 660, 600], 20, fill=(255, 255, 255, 255)); d.text((500, 535), "XXXX-XXXX", font=F(48), fill=(30, 14, 60, 255), anchor="mm")
        d.text((500, 330), "CODE", font=F(110), fill=(0, 230, 255, 255), anchor="mm"); d.text((500, 880), "NO DISC INSIDE", font=F(64), fill=(255, 255, 255, 255), anchor="mm")
    elif kind == "storage":
        d.rounded_rectangle([120, 380, 880, 560], 40, outline=(255, 255, 255, 255), width=10)
        d.rounded_rectangle([140, 400, 700, 540], 30, fill=(255, 70, 200, 255)); d.text((500, 280), "212 GB", font=F(130), fill=(0, 230, 255, 255), anchor="mm")
        d.text((500, 680), "STORAGE NEEDED (PS5)", font=F(54), fill=(255, 255, 255, 255), anchor="mm")
    elif kind == "check":
        for i, t in enumerate(["STANDARD IS FINE", "CLEAR 212 GB", "PS5 / XBOX SERIES"]):
            y = 220 + i * 210
            d.rounded_rectangle([110, y, 890, y + 160], 30, fill=(20, 10, 45, 230), outline=(120, 255, 140, 255), width=6)
            d.line([(160, y + 85), (200, y + 120), (260, y + 45)], fill=(120, 255, 140, 255), width=14)
            d.text((560, y + 80), t, font=F(58), fill=(255, 255, 255, 255), anchor="mm")
    return im

def base(i, l):
    img = grad(*PAL[i % len(PAL)])
    def t(d):
        y = 300 if LAND else 230
        if l["num"]:
            d.ellipse([TX - 80, 120, TX + 80, 280], outline=(0, 240, 255), width=10)
            d.text((TX, 200), l["num"], font=F(110), fill=(0, 240, 255), anchor="mm"); y = 360 if LAND else 330
        d.text((TX, y + 60), l["title"], font=F((112 if len(l["title"]) < 11 else 92) if LAND else (130 if len(l["title"]) < 11 else 112)), fill=(255, 70, 200), anchor="mm")
        d.text((TX, y + 185), l["sub"], font=F(62), fill=(255, 255, 255), anchor="mm")
    return neon(img, t)

def caption_chunks(text, dur):
    words = text.split(); n = sum(len(w) + 1 for w in words); t = 0; out = []
    for i in range(0, len(words), 3):
        ch = words[i:i + 3]; d = sum(len(w) + 1 for w in ch) / n * (dur - 0.22); out.append((t, t + d, " ".join(ch))); t += d
    return out

ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "silent.mp4"], stdin=subprocess.PIPE)
CF = F(72 if LAND else 84)
for i, l in enumerate(lines):
    bg = base(i, l); a = art(l["art"]); dur = durs[i]; n = int(round(dur * FPS))
    caps = caption_chunks(l.get("cap", l["say"]), dur)
    for f in range(n):
        t = f / FPS; k = 1 + 0.10 * (t / dur); s = int((760 if LAND else 860) * k)
        if f < 5: s = int(s * (0.85 + 0.03 * f))  # punch-in
        fr = bg.copy(); ai = a.resize((s, s), Image.BILINEAR); fr.paste(ai, ((1400 - s // 2, 500 - s // 2) if LAND else ((W - s) // 2, 1010 - s // 2)), ai)
        d = ImageDraw.Draw(fr)
        txt = next((c[2] for c in caps if c[0] <= t < c[1]), caps[-1][2]).upper()
        d.text((W / 2, 975 if LAND else 1560), txt, font=CF, fill=(255, 230, 0), anchor="mm", stroke_width=9, stroke_fill=(0, 0, 0))
        if f == int(n / 2) and i in (0, len(lines) // 2): fr.save(f"check{i}.png")
        ff.stdin.write(fr.tobytes())
ff.stdin.close(); ff.wait()

# audio: voice + soft pad
sr = 24000; voice = np.concatenate([sf.read(f"v{i}.wav")[0] for i in range(len(lines))])
tt = np.arange(len(voice)) / sr; pad = np.zeros_like(voice)
chords = [[220, 277.2, 329.6], [196, 246.9, 293.7], [174.6, 220, 261.6], [196, 246.9, 293.7]]
for j, ch in enumerate(chords * 10):
    s0 = int(j * 4 * sr); s1 = min(len(voice), s0 + 4 * sr)
    if s0 >= len(voice): break
    seg = tt[s0:s1]; env = np.minimum(1, np.minimum((seg - seg[0]) / .6, (seg[-1] - seg + 1e-3) / .6))
    pad[s0:s1] += sum(np.sin(2 * np.pi * fq * seg) + .3 * np.sin(4 * np.pi * fq * seg) for fq in ch) * env
pad = pad / np.abs(pad).max() * 0.06
beat = np.zeros_like(voice)
for b in np.arange(0, tt[-1], 0.5):
    s0 = int(b * sr); L = min(2400, len(voice) - s0); e = np.exp(-np.arange(L) / 500)
    beat[s0:s0 + L] += np.sin(2 * np.pi * 55 * np.arange(L) / sr) * e * 0.09
mix = voice / np.abs(voice).max() * 0.85 + pad + beat
fade = np.minimum(1, np.minimum(tt / 0.5, (tt[-1] - tt) / 1.0)); mix = mix * np.clip(fade, 0, 1)
sf.write("mix.wav", mix / max(1, np.abs(mix).max() / 0.95), sr)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "silent.mp4", "-i", "mix.wav", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-af", "loudnorm=I=-14:TP=-1.5", "-shortest", "out.mp4"], check=True)
print("ok")
