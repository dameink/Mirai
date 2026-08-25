from learning.learner import Learner


user = Learner(
    native_language="Russian",
    learning_language="English"
)


user.update_preference(
    "correction_intensity",
    30
)


user.update_motivation(
    "engagement",
    80
)


print(
    user.get_profile()
)