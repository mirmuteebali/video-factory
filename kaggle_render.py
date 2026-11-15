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
    from diffusers import StableDiffusionXLPipeline
    pipe = StableDiffusionXLPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=torch.float16, variant="fp16", use_safetensors=True).to("cuda")
    pipe.enable_vae_slicing()
    for jp in pending:
        job = json.load(open(jp))
        jid = os.path.basename(jp)[:-5]
        out = f"{W}/renders/{jid}"; os.makedirs(out, exist_ok=True)
        w, h = job.get("width", 832), job.get("height", 1472)
        neg = job.get("negative", "blurry, lowres, jpeg artifacts, deformed, watermark, text, signature")
        for i, p in enumerate(job["prompts"]):
            f = f"{out}/{i:02d}.jpg"
            if os.path.exists(f): continue
            img = pipe(p, negative_prompt=neg, width=w, height=h,
                       num_inference_steps=job.get("steps", 28), guidance_scale=6.5).images[0]
            img.save(f, quality=95)
            print(jid, i, "ok")
        open(f"{out}/done", "w").write("ok")
        sh(f'git -C {W} add renders/{jid} && git -C {W} commit -q -m "render {jid}" && git -C {W} push -q origin HEAD:main')
print("finished")
