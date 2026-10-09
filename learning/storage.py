from core.persistence import atomic_write_json, StateCorruptedError
from core.state_store import read_document, write_document
import json
import os



class MemoryStorage:

    def __init__(self, path="learner.json", user_id=None):
        self.user_id = user_id

        self.path = path

    # =========================
    # SAVE MEMORY
    # =========================

    def save(self, memory):

        data = memory.get_memory_summary()

        if self.user_id:
            write_document(self.user_id, "learning_memory", data)
        else:
            atomic_write_json(self.path, data)

    # =========================
    # LOAD MEMORY
    # =========================

    def load(self):
        if self.user_id:
            return read_document(self.user_id, "learning_memory", None)

        if not os.path.exists(self.path):
            return None

        try:

            with open(
                self.path,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(file)

        except json.JSONDecodeError as error:
            raise StateCorruptedError("Learning memory needs recovery") from error

    # =========================
    # DELETE MEMORY
    # =========================

    def delete(self):
        """
        Delete persistent learning memory for this user.
        """

        if self.user_id:
            # Keep a tombstone so an old JSON backup can never resurrect reset data.
            write_document(self.user_id, "learning_memory", None)
        elif os.path.exists(self.path):
            os.remove(self.path)