import requests
import json
import time
import os
from copy import deepcopy


BASE_URL = os.getenv("MIRAI_URL", "http://127.0.0.1:8000")


# ============================================
# HELPERS
# ============================================

def request(method, endpoint, **kwargs):
    url = BASE_URL + endpoint

    try:
        response = requests.request(
            method,
            url,
            timeout=60,
            **kwargs
        )

        print(f"\n{'=' * 70}")
        print(f"{method} {endpoint}")
        print(f"STATUS: {response.status_code}")
        print(f"{'=' * 70}")

        try:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return data
        except Exception:
            print(response.text)
            return None

    except Exception as e:
        print(f"\n❌ REQUEST FAILED: {method} {endpoint}")
        print(e)
        return None


def check(name, condition, details=""):
    if condition:
        print(f"✅ PASS — {name}")
        return True

    print(f"❌ FAIL — {name}")

    if details:
        print(f"   {details}")

    return False


def snapshot(state):
    if not state:
        return {}

    return {
        "emotion": deepcopy(state.get("emotion")),
        "relationship": deepcopy(state.get("relationship")),
        "learning": deepcopy(state.get("learning")),
    }


def compare_states(before, after):
    changes = []

    if not before or not after:
        return changes

    for category in ["emotion", "relationship", "learning"]:
        old = before.get(category, {})
        new = after.get(category, {})

        if old != new:
            changes.append(category)

    return changes


# ============================================
# TEST STATE
# ============================================

results = []


def test(name, condition, details=""):
    results.append(check(name, condition, details))


# ============================================
# 1. SERVER
# ============================================

print("\n\n")
print("╔══════════════════════════════════════════════════════════════════════╗")
print("║                    MIRAI SYSTEM SIMULATION                           ║")
print("╚══════════════════════════════════════════════════════════════════════╝")

print(f"\nBase URL: {BASE_URL}")


home = request("GET", "/")

test(
    "Server is alive",
    home is not None and home.get("message") == "Mirai is alive!",
    "Expected {message: 'Mirai is alive!'}"
)


# ============================================
# 2. FULL RESET
# ============================================

reset = request("DELETE", "/reset")

test(
    "Full reset works",
    reset is not None and "message" in reset,
)


# ============================================
# 3. INITIAL STATE
# ============================================

initial_state = request("GET", "/state")

test(
    "State endpoint works",
    initial_state is not None,
)

if initial_state:
    test(
        "Emotion exists",
        "emotion" in initial_state,
    )

    test(
        "Relationship exists",
        "relationship" in initial_state,
    )

    test(
        "Learning exists",
        "learning" in initial_state,
    )


# ============================================
# 4. INITIAL LEARNING DATA
# ============================================

profile = request("GET", "/learning/profile")
strategy = request("GET", "/learning/strategy")
history = request("GET", "/learning/history")
memory = request("GET", "/learning/memory")
analysis = request("GET", "/learning/analysis")


test(
    "Learning profile endpoint works",
    profile is not None,
)

test(
    "Learning strategy endpoint works",
    strategy is not None,
)

test(
    "Learning history endpoint works",
    history is not None,
)

test(
    "Learning memory endpoint works",
    memory is not None,
)

test(
    "Learning analysis endpoint works",
    analysis is not None,
)


# ============================================
# 5. START LEARNING SESSION
# ============================================

session = request(
    "POST",
    "/learning/session/start"
)

test(
    "Learning session can start",
    session is not None and "session" in session,
)


# ============================================
# 6. MIRAI WORLD SIMULATION
# ============================================

messages = [
    "Hi Mirai! My name is Alex.",
    "I'm really happy to meet you.",
    "You are really funny.",
    "I really like talking to you.",
    "I am learning English because I want to study abroad.",
    "I usually struggle with speaking English.",
    "Can you help me practice?",
    "Today I learned the word 'ambitious'.",
    "I think I am quite ambitious too.",
    "What do you think about me?",
    "Thank you, Mirai. You are really helpful.",
]


print("\n\n")
print("╔══════════════════════════════════════════════════════════════════════╗")
print("║                    MIRAI WORLD SIMULATION                           ║")
print("╚══════════════════════════════════════════════════════════════════════╝")


def flatten_dict(data, prefix=""):
    """
    Converts nested dictionaries into:
    {
        "emotion.happiness": 70,
        "emotion.energy": 80,
        ...
    }
    """

    result = {}

    if not isinstance(data, dict):
        return result

    for key, value in data.items():

        full_key = f"{prefix}.{key}" if prefix else key

        if isinstance(value, dict):
            result.update(
                flatten_dict(value, full_key)
            )
        else:
            result[full_key] = value

    return result


