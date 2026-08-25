from learning.learner import Learner
from learning.evidence import Evidence
from learning.update import SkillUpdateSystem



learner = Learner()


update = SkillUpdateSystem(
    learner
)



evidence = Evidence(

    skill="fluency",

    category="speaking",

    value=60,

    evidence_type="feedback",

    source="IELTS Speaking Part 2",

    certainty=70

)



print(
    "BEFORE"
)

print(
    learner.skills["speaking"]["fluency"]
)



update.update_skill(
    evidence
)



print(
    "\nAFTER"
)

print(
    learner.skills["speaking"]["fluency"]
)