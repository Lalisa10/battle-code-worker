import json
import subprocess
import sys
import os
from dotenv import load_dotenv

# ============================================================
# Load environment variables
# ============================================================
load_dotenv()

BOARD_SIZE = int(os.getenv("BOARD_SIZE", "3"))
WIN_CONDITION = int(os.getenv("WIN_CONDITION", "3"))
TIME_LIMIT_MS = int(os.getenv("TIME_LIMIT_MS", "5000"))
REPLAY_DIR = os.getenv("REPLAY_DIR", "./replay")
BASE_SUBMISSION_DIR = os.getenv("BASE_SUBMISSION_DIR")

if WIN_CONDITION > BOARD_SIZE:
    raise ValueError("WIN_CONDITION cannot be greater than BOARD_SIZE")

# ============================================================
# NSJAIL command
# ============================================================
NSJAIL_CMD = [
    "nsjail/nsjail",
    "--config", "tic-tac-toe/game_config.cfg",
    "--",
    "/usr/bin/python3"
]

# ============================================================
# Run bot inside nsjail
# ============================================================
def run_bot(bot_path: str, input_str: str):
    try:
        proc = subprocess.Popen(
            NSJAIL_CMD + [bot_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        try:
            stdout, stderr = proc.communicate(
                input=input_str,
                timeout=TIME_LIMIT_MS / 1000
            )
        except subprocess.TimeoutExpired:
            proc.kill()
            return None, "TIMEOUT"

        if proc.returncode != 0:
            return None, f"CRASH({proc.returncode})"

        return stdout.strip(), None

    except Exception as e:
        return None, f"ERROR: {str(e)}"

# ============================================================
# Game logic helpers
# ============================================================
def valid_move(board, r, c):
    if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
        return False
    return board[r][c] == "."

def check_winner(board):
    directions = [
        (1, 0),   # vertical
        (0, 1),   # horizontal
        (1, 1),   # diagonal
        (1, -1),  # anti-diagonal
    ]

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == ".":
                continue
            player = board[r][c]

            for dr, dc in directions:
                cnt = 0
                rr, cc = r, c
                while (
                    0 <= rr < BOARD_SIZE
                    and 0 <= cc < BOARD_SIZE
                    and board[rr][cc] == player
                ):
                    cnt += 1
                    if cnt == WIN_CONDITION:
                        return 1 if player == "X" else 2
                    rr += dr
                    cc += dc

    # draw?
    if all(board[r][c] != "." for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)):
        return 0

    return None

import requests
import json

def update_match_result(
    backend_base_url: str,
    match_id: int,
    status: str,
    winner_submission_id: int | None,
    events_url: str | None,
    token: str | None = None,
    timeout: int = 10
):
    """
    Send PUT request to backend to update match result.

    :param backend_base_url: e.g. http://localhost:8080
    :param match_id: match id
    :param status: FINISHED / FAILED / RUNNING
    :param winner_submission_id: submission id or None
    :param events_url: replay json path or None
    :param token: optional JWT token
    """

    url = f"{backend_base_url}/api/matches/{match_id}"

    payload = {
        "status": status,
        "winnerSubmissionId": winner_submission_id,
        "eventsUrl": events_url
    }

    headers = {
        "Content-Type": "application/json"
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    resp = requests.put(
        url,
        data=json.dumps(payload),
        headers=headers,
        timeout=timeout
    )
   
    if not resp.ok:
        raise RuntimeError(
            f"Failed to update match {match_id}: "
            f"{resp.status_code} {resp.text}"
        )

    return resp.json() if resp.content else None

# ============================================================
# Main match runner
# ============================================================
def run_match(match_id: str, bot1: str, bot2: str):
    board = [["." for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    moves = []
    turn = 1
    current = 0

    players = [
        {"id": 1, "bot": bot1, "symbol": "X"},
        {"id": 2, "bot": bot2, "symbol": "O"},
    ]

    while True:
        p = players[current]
        
        # build stdin (competitive programming style)
        input_str = ""
        for r in range(BOARD_SIZE):
            input_str += "".join(board[r]) + "\n"
        input_str += p["symbol"] + "\n"

        output, err = run_bot(p["bot"], input_str)
        if err:
            print(err)
            return 3 - p["id"], moves  # opponent wins

        try:
            r, c = map(int, output.split())
        except Exception:
            return 3 - p["id"], moves

        if not valid_move(board, r, c):
            return 3 - p["id"], moves

        board[r][c] = p["symbol"]

        moves.append({
            "turn": turn,
            "player": p["id"],
            "row": r,
            "col": c
        })

        winner = check_winner(board)
        if winner is not None:
            return winner, moves

        current ^= 1
        turn += 1

# ============================================================
# Entry point
# ============================================================
def main():
    if len(sys.argv) != 6:
        print("Usage: python game_controller.py <match_id> <bot1> <bot2> <sub_id1> <sub_id2>")
        sys.exit(1)
    
    match_id = sys.argv[1]
    bot1 = sys.argv[2]
    bot2 = sys.argv[3]
    sub_ids = [sys.argv[4], sys.argv[5]]
    os.makedirs(REPLAY_DIR, exist_ok=True)

    winner, moves = run_match(match_id, bot1, bot2)

    replay = {
        "p1": os.path.basename(bot1),
        "p2": os.path.basename(bot2),
        "board_size": BOARD_SIZE,
        "win_condition": WIN_CONDITION,
        "winner": winner,
        "moves": moves
    }

    replay_path = os.path.join(REPLAY_DIR, f"{match_id}_replay.json")
    with open(replay_path, "w") as f:
        json.dump(replay, f, indent=2)
    
    update_match_result(
        backend_base_url="http://localhost:8080",
        match_id=match_id,
        status="FINISHED",
        winner_submission_id=sub_ids[winner - 1],
        events_url=replay_path
    )

    print(f"[DONE] Match {match_id} finished, replay saved to {replay_path}")

if __name__ == "__main__":
    main()
