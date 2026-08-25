from learning.learner import Learner
from learning.controller import LearningController



# =====================================
# Create learner
# =====================================

learner = Learner(
    native_language="Russian",
    learning_language="English"
)


# Initial motivation

learner.update_motivation(
    "effort",
    80
)

learner.update_motivation(
    "engagement",
    85
)


# Set goal

learner.set_goal(
    "ielts"
)



controller = LearningController(
    learner
)



# =====================================
# BEFORE
# =====================================

print("\n===== BEFORE LEARNING =====")

print(
    learner.get_skill(
        "speaking",
        "fluency"
    )
)



# =====================================
# ANALYSIS
# =====================================

print("\n===== FIRST ANALYSIS =====")

analysis = controller.analyze()

print(
    analysis
)



# =====================================
# CREATE SESSION
# =====================================

print("\n===== SESSION =====")

session = controller.start_session()

print(
    session.__dict__
)



# =====================================
# Simulate user completing activity
# =====================================

print("\n===== USER COMPLETED ACTIVITY =====")


feedback = {

    "fluency": 70,

    "grammar": 60,

    "vocabulary": 80,

    "pronunciation": 85

}


print(
    feedback
)



# =====================================
# APPLY LEARNING UPDATE
# =====================================

print("\n===== UPDATING SKILLS =====")


learner.update_skill(
    "speaking",
    "fluency",
    feedback["fluency"],
    20
)


learner.update_skill(
    "writing",
    "grammar",
    feedback["grammar"],
    20
)


learner.update_skill(
    "reading",
    "vocabulary",
    feedback["vocabulary"],
    20
)


learner.update_skill(
    "speaking",
    "pronunciation",
    feedback["pronunciation"],
    20
)



# Recalculate CEFR level

learner.calculate_overall_level()



# =====================================
# AFTER
# =====================================

print("\n===== AFTER LEARNING =====")


print(
    "Fluency:",
    learner.get_skill(
        "speaking",
        "fluency"
    )
)


print(
    "Grammar:",
    learner.get_skill(
        "writing",
        "grammar"
    )
)


print(
    "Vocabulary:",
    learner.get_skill(
        "reading",
        "vocabulary"
    )
)


print(
    "Pronunciation:",
    learner.get_skill(
        "speaking",
        "pronunciation"
    )
)



# =====================================
# NEW ANALYSIS
# =====================================

print("\n===== SECOND ANALYSIS =====")

print(
    controller.analyze()
)



# =====================================
# PROFILE
# =====================================

print("\n===== FINAL PROFILE =====")

print(
    learner.get_profile()
)