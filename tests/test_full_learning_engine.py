from learning.learner import Learner
from learning.controller import LearningController


# ==========================
# Create learner
# ==========================

learner = Learner(
    native_language="Russian",
    learning_language="English"
)


# Goal

learner.set_goal(
    primary="ielts"
)


# Motivation example

learner.update_motivation(
    "effort",
    80
)

learner.update_motivation(
    "engagement",
    85
)



# ==========================
# Create controller
# ==========================

controller = LearningController(
    learner
)



# ==========================
# BEFORE
# ==========================

print("\n===== BEFORE =====")

print(
    controller.state.get_state()
)



# ==========================
# FIRST ANALYSIS
# ==========================

print("\n===== FIRST ANALYSIS =====")

analysis = controller.analyze()

print(
    analysis
)



# ==========================
# START SESSION
# ==========================

print("\n===== SESSION =====")

session = controller.start_session()

print(
    session.get_data()
    if hasattr(session, "get_data")
    else session.__dict__
)



print("===== USER RESULT =====")

user_result = {
    "fluency": 75,
    "pronunciation": 85,
    "grammar": 60,
    "vocabulary": 80
}


print(user_result)


print("===== UPDATING =====")


result = controller.complete_activity(
    user_result
)


updates = result["updates"]


for update in updates:
    print(update)




# ==========================
# AFTER LEARNING
# ==========================

print("\n===== AFTER =====")

print(
    controller.state.get_state()
)



# ==========================
# ADAPTATION
# ==========================

print("\n===== NEW STRATEGY =====")

strategy = controller.get_next_strategy()

print(
    strategy
)



# ==========================
# NEXT ACTIVITY
# ==========================

print("\n===== NEXT PROFILE =====")

print("===== LEARNING HISTORY =====")

print(
    learner.history
)

print("===== HISTORY =====")

print(
    learner.history
)

profile = controller.get_learning_profile()

print(
    profile["strategy"]
)