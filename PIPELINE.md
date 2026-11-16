# Shorts pipeline (every scheduled Shorts run follows this)

The user approved fully automatic publishing. Every run MUST end with a published video (never skip an upload).
Weekly usage budget is tight: max 2 web searches + 1 search_youtube_videos, no big logs, ONE tiled frame sheet per cut + ONE full-size frame check, short final message.

## 1. Setup (READ-ONLY — never push)
- `git clone --depth 1 https://github.com/mirmuteebali/video-factory /home/claude/vf` (public repo, no login needed). Read channels/<CHANNEL>.md — the channel spec (identity, style, captions, sound, IDs, publish options). Do NOT try to push or add repos.

## 2. Pick a GPU-rendered job (planned + rendered daily by a free Kaggle GPU)
- Candidates: jobs/<CH>-*.json whose renders/<id>/done exists, oldest first.
- Skip a job if its topic was already posted (check Uplika list_channel_posts for this channel: titles/descriptions mentioning the topic), if it is not a REAL well-documented case/fact, or if it is off-niche for the spec. Verify with one web search.
- Use the first good one: images = renders/<id>/NN.jpg (896x1600 SDXL; 00–15 = YouTube-cut shots, 16+ = extra shots for the long cut). Look at ONE tiled contact sheet of them, then WRITE the YouTube and long-cut scripts yourself (spec's viral rules, verified facts) to fit those shots; you may reorder or drop shots that don't fit. Upscale shots with Real-ESRGAN x2 (spandrel, ai-forever/Real-ESRGAN RealESRGAN_x2.pth) → lanczos to 1440x2560 + light unsharp mask. Do NOT generate images locally.

## 3. Fallback (no usable job)
- Pick your own new topic and make the video fully locally as the spec says (local SD "SimianLuo/LCM_Dreamshaper_v7", CPU float32, 768x1344, 8 steps, guidance 8, safety_checker=None, Real-ESRGAN x2 → 1440x2560).

## 5. Build and publish
- Voice: Kokoro (pip install --break-system-packages torch diffusers transformers accelerate safetensors spandrel soundfile ; pip install --break-system-packages --only-binary=:all: spacy ; pip install --break-system-packages --no-deps kokoro misaki ; pip install --break-system-packages loguru num2words espeakng_loader phonemizer-fork addict regex), KPipeline(lang_code='a'), voice from spec, sentence by sentence, trim silence, word timings by character length; respell hard names; fallback piper en_US-ryan-high.
- MOTION: image always fills the frame; ONE slow smooth eased push-in or pan per shot, max 8% scale change; clean cuts or 0.25 s crossfades; NO zoom punches, bounces or shakes.
- SOUND: NO sound effects at all. Clean voice + one soft continuous music bed made in code (chord pad, low-pass, ~20 dB under voice, 1 s fades); normalize ~-14 LUFS, no clipping, no sudden peaks.
- Render 1440x2560, 30 fps, libx264 crf 17 preset veryfast, yuv420p, aac 192k, +faststart; draw all text at 1440x2560.
- Upload each cut: media_presign (aiGenerated true) → curl PUT → media_complete. Publish order: YouTube, TikTok, Facebook (as the spec lists), wait: true; confirm YouTube "published", retry once. TikTok/Facebook failures never block YouTube. TikTok: get_publish_options first, privacyLevel PUBLIC_TO_EVERYONE if offered, isAigc true. Facebook: options.facebook {contentType "reel", title}; on identity/reconsent errors call get_help, skip and mention it.
- On errors call Uplika get_help. Finish with a short Roman Urdu SendUserMessage: title, lengths, links, and whether GPU images were used.
