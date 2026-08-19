import json

with open('samples/sample_match_boost.json') as f:
    data = json.load(f)

events = data['events']

# trouve le premier evenement "reveal" dont le plateau contient un symbole M
for i, event in enumerate(events):
    if event.get('type') == 'reveal':
        board = event.get('board', [])
        has_m = any(s.get('name') == 'M' for reel in board for s in reel)
        if has_m:
            print(f"=== Evenement reveal trouve (index {i}), contient un M ===")
            print(json.dumps(event, indent=2))
            print(f"\n=== Les 4 evenements suivants (index {i+1} a {i+4}) ===")
            for e in events[i+1:i+5]:
                print(json.dumps(e, indent=2))
            break
else:
    print("Aucun evenement reveal avec M trouve dans ce fichier.")
