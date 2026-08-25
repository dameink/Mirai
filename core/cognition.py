# core/cognition.py

import re



# ==========================
# CONTEXT DETECTION
# ==========================


def detect_context(message):

    msg = message.lower()


    if any(word in msg for word in [
        "goal",
        "future",
        "career",
        "want",
        "dream",
        "plan"
    ]):

        return "goal"



    if any(word in msg for word in [
        "project",
        "building",
        "creating",
        "working"
    ]):

        return "project"



    if any(word in msg for word in [
        "like",
        "love",
        "interest",
        "hobby"
    ]):

        return "interest"



    if any(word in msg for word in [
        "feel",
        "nervous",
        "sad",
        "happy",
        "stress"
    ]):

        return "emotion"



    return "general"




# ==========================
# INTENT DETECTION
# ==========================


def detect_intent(message):


    msg = message.lower()


    if any(x in msg for x in [
        "remember",
        "tell me about",
        "what",
        "which"
    ]):

        return "recall"



    if any(x in msg for x in [
        "changed my mind",
        "now i want",
        "instead"
    ]):

        return "update"



    if any(x in msg for x in [
        "i am",
        "i feel"
    ]):

        return "state"



    return "conversation"




# ==========================
# IMPORTANCE
# ==========================


def estimate_importance(message):


    msg = message.lower()


    score = 50


    important_words = {

        "goal":20,
        "future":20,
        "career":20,
        "project":15,
        "achievement":20,
        "proud":15,
        "love":10,
        "hate":10,
        "changed my mind":25

    }


    for word,value in important_words.items():

        if word in msg:

            score += value



    return min(
        100,
        score
    )




# ==========================
# MAIN COGNITION
# ==========================


def understand_message(message):


    return {

        "message":message,

        "context":
            detect_context(message),

        "intent":
            detect_intent(message),

        "importance":
            estimate_importance(message)

    }