def show_state_changes(before, after):

    if not before or not after:
        print("  ⚠️ Unable to compare states")
        return []

    changes = []

    before_flat = flatten_dict(before)
    after_flat = flatten_dict(after)

    all_keys = set(before_flat.keys()) | set(after_flat.keys())

    for key in sorted(all_keys):

        old = before_flat.get(key)
        new = after_flat.get(key)

        if old != new:

            changes.append(key)

            print(
                f"  🔄 {key}: {old} → {new}"
            )

    if not changes:
        print("  — No measurable changes")

    return changes


def validate_state_structure(state):

    if not isinstance(state, dict):
        return False

    required = [
        "emotion",
        "relationship",
        "learning",
    ]

    return all(
        key in state
        for key in required
    )


# ============================================
# RUN SIMULATION
# ============================================

for i, message in enumerate(messages, 1):

    print("\n")
    print(
        "┌──────────────────────────────────────────────────────────────────────┐"
    )
    print(
        f"│ MESSAGE {i:<59}│"
    )
    print(
        "└──────────────────────────────────────────────────────────────────────┘"
    )

    print("\nUSER:")
    print(message)

    # ----------------------------------------
    # STATE BEFORE
    # ----------------------------------------

    state_before = request(
        "GET",
        "/state"
    )

    test(
        f"Message {i}: state available before chat",
        state_before is not None
        and validate_state_structure(state_before),
    )

    # ----------------------------------------
    # CHAT
    # ----------------------------------------

    response = request(
        "POST",
        "/chat",
        json={
            "message": message
        }
    )

    test(
        f"Message {i}: chat returns response",
        response is not None
        and "mirai" in response,
    )

    if response:

        print("\nMIRAI:")
        print(
            response.get(
                "mirai",
                "<no response>"
            )
        )

        # ------------------------------------
        # CHECK RESPONSE STATE
        # ------------------------------------

        test(
            f"Message {i}: chat contains state",
            "state" in response
            and validate_state_structure(
                response.get("state")
            ),
        )

        # ------------------------------------
        # STATE AFTER
        # ------------------------------------

        state_after = request(
            "GET",
            "/state"
        )

        test(
            f"Message {i}: state available after chat",
            state_after is not None
            and validate_state_structure(
                state_after
            ),
        )

        # ------------------------------------
        # SHOW REAL CHANGES
        # ------------------------------------

        print("\nSTATE CHANGES:")

        changes = show_state_changes(
            state_before,
            state_after
        )

        # ------------------------------------
        # CHECK RESPONSE STATE VS API STATE
        # ------------------------------------

        if "state" in response and state_after:

            response_state = response["state"]

            same_state = (
                response_state == state_after
            )

            test(
                f"Message {i}: chat state matches /state",
                same_state,
                "The state returned by /chat differs from GET /state"
            )

        # ------------------------------------
        # SPECIAL CHECKS
        # ------------------------------------

        if i in [2, 3, 4, 10, 11]:

            test(
                f"Message {i}: emotional/social message affects world state",
                len(changes) > 0,
                "No emotion, relationship or learning value changed"
            )

        if i in [5, 6, 7, 8, 9]:

            print(
                "\n📚 Learning-related interaction detected"
            )

    time.sleep(0.3)


# ============================================
# 7. FINAL STATE
# ============================================

print("\n\n")
print(
    "╔══════════════════════════════════════════════════════════════════════╗"
)
print(
    "║                     FINAL WORLD STATE                               ║"
)
print(
    "╚══════════════════════════════════════════════════════════════════════╝"
)

final_state = request(
    "GET",
    "/state"
)

test(
    "Final state endpoint works",
    final_state is not None
    and validate_state_structure(final_state),
)

if final_state:

    print("\nFINAL EMOTION:")
    print(
        json.dumps(
            final_state.get("emotion"),
            indent=2,
            ensure_ascii=False
        )
    )

    print("\nFINAL RELATIONSHIP:")
    print(
        json.dumps(
            final_state.get("relationship"),
            indent=2,
            ensure_ascii=False
        )
    )

    print("\nFINAL LEARNING:")
    print(
        json.dumps(
            final_state.get("learning"),
            indent=2,
            ensure_ascii=False
        )
    )


# ============================================
# 8. CONVERSATION PERSISTENCE
# ============================================

