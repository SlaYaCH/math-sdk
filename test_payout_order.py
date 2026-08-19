import json, hashlib, pickle
from io import TextIOWrapper
from collections import Counter
import zstandard as zst

book_path = "games/louvo/library/publish_files/books_base.jsonl.zst"
lut_path = "games/louvo/library/publish_files/lookUpTable_base_0.csv"

book_payouts = []
with open(book_path, "rb") as f:
    dctx = zst.ZstdDecompressor()
    with dctx.stream_reader(f) as reader:
        text = TextIOWrapper(reader, encoding="utf-8")
        for line in text:
            line = line.strip()
            if not line:
                continue
            blob = json.loads(line)
            book_payouts.append(blob["payoutMultiplier"])

lut_payouts = []
with open(lut_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        _, weight, payout = line.split(",")
        lut_payouts.append(int(float(payout)))

print("nb books:", len(book_payouts))
print("nb lut:  ", len(lut_payouts))

def h(lst):
    return hashlib.md5(pickle.dumps(lst)).hexdigest()

print("hash brut books:", h(book_payouts))
print("hash brut lut:  ", h(lut_payouts))
print("match brut ?    ", h(book_payouts) == h(lut_payouts))

sb, sl = sorted(book_payouts), sorted(lut_payouts)
print("hash trie books:", h(sb))
print("hash trie lut:  ", h(sl))
print("match trie ?    ", h(sb) == h(sl))

cb, cl = Counter(book_payouts), Counter(lut_payouts)
print("multisets identiques ?", cb == cl)
if cb != cl:
    print("valeurs seulement dans books:", dict(list((cb - cl).items())[:10]))
    print("valeurs seulement dans lut:  ", dict(list((cl - cb).items())[:10]))
