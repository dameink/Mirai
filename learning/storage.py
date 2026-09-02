import json
import os

from core.user_state import get_user_file


class MemoryStorage:

    def __init__(self, path="learner.json", user_id=None):
        self.user_id = user_id

        if user_id:
            self.path = get_user_file(
                user_id,
                "learning_memory.json"
            )
        else:
            self.path = path

    # =========================
    # SAVE MEMORY
    # =========================

    def save(self, memory):

        data = memory.get_memory_summary()

        os.makedirs(
            os.path.dirname(self.path) or ".",
            exist_ok=True
        )

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

    # =========================
    # DELETE MEMORY
    # =========================

    def delete(self):
        """
        Delete persistent learning memory for this user.
        """

        if os.path.exists(self.path):
            os.remove(self.path)