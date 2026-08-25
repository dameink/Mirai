import json
import os


CONVERSATION_FILE = "conversation.json"


def load_conversation():

    if not os.path.exists(CONVERSATION_FILE):
        return []

    with open(CONVERSATION_FILE, "r") as file:
        return json.load(file)


def save_conversation(conversation):

    with open(CONVERSATION_FILE, "w") as file:
        json.dump(conversation, file, indent=4)


def add_message(role, content):

    conversation = load_conversation()

    conversation.append({
        "role": role,
        "content": content
    })

    save_conversation(conversation)


def get_history(limit=10):

    conversation = load_conversation()

    return conversation[-limit:]


def clear_conversation():

    save_conversation([])