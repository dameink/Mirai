from learning.learner import Learner
from learning.state import LearningState
from learning.goals import GoalSystem
from learning.modes import ModeSystem
from learning.difficulty import DifficultySystem
from learning.activity import ActivitySystem
from learning.update import SkillUpdateSystem



# =========================
# Create learner
# =========================

learner = Learner(
    native_language="Russian",
    learning_language="English"
)


learner.set_goal(
    "ielts"
)


# =========================
# Create systems
# =========================

state = LearningState(
    learner
)


goals = GoalSystem(
    learner
)


modes = ModeSystem(
    learner,
    goals
)


difficulty = DifficultySystem(
    learner,
    state,
    goals,
    modes
)


activities = ActivitySystem(
    learner,
    state,
    goals,
    modes,
    difficulty
)



# =========================
# BEFORE LEARNING
# =========================

print("\n===== BEFORE =====")

print(
    state.get_state()
)


print(
    "\nACTIVITY:"
)

print(
    activities.generate_activity()
)



# =========================
# Simulate learning result
# =========================

print("\n===== ADDING EXPERIENCE =====")


from learning.evidence import Evidence



updater = SkillUpdateSystem(
    learner
)



evidences = [


    Evidence(
        skill="fluency",
        category="speaking",
        value=70,
        evidence_type="feedback",
        certainty=80
    ),



    Evidence(
        skill="grammar",
        category="writing",
        value=60,
        evidence_type="feedback",
        certainty=80
    ),



    Evidence(
        skill="vocabulary",
        category="reading",
        value=80,
        evidence_type="feedback",
        certainty=80
    )

]



updater.update_from_evidence(
    evidences
)



# =========================
# AFTER LEARNING
# =========================

print("\n===== AFTER =====")


print(
    state.get_state()
)



print(
    "\nNEW ACTIVITY:"
)


print(
    activities.generate_activity()
)