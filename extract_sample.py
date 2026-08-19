import zstandard as zstd
import json

with open('games/louvo/library/publish_files/books_base.jsonl.zst', 'rb') as f:
    decompressor = zstd.ZstdDecompressor()
    with decompressor.stream_reader(f) as reader:
        data = reader.read()

lines = data.decode('utf-8').strip().split('\n')
print(f"Nombre total de simulations dans base : {len(lines)}")

first_sim = json.loads(lines[0])
with open('sample_base_sim.json', 'w') as out:
    json.dump(first_sim, out, indent=2)

print(f"Exemple sauvegardé : sample_base_sim.json (id={first_sim.get('id')}, payoutMultiplier={first_sim.get('payoutMultiplier')})")
