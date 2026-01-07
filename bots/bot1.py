import sys
import random

# =============================
# CONFIG
# =============================
BOARD_SIZE = 30
WIN_CONDITION = 5

# =============================
# READ INPUT
# =============================
board = [list(sys.stdin.readline().strip()) for _ in range(BOARD_SIZE)]
my_symbol = sys.stdin.readline().strip()
opp_symbol = "O" if my_symbol == "X" else "X"

# =============================
# DIRECTIONS
# =============================
DIRECTIONS = [
    (1, 0),   # vertical
    (0, 1),   # horizontal
    (1, 1),   # diag
    (1, -1),  # anti-diag
]

# =============================
# HELPER FUNCTIONS
# =============================
def inside(r, c):
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

def count_line(r, c, dr, dc, symbol):
    """Count consecutive symbol including (r,c)"""
    cnt = 1
    rr, cc = r + dr, c + dc
    while inside(rr, cc) and board[rr][cc] == symbol:
        cnt += 1
        rr += dr
        cc += dc

    rr, cc = r - dr, c - dc
    while inside(rr, cc) and board[rr][cc] == symbol:
        cnt += 1
        rr -= dr
        cc -= dc

    return cnt

def is_winning_move(r, c, symbol):
    board[r][c] = symbol
    for dr, dc in DIRECTIONS:
        if count_line(r, c, dr, dc, symbol) >= WIN_CONDITION:
            board[r][c] = "."
            return True
    board[r][c] = "."
    return False

def score_move(r, c, symbol):
    score = 0
    for dr, dc in DIRECTIONS:
        length = count_line(r, c, dr, dc, symbol)
        if length >= WIN_CONDITION:
            score += 100000
        else:
            score += length * length
    return score

# =============================
# COLLECT CANDIDATES
# =============================
empty_cells = [(r, c) for r in range(BOARD_SIZE)
                        for c in range(BOARD_SIZE)
                        if board[r][c] == "."]

# =============================
# 1. WIN IF POSSIBLE
# =============================
for r, c in empty_cells:
    if is_winning_move(r, c, my_symbol):
        print(r, c)
        sys.exit(0)

# =============================
# 2. BLOCK OPPONENT
# =============================
for r, c in empty_cells:
    if is_winning_move(r, c, opp_symbol):
        print(r, c)
        sys.exit(0)

# =============================
# 3. BEST HEURISTIC MOVE
# =============================
best_score = -1
best_moves = []

center = BOARD_SIZE // 2

for r, c in empty_cells:
    s = score_move(r, c, my_symbol)

    # prefer center slightly
    s -= abs(r - center) + abs(c - center)

    if s > best_score:
        best_score = s
        best_moves = [(r, c)]
    elif s == best_score:
        best_moves.append((r, c))

# =============================
# OUTPUT
# =============================
if best_moves:
    r, c = random.choice(best_moves)
else:
    r, c = random.choice(empty_cells)

print(r, c)
