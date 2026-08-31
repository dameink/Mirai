import json
import sys
import time

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

RESULT_FILE = "mirai_test_result.txt"


# ============================================================
# OUTPUT LOGGER
# ============================================================

class Tee:
    """
    Writes output both to the terminal and to a text file.
    """

    def __init__(self, file):
        self.terminal = sys.stdout
        self.file = file

    def write(self, message):
        self.terminal.write(message)
        self.file.write(message)

    def flush(self):
        self.terminal.flush()
        self.file.flush()


# ============================================================
# RESET
# ============================================================

def reset_mirai():

    print("\n" + "=" * 70)
    print("RESET MIRAI")
    print("=" * 70)

    response = client.delete("/reset")

    print("STATUS:", response.status_code)

    try:
        print(json.dumps(
            response.json(),
            indent=4,
            ensure_ascii=False
        ))
    except Exception:
        print(response.text)


# ============================================================
# STATE
# ============================================================

def get_state():

    response = client.get("/state")

    if response.status_code != 200:

        print("\nSTATE ERROR:", response.status_code)
        print(response.text)

        return None

    return response.json()


def print_state():

    state = get_state()

    if state is None:
        return

    print("\n" + "=" * 70)
    print("CURRENT MIRAI STATE")
    print("=" * 70)

    print(json.dumps(
        state,
        indent=4,
        ensure_ascii=False
    ))


# ============================================================
# CHAT
# ============================================================

def ask(number, message):

    print("\n" + "=" * 70)
    print(f"[{number}] USER")
    print("=" * 70)

    print(message)

    start = time.time()

    try:

        response = client.post(
            "/chat",
            json={
                "message": message
            }
        )

    except Exception as e:

        print("\nREQUEST ERROR")
        print("ERROR:", e)

        return None

    elapsed = time.time() - start

    print("\nSTATUS:", response.status_code)
    print("TIME:", round(elapsed, 2), "seconds")

    if response.status_code != 200:

        print("\nERROR:")
        print(response.text)

        return None

    try:

        data = response.json()

    except Exception:

        print("\nINVALID JSON:")
        print(response.text)

        return None

    print("\nMIRAI:")
    print("-" * 70)

    print(data.get("mirai"))

    print("\nSTATE AFTER MESSAGE:")
    print("-" * 70)

    print(json.dumps(
        data.get("state"),
        indent=4,
        ensure_ascii=False
    ))

    return data


# ============================================================
# LEARNING TEST
# ============================================================

def learning_test():

    print("\n")
    print("=" * 70)
    print("MIRAI LEARNING SYSTEM — MINI TEST")
    print("=" * 70)

    print("""
This test checks:

1. Learning goal detection
2. Learning request detection
3. Learning event processing
4. Learner profile updates
5. Learning memory
6. Learning state
7. Session / activity creation
8. Skill update pipeline
""")

    # ========================================================
    # RESET
    # ========================================================

    reset_mirai()

    print_state()

    # ========================================================
    # TEST 1 — LEARNING GOAL
    # ========================================================

    ask(
        1,
        "I want to improve my English."
    )

    # ========================================================
    # TEST 2 — LEARNING REQUEST
    # ========================================================

    ask(
        2,
        "Can we practice English?"
    )

    # ========================================================
    # TEST 3 — IELTS GOAL
    # ========================================================

    ask(
        3,
        "I want to prepare for IELTS."
    )

    # ========================================================
    # TEST 4 — LEARNING PROGRESS
    # ========================================================

    ask(
        4,
        "I think my speaking has improved."
    )

    # ========================================================
    # TEST 5 — LEARNING FAILURE
    # ========================================================

    ask(
        5,
        "I don't understand this grammar."
    )

    # ========================================================
    # FINAL STATE
    # ========================================================

    print("\n")
    print("=" * 70)
    print("FINAL LEARNING STATE")
    print("=" * 70)

    print_state()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    with open(
        RESULT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        original_stdout = sys.stdout

        sys.stdout = Tee(file)

        try:

            learning_test()

        finally:

            sys.stdout = original_stdout

    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print(f"Result saved to: {RESULT_FILE}")