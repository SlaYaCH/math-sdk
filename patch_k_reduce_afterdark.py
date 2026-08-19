import csv, random

random.seed(7)

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

def reduce_k(grid, target_per_col):
    counts = count_per_column(grid)
    for col in range(5):
        excess = counts[col] - target_per_col
        if excess <= 0:
            continue
        k_positions = [r for r, row in enumerate(grid) if row[col] == "K"]
        random.shuffle(k_positions)
        for r in k_positions[:excess]:
            grid[r][col] = random.choice(["L1","L2","L3","L4"])
    return grid

path = "games/louvo/reels/FR1.csv"
grid = load(path)
before = count_per_column(grid)
grid = reduce_k(grid, 2)
after = count_per_column(grid)
with open(path, "w", newline="") as f:
    csv.writer(f).writerows(grid)
print(f"FR1.csv: avant={before} -> apres={after}")
