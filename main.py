import redis
import subprocess
import time
import json
import os

REDIS_QUEUE = "match_queue"

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def get_file_name(url):
    return url.split('/')[-1]

def run_match(match_id, problem, submissions):
    # set env for game_controller
    # os.environ["BOARD_SIZE"] = str(problem["board_size"])
    # os.environ["WIN_CONDITION"] = str(problem["win_condition"])
    # os.environ["TIME_LIMIT_MS"] = str(problem["time_limit_ms"])

    # prepare bots
    bot_paths = []
    sub_ids = []
    for sub in submissions:
        bot_path = sub['codeUrl']
        bot_paths.append(get_file_name(bot_path))
        sub_ids.append(str(sub['submissionId']))
    #print(bot_paths)
    # example for tic-tac-toe (2 players)
    print("Running command:", "python3", "tic-tac-toe/game_controller.py", str(match_id), bot_paths[0], bot_paths[1], sub_ids[0], sub_ids[1])
    subprocess.run(
        ["python3", "tic-tac-toe/game_controller.py", str(match_id), bot_paths[0], bot_paths[1], sub_ids[0], sub_ids[1]],
        check=True
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
    print(555)
    main()

    # example for tic-tac-toe (2 players)