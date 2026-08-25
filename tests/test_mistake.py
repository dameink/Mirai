from learning.learner import Learner
from core.learning_bridge import LearningBridge



print("===== CREATE LEARNER =====")


learner = Learner(

    native_language="Russian",

    learning_language="English"

)


learner.set_goal(
    "ielts"
)



bridge = LearningBridge(
    learner
)



print("\n===== START LEARNING =====")


session = bridge.start_learning()


print(
    session.get_summary()
)



print("\n===== ANALYSIS =====")


analysis = bridge.analyze_user()


print(
    analysis
)



print("\n===== USER ANSWER WITH MISTAKES =====")


result = {


    "fluency":75,


    "pronunciation":85,


    "grammar":40,


    "vocabulary":80

}



print(result)



print("\n===== PROCESS ANSWER =====")


response = bridge.process_answer(

    result

)


print(response)



print("\n===== PROFILE AFTER LEARNING =====")


profile = bridge.get_profile()


print(profile)



print("\n===== CHECK FEEDBACK =====")


last_session = (
    profile["sessions"][-1]
)



print(
    "Feedback:"
)


print(

    last_session["feedback"]

)



print("\n===== CHECK MISTAKES =====")


if "mistakes" in last_session:

    print(
        last_session["mistakes"]
    )

else:

    print(
        "No mistakes storage yet"
    )



print("\n===== TEST COMPLETED =====")