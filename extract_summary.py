import json

with open('samples/sample_match_boost.json') as f:
    data = json.load(f)

events = data['events']

for i, event in enumerate(events):
    if event.get('type') == 'reveal':
        board = event.get('board', [])
        specials = []
        for reel_idx, reel in enumerate(board):
            for row_idx, sym in enumerate(reel):
                if sym.get('name') in ('M', 'K', 'W') and 'multiplier' in sym:
                    specials.append(f"reel={reel_idx} row={row_idx} {sym['name']} x{sym['multiplier']}")
        if any(s.split()[2].startswith('M') for s in specials):
            print(f"--- reveal #{i} ---")
            for s in specials:
                print(s)
            print(f"totalWin evenement suivant probable: {events[i+1] if i+1 < len(events) else 'aucun'}")
            print()
