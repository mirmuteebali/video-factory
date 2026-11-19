import json, math, random, subprocess, numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H, FPS = 1080, 1920, 30
CW, CH = 1800, 3200
FB = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
F = lambda s: ImageFont.truetype(FB, s)
import sys, os; os.chdir(sys.argv[1])
lines = json.load(open("script.json")); durs = json.load(open("durs.json"))
random.seed(7); np.random.seed(7)

def blob(cx, cy, rx, ry, n=90, rough=0.08, seed=0):
    r = np.random.RandomState(seed); k = r.randn(6) * rough; ph = r.rand(6) * 6.28
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        m = 1 + sum(k[j] * math.sin((j + 2) * a + ph[j]) for j in range(6))
        pts.append((cx + rx * m * math.cos(a), cy + ry * m * math.sin(a)))
    return pts

# ---------- Leonida (original stylised map) ----------
WATER = (40, 110, 190); SHALLOW = (80, 170, 215); LAND = (196, 226, 140); CITY = (215, 215, 222)
L = Image.new("RGB", (CW, CH), WATER); d = ImageDraw.Draw(L)
isl = blob(900, 1550, 560, 1150, seed=3)
glow = Image.new("RGB", (CW, CH), WATER); ImageDraw.Draw(glow).polygon(isl, fill=SHALLOW)
L = Image.blend(L, glow.filter(ImageFilter.GaussianBlur(60)), 0.9); d = ImageDraw.Draw(L)
d.polygon(isl, fill=LAND)
keys = [(560 + i * 70, 2830 + int(18 * i * i / 2)) for i in range(6)]
for i, (x, y) in enumerate(keys): d.polygon(blob(x, y, 70 - i * 6, 34, seed=10 + i), fill=LAND)
d.polygon(blob(880, 560, 300, 260, seed=5), fill=(150, 200, 110))                 # Kalaga forest
d.polygon(blob(1010, 980, 120, 95, seed=6), fill=SHALLOW)                       # lake
for i in range(25):                                                                # Grassrivers swamp
    x, y = 650 + random.randint(-230, 230), 2250 + random.randint(-220, 220)
    d.ellipse([x - 30, y - 18, x + 30, y + 18], fill=(120, 200, 190))
towns = {"vice": (1220, 2150, 230, 330), "ambrosia": (930, 1250, 140, 110), "gellhorn": (520, 900, 130, 110)}
for k, (x, y, rx, ry) in towns.items():
    bp = blob(x, y, rx, ry, seed=sum(map(ord, k)) % 50); d.polygon(bp, fill=CITY)
    gl = Image.new("RGB", (CW, CH), CITY); gdd = ImageDraw.Draw(gl)
    for gx in range(x - rx - 60, x + rx + 60, 34): gdd.line([(gx, y - ry - 60), (gx, y + ry + 60)], fill=(245, 245, 250), width=4)
    for gy in range(y - ry - 60, y + ry + 60, 34): gdd.line([(x - rx - 60, gy), (x + rx + 60, gy)], fill=(245, 245, 250), width=4)
    bm = Image.new("L", (CW, CH), 0); ImageDraw.Draw(bm).polygon(bp, fill=255); L.paste(gl, (0, 0), bm); d = ImageDraw.Draw(L)
d.polygon(isl, outline=LAND)
road = [(520, 900), (930, 1250), (1220, 2150), (700, 2500), (620, 2800)]
d.line(road, fill=(255, 255, 255), width=10, joint="curve"); d.line([(930, 1250), (880, 560), (520, 900)], fill=(255, 255, 255), width=8, joint="curve")
d.line([(1220, 2150), (1300, 1500), (930, 1250)], fill=(255, 255, 255), width=8, joint="curve")
# re-mask outside island to water so grids don't spill
mask = Image.new("L", (CW, CH), 0); md = ImageDraw.Draw(mask); md.polygon(isl, fill=255)
for i, (x, y) in enumerate(keys): md.polygon(blob(x, y, 70 - i * 6, 34, seed=10 + i), fill=255)
base = Image.blend(Image.new("RGB", (CW, CH), WATER), glow.filter(ImageFilter.GaussianBlur(60)), 0.9)
L = Image.composite(L, base, mask)

# ---------- GTA 5 style (generic dark map) ----------
G = Image.new("RGB", (CW, CH), (60, 66, 72)); gd = ImageDraw.Draw(G)
gis = blob(900, 1500, 600, 1000, seed=21)
gg = Image.new("L", (CW, CH), 0); ImageDraw.Draw(gg).polygon(gis, fill=255)
G.paste((200, 205, 210), (0, 0), gg.filter(ImageFilter.GaussianBlur(45)))
gd.polygon(gis, fill=(28, 28, 32))
gd.polygon(blob(950, 900, 260, 70, seed=22), fill=(200, 205, 210))
for i in range(40):
    x0, y0 = random.randint(500, 1300), random.randint(700, 1900)
    gd.line([(x0, y0), (x0 + random.randint(-300, 300), y0 + random.randint(-300, 300))], fill=(110, 110, 118), width=4)
