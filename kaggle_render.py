# Kaggle GPU renderer for video-factory.
# Paste this whole file into ONE Kaggle notebook cell (GPU T4 + Internet ON,
# secret GITHUB_TOKEN added) and run. It renders every pending job in jobs/
# and pushes the images to renders/<job id>/.
import os, json, glob, subprocess, torch
from kaggle_secrets import UserSecretsClient

TOKEN = UserSecretsClient().get_secret("GITHUB_TOKEN")
REPO = "mirmuteebali/video-factory"
W = "/kaggle/working/vf"

def sh(c): subprocess.run(c, shell=True, check=True)

sh("pip -q install -U diffusers transformers accelerate safetensors")
if not os.path.exists(W):
    sh(f"git clone --depth 1 https://x-access-token:{TOKEN}@github.com/{REPO} {W}")
else:
    sh(f"git -C {W} pull -q")
sh(f'git -C {W} config user.email "render@kaggle" && git -C {W} config user.name "kaggle-render"')

os.makedirs(f"{W}/jobs", exist_ok=True); os.makedirs(f"{W}/renders", exist_ok=True)
def push(msg):
    subprocess.run(f'git -C {W} add -A && (git -C {W} commit -q -m "{msg}" || true) && git -C {W} pull -q --rebase origin main && git -C {W} push -q origin HEAD:main', shell=True)

# ---------- housekeeping: drop jobs/renders older than 6 days ----------
import datetime, re, shutil
today = datetime.datetime.utcnow().date()
for jp in glob.glob(f"{W}/jobs/*.json"):
    m = re.search(r"-(\d{8})-", os.path.basename(jp))
    if m and (today - datetime.datetime.strptime(m.group(1), "%Y%m%d").date()).days > 6:
        jid = os.path.basename(jp)[:-5]
        os.remove(jp); shutil.rmtree(f"{W}/renders/{jid}", ignore_errors=True)

# ---------- plan new jobs with a small free LLM ----------
PER_DAY = {"cosmic": 2, "levelup": 2, "infinite": 1, "coldcase": 2}
def jobs_of(ch): return sorted(glob.glob(f"{W}/jobs/{ch}-*.json"))
need = {}
for ch, n in PER_DAY.items():
    recent = [j for j in jobs_of(ch) if (today - datetime.datetime.strptime(
        re.search(r"-(\d{8})-", j).group(1), "%Y%m%d").date()).days <= 1]
    need[ch] = max(0, n + 1 - len(recent))
print("plan need:", need)
if any(need.values()):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    LM = "Qwen/Qwen2.5-7B-Instruct"
    try:
        from transformers import BitsAndBytesConfig
        sh("pip -q install -U bitsandbytes")
        tok = AutoTokenizer.from_pretrained(LM)
        lm = AutoModelForCausalLM.from_pretrained(LM, device_map="cuda:0",
             quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16))
    except Exception as e:
        print("7B failed, using 3B:", e)
        LM = "Qwen/Qwen2.5-3B-Instruct"
        tok = AutoTokenizer.from_pretrained(LM)
        lm = AutoModelForCausalLM.from_pretrained(LM, torch_dtype=torch.float16).to("cuda:0")
    def ask(msg):
        text = tok.apply_chat_template([{"role": "user", "content": msg}], add_generation_prompt=True, tokenize=False)
        enc = tok(text, return_tensors="pt").to(lm.device)
        out = lm.generate(**enc, max_new_tokens=2200, do_sample=True, temperature=0.8, top_p=0.9)
        return tok.decode(out[0][enc["input_ids"].shape[1]:], skip_special_tokens=True)
    for ch, k in need.items():
        spec = open(f"{W}/channels/{ch}.md").read()
        used = [json.load(open(j)).get("topic", "") for j in jobs_of(ch)]
        for n in range(k):
            for attempt in range(3):
                txt = ask(f"""You plan short vertical videos for this YouTube channel:\n{spec}\n
Pick ONE new topic: a REAL, well-documented case/fact (no invented stories), fitting the niche above, different from these already planned: {used}.
Then write 26 image prompts, one per shot, in story order (hook shot first), each a rich standalone Stable Diffusion XL prompt in the channel's visual style
(subject, setting, lighting, camera, mood), no text in the image, no real people's faces, no logos.
Reply EXACTLY in this format and nothing else:
TOPIC: <topic in one line>
SHOT 1: <prompt>
SHOT 2: <prompt>
... up to SHOT 26""")
                t = re.search(r"TOPIC:\s*(.+)", txt)
                shots = [m.group(1).strip() for m in re.finditer(r"SHOT\s*\d+\s*:\s*(.+)", txt)]
                if t and len(shots) >= 20: break
            if not t or len(shots) < 20:
                print("plan failed for", ch); continue
            topic = t.group(1).strip(); used.append(topic)
            jid = f"{ch}-{datetime.datetime.utcnow():%Y%m%d-%H%M}-{n}"
            json.dump({"channel": ch, "topic": topic, "youtube_prompts": shots[:16], "long_extra_prompts": shots[16:26],
                       "prompts": shots[:26], "width": 896, "height": 1600, "steps": 36},
                      open(f"{W}/jobs/{jid}.json", "w"), indent=1)
            print("planned", jid, topic); push(f"plan {jid}")
    del lm; import gc; gc.collect(); torch.cuda.empty_cache()
