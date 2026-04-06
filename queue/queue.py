import os
import json
import time
import sys

STATE_PATH = "./storage/data/state.json"

async def initialize_queue() -> None:

    # Ensure directory exists
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)

    # Initialize with proper structure
    with open(STATE_PATH, "w") as state:
        json.dump({
            "microsoft": {
                "send_this_minutes": 0,
                "queue": {}
            },
            "sms": {
                "send_this_minutes": 0,
                "queue": {}
            }
        }, state, indent=4)

class queue_utils:
    async def _verify_file():
        if not os.path.exists(STATE_PATH):
            sys.exit(1)

    async def _load():
        try:
            with open(STATE_PATH, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {
                "microsoft": {"send_this_minutes": 0, "queue": {}},
                "sms": {"send_this_minutes": 0, "queue": {}}
            }

    async def _save(data):
        with open(STATE_PATH, "w") as f:
            json.dump(data, f, indent=4)

    async def _next_index(queue: dict) -> str:
        if queue:
            return str(max(map(int, queue.keys())) + 1)
        return "1"

class Microsoft:
    @staticmethod
    async def add_in_queue(to: str, code: int) -> None:
        queue_utils._verify_file()
        data = queue_utils._load()

        queue = data["microsoft"]["queue"]
        idx = queue_utils._next_index(queue)

        queue[idx] = {
            "to": to,
            "code": code,
            "time": int(time.time())
        }

        queue_utils._save(data)

    @staticmethod
    async def remove_in_queue(index: int) -> None:
        queue_utils._verify_file()
        data = queue_utils._load()

        queue = data["microsoft"]["queue"]
        index = str(index)

        if index in queue:
            del queue[index]

        queue_utils._save(data)

class SMS:
    @staticmethod
    async def add_in_queue(to: str, code: int) -> None:
        queue_utils._verify_file()
        data = queue_utils._load()

        queue = data["sms"]["queue"]
        idx = queue_utils._next_index(queue)

        queue[idx] = {
            "to": to,
            "code": code,
            "time": int(time.time())
        }

        queue_utils._save(data)

    @staticmethod
    async def remove_in_queue(index: int) -> None:
        queue_utils._verify_file()
        data = queue_utils._load()

        queue = data["sms"]["queue"]
        index = str(index)

        if index in queue:
            del queue[index]

        queue_utils._save(data)