cityc = (880, 2150, 330, 260)
cx, cy, rx, ry = cityc
_gl = Image.new("RGB", (CW, CH), (28, 28, 32)); _d = ImageDraw.Draw(_gl)
for gx in range(cx - rx, cx + rx, 22): _d.line([(gx, cy - ry), (gx, cy + ry)], fill=(170, 170, 180), width=3)
for gy in range(cy - ry, cy + ry, 22): _d.line([(cx - rx, gy), (cx + rx, gy)], fill=(170, 170, 180), width=3)
_m = Image.new("L", (CW, CH), 0); ImageDraw.Draw(_m).polygon(blob(cx, cy, rx * 0.9, ry * 0.8, seed=30), fill=255)
_m2 = Image.new("L", (CW, CH), 0); ImageDraw.Draw(_m2).polygon(gis, fill=255)
from PIL import ImageChops as _C; G.paste(_gl, (0, 0), _C.multiply(_m, _m2))
gm = Image.new("L", (CW, CH), 0); ImageDraw.Draw(gm).polygon(gis, fill=255)
G = Image.composite(G, Image.new("RGB", (CW, CH), (60, 66, 72)).copy(), gm) if False else G
cm = Image.new("L", (CW, CH), 0); ImageDraw.Draw(cm).ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=255)
cm = cm.filter(ImageFilter.GaussianBlur(40))
Gred = Image.blend(G, Image.new("RGB", (CW, CH), (200, 20, 40)), 0.45)
Ggreen = Image.composite(Image.blend(G, Image.new("RGB", (CW, CH), (40, 230, 90)), 0.5), Gred, cm)

FULL = (900, 1600, 1.0)
VIEWS = {"vice": (1220, 2150, 2.6), "ambrosia": (930, 1250, 2.6), "gellhorn": (520, 900, 2.6), "kalaga": (880, 560, 2.4),
         "south": (700, 2550, 2.0), "city5": (880, 2150, 2.2)}
LABELS = {"vice": ("VICE CITY", (255, 40, 200)), "ambrosia": ("AMBROSIA", (0, 230, 255)), "gellhorn": ("PORT GELLHORN", (255, 230, 0)),
          "kalaga": ("MOUNT KALAGA", (255, 140, 40)), "grass": ("GRASSRIVERS", (120, 255, 140)), "keys": ("THE KEYS", (120, 255, 140))}
LPOS = {"vice": (1220, 2150), "ambrosia": (930, 1250), "gellhorn": (520, 900), "kalaga": (880, 560), "grass": (650, 2250), "keys": (700, 2880)}
COLS = {"red": (255, 40, 40), "green": (60, 255, 110), "cyan": (0, 230, 255), "yellow": (255, 230, 0), "pink": (255, 40, 200), "orange": (255, 140, 40)}
VIEWS["full"] = FULL; VIEWS["grass"] = (650, 2250, 2.4); VIEWS["keys"] = (700, 2880, 2.4)
SEG = []; prev = FULL; seen = []
for l in lines:
    m = l.get("map", "L"); v = VIEWS[l.get("view", "full")]
    if SEG and m != SEG[-1][0]: prev = FULL
    for k in l.get("labels", []): seen = list(LABELS) if k == "all" else seen + ([k] if k not in seen else [])
    v1 = v if v != prev else (v[0], v[1], v[2] * 1.08)
    SEG.append((m, prev, v1, l.get("ov"), list(seen))); prev = v1
ease = lambda t: t * t * (3 - 2 * t)

def frame(src, view):
    x, y, z = view; vw, vh = CW / z, CH / z
    x = min(max(x, vw / 2), CW - vw / 2); y = min(max(y, vh / 2), CH - vh / 2)
    box = (x - vw / 2, y - vh / 2, x + vw / 2, y + vh / 2)
    return src.resize((W, H), Image.BILINEAR, box=box), box

KEYW0 = {"empty.": (255, 40, 40), "barren": (255, 40, 40), "alive.": (60, 255, 110), "leonida.": (0, 230, 255), "twice": (255, 230, 0),
        "vice": (255, 40, 200), "city.": (255, 40, 200), "ambrosia.": (0, 230, 255), "port": (255, 230, 0), "gellhorn.": (255, 230, 0),
        "mount": (255, 140, 40), "kalaga.": (255, 140, 40), "grassrivers,": (120, 255, 140), "keys.": (120, 255, 140), "walk": (0, 230, 255), "follow": (255, 40, 200)}
