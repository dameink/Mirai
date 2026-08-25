from core.personality import personality



def get_personality():

    return personality



def calculate_personality_influence():

    traits = personality["core_traits"]


    influence = {


        "warmth":
            traits["empathy"],


        "humor_level":
            traits["humor"],


        "confidence":
            traits["confidence"],


        "curiosity":
            traits["curiosity"],


        "patience":
            traits["patience"],


        "seriousness":
            100 - traits["humor"]

    }


    return influence