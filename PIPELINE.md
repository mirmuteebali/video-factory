# Shorts pipeline (every scheduled Shorts run follows this)

The user approved fully automatic publishing. Every run MUST end with a published video (never skip an upload).
Weekly usage budget is tight: max 2 web searches + 1 search_youtube_videos, no big logs, ONE tiled frame sheet per cut + ONE full-size frame check, short final message.

## 1. Setup (READ-ONLY — never push)
- `git clone --depth 1 https://github.com/mirmuteebali/video-factory /home/claude/vf` (public repo, no login needed). Read channels/<CHANNEL>.md — the channel spec (identity, style, captions, sound, IDs, publish options). Do NOT try to push or add repos.

## 2. Pick a GPU-rendered job (planned + rendered daily by a free Kaggle GPU)
- Candidates: jobs/<CH>-*.json whose renders/<id>/done exists, oldest first.
- Skip a job if its topic was already posted (check Uplika list_channel_posts for this channel: titles/descriptions mentioning the topic), if it is not a REAL well-documented case/fact, or if it is off-niche for the spec. Verify with one web search.
- Use the first good one: images = renders/<id>/NN.jpg (896x1600 SDXL; 00–15 = YouTube-cut shots, 16+ = extra shots for the long cut). Look at ONE tiled contact sheet of them, then WRITE the YouTube and long-cut scripts yourself (spec's viral rules, verified facts) to fit those shots; you may reorder or drop shots that don't fit. Upscale shots with Real-ESRGAN x2 (spandrel, ai-forever/Real-ESRGAN RealESRGAN_x2.pth) → lanczos to 1440x2560 + light unsharp mask. Do NOT generate images locally.

## 3. Fallback (no usable job) — LAST RESORT, quality is much lower; say so in the final message
- Pick your own new topic and make the video fully locally as the spec says (local SD "SimianLuo/LCM_Dreamshaper_v7", CPU float32, 768x1344, 8 steps, guidance 8, safety_checker=None, Real-ESRGAN x2 → 1440x2560).

## 5. Build and publish
- Voice: Kokoro (pip install --break-system-packages torch diffusers transformers accelerate safetensors spandrel soundfile ; pip install --break-system-packages --only-binary=:all: spacy ; pip install --break-system-packages --no-deps kokoro misaki ; pip install --break-system-packages loguru num2words espeakng_loader phonemizer-fork addict regex), KPipeline(lang_code='a'), voice from spec, sentence by sentence, trim silence, word timings by character length; respell hard names; fallback piper en_US-ryan-high.
- MOTION: image always fills the frame (never shows edges or black), smooth eased movement only (no jitter, no shaking), but ALIVE: every shot moves clearly — push-in, pull-out, pan or 2-layer parallax, 10–15% scale change, alternate direction shot to shot; hard cuts on the beat.
- SOUND: clean voice on top + ONE energetic rhythmic music bed made in code for the whole video (driving beat 100–120 BPM with kick + soft hats + bass + chords, matching the channel mood), ~14 dB under the voice, steady volume, 0.5 s fade-in, no random effects, no clipping, normalize ~-14 LUFS.
- Render 1440x2560, 30 fps, libx264 crf 17 preset veryfast, yuv420p, aac 192k, +faststart; draw all text at 1440x2560.
- Upload each cut: media_presign (aiGenerated true) → curl PUT → media_complete. Publish order: YouTube, TikTok, Facebook (as the spec lists), wait: true; confirm YouTube "published", retry once. TikTok/Facebook failures never block YouTube. TikTok: get_publish_options first, privacyLevel PUBLIC_TO_EVERYONE if offered, isAigc true. Facebook: options.facebook {contentType "reel", title}; on identity/reconsent errors call get_help, skip and mention it.
- On errors call Uplika get_help. Finish with a short Roman Urdu SendUserMessage: title, lengths, links, and whether GPU images were used.

## 6. Batch mode (3 Shorts per run)
- If the run prompt says SHORTS_PER_RUN=N, make N different Shorts in this ONE run (different jobs/topics), reusing installs, models and voice pipeline. Do steps 2–5 for each.
- Publish Short 1 immediately (wait: true). For Short k (k ≥ 2) publish the same way but with scheduledAt = now + (k−1)×8 hours (ISO 8601 with offset), so the day gets 3 Shorts 8 hours apart on every target (YouTube, TikTok, Facebook). Never put two of today's Shorts on the same topic.
- If time or a step fails, publish what is ready; never block the first Short. One combined Roman Urdu message at the end.

## 7. ENERGY RULES (override anything slower in the channel spec) — the user says Shorts feel lifeless and stopped going viral
- 0.0–1.5 s: the single most shocking image + 3–6 word HOOK text huge on screen + a first spoken line that is a bold claim or impossible-sounding fact ("This cup changes colour… and it's 1,700 years old."). No intros, no "did you know", no channel name.
- Pace: new shot every 1.2–2 s (reuse a shot with a different crop/move if needed). Every 4–6 s a new twist or bigger number ("But that's not the crazy part…").
- Voice: Kokoro speed 1.12–1.18, short punchy sentences (max ~12 words), questions and "you"; sound excited/intrigued, never flat. Cold Case stays serious but tense and fast, not slow.
- Captions: word-by-word pop (1–3 words at a time, quick scale-in 90%→100% in 0.12 s), big (≥110 px at 1440 wide), key word in the channel colour, placed lower-middle; must stay in sync with the voice.
- Length: YouTube cut 22–35 s (ignore the old A/B 50–60 s option); TikTok/Facebook cut 45–65 s with the same hook. End on a cliffhanger/question that loops into the first line.
- Topic choice: prefer the most jaw-dropping, emotional or "wait, what?" angle; use the one search_youtube_videos call to see which similar Shorts got the most views and steal the ANGLE (never the content).
- Before uploading, watch ONE tiled sheet of frames from the first 3 seconds: if the hook frame is not instantly striking, fix it.

## 8. QUALITY FIRST (the user: "better 1 a day, but it must look HD and be worth watching")
- One Short per channel per day. Spend the effort on it: check every shot in the contact sheet, drop any blurry, deformed, off-topic or repeated image; reorder for the strongest story.
- Final frames must look sharp at full size: upscale with Real-ESRGAN, never stretch a small image; check ONE full-size frame at 1440x2560 before upload.
- Script: research properly (2 web searches), one surprising verified fact per 5 s, no filler words, no generic lines; read it aloud mentally — if it is boring, rewrite it.
- Drop any shot that shows a clear human face (especially in Cold Case: a face can look like a real victim). Use places, objects and evidence instead.