KEYW = {k.lower(): COLS[c] for l in lines for k, c in l.get("hl", {}).items()}
ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "silent.mp4"], stdin=subprocess.PIPE)
CF, LF, HF = F(110), F(64), F(78)
starts = []; acc = 0
for i, (m, v0, v1, ov, labs) in enumerate(SEG):
    dur = durs[i]; n = int(round(dur * FPS)); starts.append(acc); acc += dur
    words = lines[i]["cap"].split(); tot = sum(len(w) + 1 for w in words); wt = []; t0 = 0
    for w in words: dd = (len(w) + 1) / tot * (dur - 0.12); wt.append((t0, t0 + dd, w)); t0 += dd
    for f in range(n):
        t = f / FPS; k = ease(min(1, t / max(0.5, dur * 0.85)))
        view = tuple(a + (b - a) * k for a, b in zip(v0, v1))
        if m == "L": src = L
        elif ov == "red": src = Image.blend(G, Gred, min(1, t / 1.0))
        else: src = Image.blend(Gred, Ggreen, min(1, t / 0.8))
        fr, box = frame(src, view); d = ImageDraw.Draw(fr)
        sx = W / (box[2] - box[0])
        for key in labs:
            txt, col = LABELS[key]; px, py = LPOS[key]
            X, Y = (px - box[0]) * sx, (py - box[1]) * sx
            if -200 < X < W + 200 and 0 < Y < H:
                d.text((X, Y), txt, font=LF, fill=col, anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0))
        if i == 0:
            d.text((W / 2, 300), lines[0]["hook1"], font=HF, fill="white", anchor="mm", stroke_width=8, stroke_fill="black")
            d.text((W / 2, 400), lines[0]["hook2"], font=F(110), fill=(255, 40, 40), anchor="mm", stroke_width=9, stroke_fill="black")
        w = next((x for x in wt if x[0] <= t < x[1]), wt[-1])
        pop = 1.0 + 0.18 * max(0, 1 - (t - w[0]) / 0.12)
        col = KEYW.get(w[2].lower().strip(".,!?"), (255, 255, 255))
        d.text((W / 2, 1000), w[2].rstrip(".,"), font=F(int(110 * pop)), fill=col, anchor="mm", stroke_width=10, stroke_fill=(0, 0, 0))
        if f == n // 2 and i in (1, len(lines) // 2, len(lines) - 2): fr.save(f"chk{i}.png")
        ff.stdin.write(fr.tobytes())
ff.stdin.close(); ff.wait()

sr = 24000; voice = np.concatenate([sf.read(f"v{i}.wav")[0] for i in range(len(lines))]); tt = np.arange(len(voice)) / sr
pad = np.zeros_like(voice)
for j, ch in enumerate([[220, 261.6, 329.6], [174.6, 220, 261.6], [196, 246.9, 293.7], [164.8, 196, 246.9]] * 10):
    s0 = int(j * 3 * sr); s1 = min(len(voice), s0 + 3 * sr)
    if s0 >= len(voice): break
    seg = tt[s0:s1]; env = np.clip(np.minimum((seg - seg[0]) / .4, (seg[-1] - seg + 1e-3) / .4), 0, 1)
    pad[s0:s1] += sum(np.sin(2 * np.pi * q * seg) for q in ch) * env
pad = pad / np.abs(pad).max() * 0.05
beat = np.zeros_like(voice)
for b in np.arange(0, tt[-1], 0.4):
    s0 = int(b * sr); Lb = min(2400, len(voice) - s0); beat[s0:s0 + Lb] += np.sin(2 * np.pi * 52 * np.arange(Lb) / sr) * np.exp(-np.arange(Lb) / 450) * 0.1
wh = np.zeros_like(voice); rng = np.random.RandomState(1)
for i in range(1, len(lines)):
    s0 = int(starts[i] * sr); Lw = min(int(0.35 * sr), len(voice) - s0)
    nz = np.convolve(rng.randn(Lw), np.ones(30) / 30, "same"); e = np.sin(np.linspace(0, np.pi, Lw)) ** 2
    wh[s0:s0 + Lw] += nz * e * 0.5
mix = voice / np.abs(voice).max() * 0.85 + pad + beat + wh
mix *= np.clip(np.minimum(tt / 0.3, (tt[-1] - tt) / 0.8), 0, 1)
sf.write("mix.wav", mix / max(1, np.abs(mix).max() / 0.95), sr)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "silent.mp4", "-i", "mix.wav", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-af", "loudnorm=I=-14:TP=-1.5", "-shortest", "out.mp4"], check=True)
print("ok")
