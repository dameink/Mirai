from core.memory import clear_memory
from core.relationship import reset_relationship
from core.emotion import reset_emotion


def reset_all():

    clear_memory()

    reset_relationship()

    reset_emotion()

    print("All systems reset")