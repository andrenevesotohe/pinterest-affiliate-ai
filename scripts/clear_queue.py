import json
import os

QUEUE_FILE = "fallback_queue.json"

def clear_queue():
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, "r+") as f:
            try:
                queue = [json.loads(line) for line in f]
                print(f"Found {len(queue)} failed posts")
                if input("Clear queue? (y/n): ").lower() == "y":
                    f.truncate(0)
                    print("Queue cleared")
            except json.JSONDecodeError:
                print("Invalid queue format")

if __name__ == "__main__":
    clear_queue() 