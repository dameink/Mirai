from learning.learning_engine import LearningEngine
from learning.learner import Learner


print("\n")
print("=" * 60)
print("MIRAI LEARNING SYSTEM FINAL TEST")
print("=" * 60)


# ===============================
# CREATE LEARNER
# ===============================

learner = Learner()


# ===============================
# CREATE ENGINE
# ===============================

engine = LearningEngine(
    learner
)


# ===============================
# INITIAL ANALYSIS
# ===============================

print("\n===== INITIAL ANALYSIS =====")

analysis = engine.analyze()

print(analysis)


# ===============================
# START SESSION
# ===============================

print("\n===== START SESSION =====")

session = engine.start_session()

print(session)


# ===============================
# SIMULATE LEARNING RESULT
# ===============================

print("\n===== SUBMIT RESULT =====")


result = {

    "skill": "speaking",

    "subskill": "fluency",

    "score": 70,

    "confidence": 75,

    "errors": [

        {
            "type": "grammar",
            "severity": 40
        }

    ]

}


response = engine.submit_result(
    {
        "fluency": 75,
        "grammar": 60,
        "confidence": 70,
        "pronunciation": 65
    }
)


print(response)


# ===============================
# CHECK PROFILE
# ===============================

print("\n===== FINAL PROFILE =====")


profile = engine.get_profile()


print(profile)


# ===============================
# NEXT STRATEGY
# ===============================

print("\n===== NEXT STRATEGY =====")


print(
    engine.controller.get_next_strategy()
)


print("\n")
print("=" * 60)
print("TEST COMPLETE")
print("=" * 60)