sh(f'git -C {W} add -A && (git -C {W} commit -q -m "plan + cleanup" || true) && git -C {W} pull -q --rebase origin main && git -C {W} push -q origin HEAD:main')

pending = [j for j in sorted(glob.glob(f"{W}/jobs/*.json"))
           if not os.path.exists(f"{W}/renders/{os.path.basename(j)[:-5]}/done")]
print("pending jobs:", [os.path.basename(p) for p in pending])

if pending:
    import gc
    from diffusers import StableDiffusionXLPipeline, AutoencoderKL
    gc.collect(); torch.cuda.empty_cache()
    vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)
    pipe = StableDiffusionXLPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0", vae=vae,
        torch_dtype=torch.float16, variant="fp16", use_safetensors=True).to("cuda")
    for fn in ("enable_tiling", "enable_slicing"):
        try: getattr(pipe.vae, fn)()
        except Exception: pass
    clip = proc = None
    try:
        from transformers import CLIPModel, CLIPProcessor
        clip = CLIPModel.from_pretrained("openai/clip-vit-large-patch14", torch_dtype=torch.float16).to("cuda")
        proc = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
    except Exception as e:
        print("clip unavailable:", e)

    def score(img, text):
        if clip is None: return 0.0
        inp = proc(text=[text[:300]], images=img, return_tensors="pt", padding=True, truncation=True).to("cuda")
        inp["pixel_values"] = inp["pixel_values"].half()
        with torch.no_grad():
            return float(clip(**inp).logits_per_image[0, 0])

    for jp in pending:
        job = json.load(open(jp))
        jid = os.path.basename(jp)[:-5]
        out = f"{W}/renders/{jid}"; os.makedirs(out, exist_ok=True)
        w, h = job.get("width", 896), job.get("height", 1600)
        w, h = max(w, 896), max(h, 1600)
        steps = max(job.get("steps", 36), 36)
        neg = job.get("negative", "blurry, lowres, jpeg artifacts, deformed, watermark, text, signature")
        n_best = len(job.get("youtube_prompts", [])) or len(job["prompts"])
        for i, p in enumerate(job["prompts"]):
            f = f"{out}/{i:02d}.jpg"
            if os.path.exists(f): continue
            tries = 2 if i < n_best else 1
            best, best_s = None, -1e9
            for t in range(tries):
                g = torch.Generator("cuda").manual_seed(1000 * i + t + 7)
                img = pipe(p, negative_prompt=neg, width=w, height=h, generator=g,
                           num_inference_steps=steps, guidance_scale=6.5).images[0]
                sc = score(img, p) if tries > 1 else 0.0
                if sc > best_s: best, best_s = img, sc
            best.save(f, quality=95)
            print(jid, i, "ok", round(best_s, 2))
            torch.cuda.empty_cache()
        open(f"{out}/done", "w").write("ok")
        sh(f'git -C {W} add renders/{jid} && git -C {W} commit -q -m "render {jid}" && git -C {W} pull -q --rebase origin main && git -C {W} push -q origin HEAD:main')
print("finished")
