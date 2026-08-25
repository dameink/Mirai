from core.memory_engine import save_event_memory
from core.memory import get_memory, clear_memory
from core.memory_recall import recall_memory



print("\n========== RESET MEMORY ==========")

clear_memory()

print("Memory cleared")



# ==========================
# TEST 1
# SEMANTIC MEMORY
# ==========================

print("\n========== TEST SEMANTIC ==========")


save_event_memory(
    "achievement",
    "I passed my physics exam"
)


save_event_memory(
    "preference",
    "User likes nuclear physics"
)


save_event_memory(
    "goal",
    "User wants to become a mechanical engineer"
)



# ==========================
# TEST 2
# DUPLICATE PROTECTION
# ==========================

print("\n========== TEST DUPLICATES ==========")


save_event_memory(
    "achievement",
    "I passed my physics exam"
)


save_event_memory(
    "achievement",
    "I passed my physics exam"
)



# ==========================
# TEST 3
# EPISODIC MEMORY
# ==========================

print("\n========== TEST EPISODIC ==========")


save_event_memory(
    "deep_conversation",
    "User talked about future career plans"
)


save_event_memory(
    "milestone",
    "User started building Mirai application"
)




# ==========================
# TEST 4
# EMOTIONAL MEMORY
# ==========================

print("\n========== TEST EMOTIONAL ==========")


save_event_memory(
    "stress",
    "User felt nervous before university interview",
    emotion="anxiety",
    intensity=80
)


save_event_memory(
    "happiness",
    "User felt proud after finishing a project",
    emotion="happiness",
    intensity=90
)



# ==========================
# TEST 5
# RELATIONSHIP MEMORY
# ==========================

print("\n========== TEST RELATIONSHIP ==========")


save_event_memory(
    "support_received",
    "Mirai helped user prepare for interview"
)


save_event_memory(
    "user_compliment",
    "User thanked Mirai for help"
)




# ==========================
# PRINT FULL MEMORY
# ==========================

print("\n========== FULL MEMORY ==========")


memory = get_memory()


print(memory)




# ==========================
# TEST RECALL
# ==========================

print("\n========== TEST RECALL ==========")


queries = [

    "I have a physics exam",

    "I am nervous about interview",

    "Tell me about my goals",

    "What projects am I working on?"

]


for query in queries:


    print("\nQUERY:")
    print(query)


    results = recall_memory(query)


    for result in results:


        print(
            "\nTYPE:",
            result["type"]
        )

        print(
            "MEMORY:",
            result["memory"]
        )

        print(
            "SCORE:",
            result["score"]
        )