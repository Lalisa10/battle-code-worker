import json
import os
import subprocess
import time

import redis

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

if load_dotenv:
    load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_QUEUE = os.getenv("REDIS_QUEUE", "match_queue")
PYTHON_BIN = os.getenv("PYTHON_BIN", "python3")
GAME_CONTROLLER_PATH = os.getenv("GAME_CONTROLLER_PATH", "tic-tac-toe/game_controller.py")

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def get_file_name(url):
    return url.split('/')[-1]

def build_game_env(problem):
    env = os.environ.copy()
    if "board_size" in problem:
        env["BOARD_SIZE"] = str(problem["board_size"])
    if "win_condition" in problem:
        env["WIN_CONDITION"] = str(problem["win_condition"])
    if "time_limit_ms" in problem:
        env["TIME_LIMIT_MS"] = str(problem["time_limit_ms"])
    return env


def run_match(match_id, problem, submissions):
    game_env = build_game_env(problem)

    # prepare bots
    bot_paths = []
    sub_ids = []
    for sub in submissions:
        bot_path = sub['codeUrl']
        bot_paths.append(get_file_name(bot_path))
        sub_ids.append(str(sub['submissionId']))
    #print(bot_paths)
    # example for tic-tac-toe (2 players)
    print("Running command:", PYTHON_BIN, GAME_CONTROLLER_PATH, str(match_id), bot_paths[0], bot_paths[1], sub_ids[0], sub_ids[1])
    subprocess.run(
        [PYTHON_BIN, GAME_CONTROLLER_PATH, str(match_id), bot_paths[0], bot_paths[1], sub_ids[0], sub_ids[1]],
        check=True,
        env=game_env,
    )


def main():
    print("Worker started, waiting for match...")

    while True:
        _, raw_message = r.brpop(REDIS_QUEUE)

        try:
            message = json.loads(raw_message)
        except json.JSONDecodeError:
            print("[ERROR] Invalid JSON message:", raw_message)
            continue

        match_id = message["matchId"]
        problem = message["problem"]
        submissions = message["submissions"]

        # sort by slot to keep deterministic order
        submissions.sort(key=lambda s: s["slot"])

        print(f"[WORKER] Picked match {match_id} with {len(submissions)} submissions")

        try:
            run_match(
                match_id=match_id,
                problem=problem,
                submissions=submissions
            )
        except Exception as e:
            print(f"[ERROR] Match {match_id} failed:", e)

if __name__ == "__main__":
    main()

    # example for tic-tac-toe (2 players)
