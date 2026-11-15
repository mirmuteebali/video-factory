# Shorts pipeline (every scheduled Shorts run follows this)

The user approved fully automatic publishing. Every run MUST end with a published video (never skip an upload).
Weekly usage budget is tight: max 2 web searches + 1 search_youtube_videos, no big logs, ONE tiled frame sheet per cut + ONE full-size frame check, short final message.

## 1. Setup
- Call Claude Code Remote `add_repo` {owner: mirmuteebali, repo: video-factory, access: push}, then clone exactly as it says to /home/claude/vf (depth 1). Read channels/<CHANNEL>.md — it is the channel spec (identity, style, captions, sound, IDs, publish options).
- Git identity: `git -C /home/claude/vf config user.name scheduled-run; git -C /home/claude/vf config user.email run@local`. Push with `git -C /home/claude/vf pull -q --rebase origin main && git -C /home/claude/vf -c push.negotiate=true push -q origin HEAD:main`.

## 2. Use a GPU-rendered job if one is ready
- Ready job = jobs/<CH>-*.json where renders/<id>/done exists and used/<id> does NOT exist. Take the OLDEST.
- If found: use its title, youtube_script, long_script; images are renders/<id>/NN.jpg in prompt order (first len(youtube_prompts) images = YouTube cut shots; the rest are extra shots for the long cut). These are SDXL 832x1472 — upscale with Real-ESRGAN x2 (spandrel, ai-forever/Real-ESRGAN RealESRGAN_x2.pth) then lanczos to 1440x2560 + light unsharp mask. Do NOT generate images locally. Then create used/<id> (one line: date) and push.
- Quickly re-verify the job's key facts with one web search before using it.

## 3. Fallback (no ready job)
- Make the video fully locally exactly as the channel spec says (local SD "SimianLuo/LCM_Dreamshaper_v7", CPU float32, 768x1344, 8 steps, guidance 8, safety_checker=None, Real-ESRGAN x2 → 1440x2560).

## 4. Queue future jobs for the Kaggle GPU (always, after step 2/3)
- Count this channel's jobs without used/<id>. While count < BUFFER (from channel spec), plan ONE new video and write jobs/<CH>-<YYYYMMDD-HHMM>-<n>.json:
  {"channel","topic","title","youtube_script","long_script","youtube_prompts":[...],"long_extra_prompts":[...],"prompts":youtube_prompts+long_extra_prompts,"width":832,"height":1472,"steps":28,"negative":"blurry, lowres, jpeg artifacts, deformed, watermark, text, signature, logo, extra limbs"}
- Topic must not appear in the channel's posts (list_channel_posts), in any jobs/ file, or in the paired channel named in the spec. Scripts follow the spec's viral rules and lengths. youtube_prompts: one rich SDXL prompt per shot (one shot per 2.5–3.5 s of the YouTube cut, typically 9–12); long_extra_prompts: 6–8 more shots. Write prompts in the channel's visual style, detailed (subject, setting, lighting, lens, mood), no text in images, no real people's faces, no logos or copyrighted characters.
- Commit + push. A free Kaggle GPU notebook renders queued jobs once a day.

## 5. Build and publish
- Voice: Kokoro (pip install --break-system-packages torch diffusers transformers accelerate safetensors spandrel soundfile ; pip install --break-system-packages --only-binary=:all: spacy ; pip install --break-system-packages --no-deps kokoro misaki ; pip install --break-system-packages loguru num2words espeakng_loader phonemizer-fork addict regex), KPipeline(lang_code='a'), voice from spec, sentence by sentence, trim silence, word timings by character length; respell hard names; fallback piper en_US-ryan-high.
- MOTION: image always fills the frame; ONE slow smooth eased push-in or pan per shot, max 8% scale change; clean cuts or 0.25 s crossfades; NO zoom punches, bounces or shakes.
- SOUND: NO sound effects at all. Clean voice + one soft continuous music bed made in code (chord pad, low-pass, ~20 dB under voice, 1 s fades); normalize ~-14 LUFS, no clipping, no sudden peaks.
- Render 1440x2560, 30 fps, libx264 crf 17 preset veryfast, yuv420p, aac 192k, +faststart; draw all text at 1440x2560.
- Upload each cut: media_presign (aiGenerated true) → curl PUT → media_complete. Publish order: YouTube, TikTok, Facebook (as the spec lists), wait: true; confirm YouTube "published", retry once. TikTok/Facebook failures never block YouTube. TikTok: get_publish_options first, privacyLevel PUBLIC_TO_EVERYONE if offered, isAigc true. Facebook: options.facebook {contentType "reel", title}; on identity/reconsent errors call get_help, skip and mention it.
- On errors call Uplika get_help. Finish with a short Roman Urdu SendUserMessage: title, lengths, links, and whether GPU images were used.
