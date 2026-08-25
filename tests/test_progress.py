from learning.progress import ProgressTracker


progress = ProgressTracker()



progress.record(
    "Past Simple",
    30
)


progress.record(
    "Past Simple",
    40
)


progress.record(
    "Past Simple",
    50
)



print(
    "History:",
    progress.get_history(
        "Past Simple"
    )
)



print(
    "Trend:",
    progress.calculate_trend(
        "Past Simple"
    )
)



print(
    "Velocity:",
    progress.learning_velocity(
        "Past Simple"
    )
)



print(
    "Plateau:",
    progress.detect_plateau(
        "Past Simple"
    )
)



print(
    "Stability:",
    progress.calculate_stability(
        "Past Simple"
    )
)



print(
    "Mastery confidence:",
    progress.mastery_confidence(
        "Past Simple"
    )
)