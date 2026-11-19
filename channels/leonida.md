# Leonida Clips (GTA 6 Shorts)
IDs: Uplika workspace ws_61ac39577bb4fa49; YouTube conn_539a72a23acfa68f (@leonidaclips-b9h), categoryId "20" (Gaming), privacyStatus public. YouTube only.

## Rules (hard)
- NEVER use anyone else's footage, clips, screenshots, maps, thumbnails or Rockstar art/logos. Everything is drawn in code (leonida/*.py). Owner's own PS5/Xbox gameplay is the only real footage allowed (only when he sends it).
- Facts must be verified with a web search the same run (confirmed by Rockstar or major outlets). Label leaks/rumours as rumours or skip them.
- Don't repeat a topic: check list_channel_posts for this account first.
- English voice, 20–35 s, punchy hook in the first 2 s.

## Two styles (alternate: map, cards, map, ...)
1. MAP (leonida/mapvid.py): stylised Leonida / GTA 5-style map, camera zoom/pan between regions, coloured labels, one big pop-word caption, beat + whooshes. Example: leonida/example_map.json.
   Per line: say (TTS text; write GTA as "G T A six"), cap (on-screen text), map "L" (Leonida) or "G" (GTA 5 style), ov "red"/"green" (G only), view one of full, vice, ambrosia, gellhorn, kalaga, grass, keys, south, city5; labels to reveal (vice, ambrosia, gellhorn, kalaga, grass, keys, or "all"); hl {word: red|green|cyan|yellow|pink|orange}. Line 0 also needs hook1 (white) and hook2 (red, 1–2 words).
   Good topics: map size, regions, Vice City areas, GTA 5 vs 6 comparisons, where things are.
2. CARDS (leonida/cards.py): neon synthwave cards, number badge, title/sub, code-drawn art, 3-word yellow captions, soft music. Example: leonida/example_cards.json.
   Per line: say, cap, num ("" or "1".."5"), title (<=11 chars best), sub, art one of sun, island, skyline, regions, size, pad.
   Good topics: top-5 facts, characters (Jason & Lucia), features, release/platform info, tips.

## Build
mkdir /home/claude/run && write script.json there, then:
python3 leonida/voice.py /home/claude/run && python3 leonida/<mapvid|cards>.py /home/claude/run  → /home/claude/run/out.mp4
Kokoro install: see PIPELINE.md §5 (needs espeakng_loader; voice.py sets it up). Look at ONE contact sheet of the chk*/check*.png frames before publishing.

## Publish
media_presign (aiGenerated false) → curl PUT → media_complete → publish wait:true, options.youtube {title (<=70 chars, ends "#GTA6 #Shorts"), privacyStatus "public", categoryId "20", tags, defaultLanguage "en"}. Description: 1–2 lines + "Follow Leonida Clips for more GTA 6 Shorts." + #GTA6 #GTAVI #GTA6Shorts #Leonida #ViceCity #Gaming #Shorts.
