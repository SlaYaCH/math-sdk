import zstandard as zstd
import json
import os

modes = ["base", "bonus_speed_dating", "bonus_after_dark", "match_boost", "match_frenzy", "like_storm"]
os.makedirs("samples", exist_ok=True)

for mode in modes:
    path = f"games/louvo/library/publish_files/books_{mode}.jsonl.zst"
    with open(path, 'rb') as f:
        decompressor = zstd.ZstdDecompressor()
        with decompressor.stream_reader(f) as reader:
            data = reader.read()
    lines = data.decode('utf-8').strip().split('\n')
    first_sim = json.loads(lines[0])
    # pour les modes bonus, on cherche si possible une simu avec un vrai gain (pas 0)
    for line in lines[:200]:
        sim = json.loads(line)
        if sim.get('payoutMultiplier', 0) > 0:
            first_sim = sim
            break
    out_path = f"samples/sample_{mode}.json"
    with open(out_path, 'w') as out:
        json.dump(first_sim, out, indent=2)
    print(f"{mode}: {len(lines)} simulations, exemple sauvé dans {out_path} (payoutMultiplier={first_sim.get('payoutMultiplier')})")
