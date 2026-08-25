from learning.knowledge import KnowledgeMap
from learning.knowledge_state import KnowledgeState
from learning.progress import ProgressTracker


knowledge = KnowledgeMap()


progress = ProgressTracker()


student = KnowledgeState(
    knowledge,
    progress
)


print(
    student.get_topic_state(
        "Past Simple"
    )
)



student.update_topic(
    "Past Simple",
    5,
    10
)
print(
    progress.get_history(
        "Past Simple"
    )
)



print(
    student.get_topic_state(
        "Past Simple"
    )
)


print(
    student.get_weak_topics()
)