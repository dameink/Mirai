import json
import os


class MemoryStorage:

    def __init__(self, path="learner.json"):
        self.path = path


    # =========================
    # SAVE MEMORY
    # =========================

    def save(self, memory):

        data = memory.get_memory_summary()

        with open(
            self.path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )


    # =========================
    # LOAD MEMORY
    # =========================

    def load(self):
        if not os.path.exists(self.path):
            return None

        try:
            with open(
                self.path,
                "r",
                encoding="utf-8"
            ) as file:
                return json.load(file)

        except json.JSONDecodeError:
            print(
                f"Warning: corrupted memory file: {self.path}"
            )
            return None