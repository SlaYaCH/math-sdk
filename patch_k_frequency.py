import csv, random

random.seed(42)

def load(path):
    with open(path) as f:
        return [row for row in csv.reader(f)]

def count_per_column(grid):
    counts = [0,0,0,0,0]
    for row in grid:
        for c, val in enumerate(row):
            if val == "K":
                counts[c] += 1
    return counts

def top_up_k(grid, target_per_col):
    counts = count_per_column(grid)
    for col in range(5):
        needed = target_per_col - counts[col]
        if needed <= 0:
            continue
        candidates = [r for r, row in enumerate(grid) if row[col] in ("L1","L2","L3","L4")]
        random.shuffle(candidates)
        for r in candidates[:needed]:
            grid[r][col] = "K"
    return grid

for name, target in [("FR0.csv", 2), ("FR1.csv", 3)]:
    path = f"games/louvo/reels/{name}"
    grid = load(path)
    before = count_per_column(grid)
    grid = top_up_k(grid, target)
    after = count_per_column(grid)
    with open(path, "w", newline="") as f:
        csv.writer(f).writerows(grid)
    print(f"{name}: avant={before} -> apres={after}")
