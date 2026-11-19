import sys
import json, numpy as np, soundfile as sf
import espeakng_loader
from phonemizer.backend.espeak.wrapper import EspeakWrapper
EspeakWrapper.set_library(espeakng_loader.get_library_path()); EspeakWrapper.set_data_path(espeakng_loader.get_data_path())
from kokoro import KPipeline
lines = json.load(open(sys.argv[1] + "/script.json"))
p = KPipeline(lang_code='a')
out = []
for i, l in enumerate(lines):
    a = np.concatenate([np.asarray(r.audio) for r in p(l["say"], voice="am_michael", speed=1.12)])
    nz = np.where(np.abs(a) > 0.01)[0]
    a = a[max(0, nz[0] - 1200): nz[-1] + 2400]
    a = np.concatenate([a, np.zeros(int(24000 * 0.12))])
    sf.write(f"{sys.argv[1]}/v{i}.wav", a, 24000)
    out.append(len(a) / 24000)
json.dump(out, open(sys.argv[1] + "/durs.json", "w"))
print(out, sum(out))
