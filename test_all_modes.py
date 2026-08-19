import json, hashlib, pickle
from io import TextIOWrapper
from collections import Counter
import zstandard as zst

modes = ["base", "bonus_speed_dating", "bonus_after_dark", "match_boost", "match_frenzy", "like_storm"]

def h(lst):
    return hashlib.md5(pickle.dumps(lst)).hexdigest()

for mode in modes:
    book_path = f"games/louvo/library/publish_files/books_{mode}.jsonl.zst"
    lut_path = f"games/louvo/library/publish_files/lookUpTable_{mode}_0.csv"

    book_payouts = []
    with open(book_path, "rb") as f:
        dctx = zst.ZstdDecompressor()
        with dctx.stream_reader(f) as reader:
            text = TextIOWrapper(reader, encoding="utf-8")
            for line in text:
                line = line.strip()
                if line:
                    book_payouts.append(json.loads(line)["payoutMultiplier"])

    lut_payouts = []
    with open(lut_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                _, weight, payout = line.split(",")
                lut_payouts.append(int(float(payout)))

    match_brut = h(book_payouts) == h(lut_payouts)
    match_multiset = Counter(book_payouts) == Counter(lut_payouts)
    status = "OK" if match_brut and match_multiset else "PROBLEME REEL"
    print(f"{mode:20s} books={len(book_payouts):6d}  lut={len(lut_payouts):6d}  brut={match_brut}  multiset={match_multiset}  -> {status}")
