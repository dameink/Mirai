from learning.knowledge import KnowledgeMap
from learning.knowledge_state import KnowledgeState
from learning.diagnosis import Diagnosis


knowledge = KnowledgeMap()


student = KnowledgeState(
    knowledge
)


diagnosis = Diagnosis(
    student
)



evidence = {

    "topic": "Past Simple",

    "type": "mistake",

    "impact": -3

}



result = diagnosis.analyze(
    evidence
)


print(result)