print("\n\n")
print(
    "╔══════════════════════════════════════════════════════════════════════╗"
)
print(
    "║                  CONVERSATION PERSISTENCE                           ║"
)
print(
    "╚══════════════════════════════════════════════════════════════════════╝"
)

conversation = request(
    "GET",
    "/conversation"
)

test(
    "Conversation endpoint works",
    conversation is not None,
)

if conversation is not None:

    if isinstance(conversation, list):

        print(
            f"\nConversation messages: {len(conversation)}"
        )

        test(
            "Conversation contains messages",
            len(conversation) > 0,
            "Conversation is empty after simulation"
        )

    elif isinstance(conversation, dict):

        print(
            "\nConversation object:"
        )

        print(
            json.dumps(
                conversation,
                indent=2,
                ensure_ascii=False
            )
        )

        test(
            "Conversation contains data",
            len(conversation) > 0,
            "Conversation object is empty"
        )


# ============================================
# 9. LEARNING AFTER SIMULATION
# ============================================

print("\n\n")
print(
    "╔══════════════════════════════════════════════════════════════════════╗"
)
print(
    "║                       LEARNING CHECK                                ║"
)
print(
    "╚══════════════════════════════════════════════════════════════════════╝"
)

final_profile = request(
    "GET",
    "/learning/profile"
)

final_strategy = request(
    "GET",
    "/learning/strategy"
)

final_history = request(
    "GET",
    "/learning/history"
)

final_memory = request(
    "GET",
    "/learning/memory"
)

final_analysis = request(
    "GET",
    "/learning/analysis"
)


test(
    "Learning profile works",
    final_profile is not None,
)

test(
    "Learning strategy works",
    final_strategy is not None,
)

test(
    "Learning history works",
    final_history is not None,
)

test(
    "Learning memory works",
    final_memory is not None,
)

test(
    "Learning analysis works",
    final_analysis is not None,
)


# ============================================
# 10. PERSISTENCE BETWEEN REQUESTS
# ============================================

print("\n\n")
print(
    "╔══════════════════════════════════════════════════════════════════════╗"
)
print(
    "║                    PERSISTENCE TEST                                ║"
)
print(
    "╚══════════════════════════════════════════════════════════════════════╝"
)

state_1 = request(
    "GET",
    "/state"
)

conversation_1 = request(
    "GET",
    "/conversation"
)

time.sleep(1)

state_2 = request(
    "GET",
    "/state"
)

conversation_2 = request(
    "GET",
    "/conversation"
)


test(
    "State persists between requests",
    state_1 == state_2,
    "State changed without any new interaction"
)

test(
    "Conversation persists between requests",
    conversation_1 == conversation_2,
    "Conversation changed without any new interaction"
)


# ============================================
# 11. RESET TEST
# ============================================

print("\n\n")
print(
    "╔══════════════════════════════════════════════════════════════════════╗"
)
print(
    "║                         RESET TEST                                  ║"
)
print(
    "╚══════════════════════════════════════════════════════════════════════╝"
)

reset_result = request(
    "DELETE",
    "/reset"
)

test(
    "Reset endpoint works",
    reset_result is not None
    and "message" in reset_result,
)


conversation_after_reset = request(
    "GET",
    "/conversation"
)

test(
    "Conversation clears after reset",
    conversation_after_reset == [],
    f"Remaining data: {conversation_after_reset}"
)


state_after_reset = request(
    "GET",
    "/state"
)

test(
    "State still exists after reset",
    state_after_reset is not None
    and validate_state_structure(
        state_after_reset
    ),
)


# ============================================
# 12. FINAL REPORT
# ============================================

print("\n\n")
print(
    "╔══════════════════════════════════════════════════════════════════════╗"
)
print(
    "║                         FINAL REPORT                                ║"
)
print(
    "╚══════════════════════════════════════════════════════════════════════╝"
)

passed = sum(results)
failed = len(results) - passed

print(
    f"\nTotal tests : {len(results)}"
)

print(
    f"Passed      : {passed}"
)

print(
    f"Failed      : {failed}"
)

if failed == 0:

    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                         ✅ MIRAI PASS                               ║
║                                                                      ║
║  All automated system checks passed.                                ║
╚══════════════════════════════════════════════════════════════════════╝
""")

else:

    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                         ❌ MIRAI FAIL                               ║
║                                                                      ║
║  Some subsystem checks failed.                                      ║
║  Inspect the output above to locate the broken subsystem.            ║
╚══════════════════════════════════════════════════════════════════════╝
""")
# ============================================
# 7. STATE AFTER CONVERSATION
# ============================================

