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
