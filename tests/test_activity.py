from learning.learner import Learner
from learning.goals import GoalSystem
from learning.modes import ModeSystem
from learning.difficulty import DifficultySystem
from learning.activity import ActivitySystem


learner = Learner()


goals = GoalSystem(
    learner
)


modes = ModeSystem(
    learner,
    goals
)


difficulty = DifficultySystem(
    learner,
    None,
    goals,
    modes
)


activity = ActivitySystem(
    learner,
    goals,
    modes,
    difficulty
)


print(activity.get_activity())