from learning.feedback import FeedbackSystem


activity = {

    "name":
        "IELTS Speaking Part 2",

    "skill":
        "speaking"

}



performance = {

    "scores": {

        "fluency": 60,

        "grammar": 55,

        "vocabulary": 75,

        "pronunciation": 80

    }

}



feedback_system = FeedbackSystem(
    None
)


feedback = feedback_system.analyze(
    activity,
    performance
)


print(
    feedback.get_feedback()
)