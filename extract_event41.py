import json

with open('samples/sample_match_boost.json') as f:
    data = json.load(f)

events = data['events']
print(json.dumps(events[41], indent=2))
print("--- evenement suivant ---")
print(json.dumps(events[42], indent=2))
