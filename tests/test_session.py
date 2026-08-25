from learning.learner import Learner
from learning.session import SessionSystem



learner = Learner(
    native_language="Russian",
    learning_language="English"
)



sessions = SessionSystem(
    learner
)



session = sessions.create_session(

    goal="ielts",

    mode="exam",

    difficulty="challenging"

)



session.add_activity(
    "writing task"
)


session.add_activity(
    "speaking practice"
)



session.update_performance(
    True
)


session.update_performance(
    True
)


session.update_performance(
    False
)



session.add_feedback(
    "Good vocabulary usage"
)



print(
    session.get_summary()
)


print(
    sessions.get_history()
)