print("\n\n")
print("╔══════════════════════════════════════════════════════════════════════╗")
print("║                     FINAL STATE CHECK                               ║")
print("╚══════════════════════════════════════════════════════════════════════╝")

final_state = request("GET", "/state")

test(
    "Final state endpoint works",
    final_state is not None,
)


# ============================================
# 8. CHECK CONVERSATION PERSISTENCE
# ============================================

conversation = request(
    "GET",
    "/conversation"
)

test(
    "Conversation endpoint works",
    conversation is not None,
)

if conversation is not None:

    if isinstance(conversation, list):

        test(
            "Conversation contains messages",
            len(conversation) > 0,
            f"Conversation length: {len(conversation)}"
        )

    elif isinstance(conversation, dict):

        test(
            "Conversation contains data",
            len(conversation) > 0,
            "Conversation object is empty"
        )


# ============================================
# 9. CHECK LEARNING AFTER CHAT
# ============================================

print("\n\n")
print("╔══════════════════════════════════════════════════════════════════════╗")
print("║                    LEARNING CHECK                                   ║")
print("╚══════════════════════════════════════════════════════════════════════╝")


final_profile = request(
    "GET",
    "/learning/profile"
)

final_strategy = request(
    "GET",
    "/learning/strategy"
)

final_history = request(
    "GET",
    "/learning/history"
)

final_memory = request(
    "GET",
    "/learning/memory"
)

final_analysis = request(
    "GET",
    "/learning/analysis"
)


test(
    "Learning profile still works after conversation",
    final_profile is not None,
)

test(
    "Learning strategy still works after conversation",
    final_strategy is not None,
)

test(
    "Learning history still works after conversation",
    final_history is not None,
)

test(
    "Learning memory still works after conversation",
    final_memory is not None,
)

test(
    "Learning analysis still works after conversation",
    final_analysis is not None,
)


# ============================================
# 10. PERSISTENCE TEST
# ============================================

print("\n\n")
print("╔══════════════════════════════════════════════════════════════════════╗")
print("║                    PERSISTENCE TEST                                ║")
print("╚══════════════════════════════════════════════════════════════════════╝")


state_before_restart = request(
    "GET",
    "/state"
)

conversation_before_restart = request(
    "GET",
    "/conversation"
)


print("\nThe server process is NOT restarted automatically.")
print("This test checks whether data survives between API requests.")


state_after = request(
    "GET",
    "/state"
)

conversation_after = request(
    "GET",
    "/conversation"
)


test(
    "State persists between requests",
    state_before_restart == state_after,
)

test(
    "Conversation persists between requests",
    conversation_before_restart == conversation_after,
)


# ============================================
# 11. RESET TEST
# ============================================

print("\n\n")
print("╔══════════════════════════════════════════════════════════════════════╗")
print("║                       RESET TEST                                    ║")
print("╚══════════════════════════════════════════════════════════════════════╝")


reset = request(
    "DELETE",
    "/reset"
)

test(
    "Reset endpoint responds",
    reset is not None,
)


state_after_reset = request(
    "GET",
    "/state"
)

conversation_after_reset = request(
    "GET",
    "/conversation"
)


if conversation_after_reset is not None:

    if isinstance(conversation_after_reset, list):

        test(
            "Conversation actually clears",
            len(conversation_after_reset) == 0,
            f"Remaining messages: {len(conversation_after_reset)}"
        )

    elif isinstance(conversation_after_reset, dict):

        test(
            "Conversation actually clears",
            len(conversation_after_reset) == 0,
            "Conversation still contains data"
        )


# ============================================
# 12. FINAL REPORT
# ============================================

print("\n\n")
print("╔══════════════════════════════════════════════════════════════════════╗")
print("║                         FINAL REPORT                                ║")
print("╚══════════════════════════════════════════════════════════════════════╝")

passed = sum(results)
failed = len(results) - passed

print(f"\nTotal tests : {len(results)}")
print(f"Passed      : {passed}")
print(f"Failed      : {failed}")

if failed == 0:

    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                         ✅ MIRAI PASS                               ║
║                                                                      ║
║  All automated system checks passed.                                ║
╚══════════════════════════════════════════════════════════════════════╝
""")

else:

    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                         ❌ MIRAI FAIL                               ║
║                                                                      ║
║  Some subsystem checks failed.                                      ║
║  Inspect the output above to locate the broken subsystem.            ║
╚══════════════════════════════════════════════════════════════════════╝
""")