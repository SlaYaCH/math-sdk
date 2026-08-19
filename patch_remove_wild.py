import csv, random

random.seed(11)

def strip_w(path):
    with open(path) as f:
        grid = [row for row in csv.reader(f)]
    count = 0
    for row in grid:
        for c in range(len(row)):
            if row[c] == "W":
                row[c] = random.choice(["L1","L2","L3","L4"])
                count += 1
    with open(path, "w", newline="") as f:
        csv.writer(f).writerows(grid)
    return count

for name in ["BR0.csv", "FR0.csv", "FR1.csv"]:
    path = f"games/louvo/reels/{name}"
    n = strip_w(path)
    print(f"{name}: {n} W remplaces")
