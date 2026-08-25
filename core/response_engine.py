from core.behavior import get_behavior
from core.emotion import get_emotion
from core.relationship import get_relationship
from core.memory_recall import recall_memory
from core.memory import get_memory
from core.intent import detect_intent
from core.personality import personality
from core.personality_voice import get_personality_voice


def analyze_memory_intent(memories):

    if not memories:
        return "none"


    # New memory system:
    # semantic -> facts

    if isinstance(memories, dict):

        facts = memories.get(
            "semantic",
            {}
        ).get(
            "facts",
            []
        )


        if not facts:
            return "none"


        memory = facts[-1]


    # Old memory compatibility

    elif isinstance(memories, list):

        memory = memories[0]


    else:
        return "none"



    category = memory.get(
        "category",
        "unknown"
    )


    if category == "achievement":
        return "celebrate"


    elif category == "interest":
        return "connect"


    elif category == "problem":
        return "support"


    elif category == "hobby":
        return "casual"


    elif category == "personal":
        return "support"


    elif category == "identity":
        return "personal"


    return "neutral"





def get_response_context(message):


    # ======================
    # Current systems
    # ======================

    behavior = get_behavior()

    emotion = get_emotion()

    relationship = get_relationship()

    memory = get_memory()



    # ======================
    # Understanding message
    # ======================

    memories = recall_memory(message)

    intent = detect_intent(message)



    # ======================
    # Context
    # ======================

    context = {



        # ======================
        # Personality
        # ======================

        "personality": {

            "traits":
                personality["core_traits"],


            "communication_style":
                personality["communication_style"],


            "values":
                personality["values"],


            "weaknesses":
                personality["weaknesses"]

        },




        # ======================
        # Behavior
        # ======================

        "behavior": behavior,



        "tone":
            behavior["tone"],


        "conversation_mode":
            behavior["conversation_mode"],


        "warmth":
            behavior["warmth"],


        "humor":
            behavior["humor_level"],


        "seriousness":
            behavior["seriousness"],


        "talkativeness":
            behavior["talkativeness"],




        # ======================
        # Relationship
        # ======================


        "relationship": relationship,


        "relationship_stage":
            relationship.get(
                "stage",
                "stranger"
            ),


        "closeness":
            relationship.get(
                "closeness",
                0
            ),


        "bond":
            relationship.get(
                "bond",
                0
            ),



        # ======================
        # Emotion
        # ======================


        "emotion": emotion,


        "mood":
            behavior["mood"],


        "energy":
            emotion["state"].get(
                "energy",
                50
            ),




        # ======================
        # Memory
        # ======================


        "user_profile": {

            "name":
                memory.get(
                    "user_name"
                )

        },


        "relevant_memories":
            memories,


        "memory_intent":
            analyze_memory_intent(
                memories
            ),




        # ======================
        # User understanding
        # ======================


        "user_intent":
            intent



    }



    return context

def choose_response_strategy(context):

    intent = context.get(
        "user_intent",
        "casual_chat"
    )


    relationship = context.get(
        "relationship_stage",
        "stranger"
    )


    humor = context.get(
        "humor",
        50
    )


    closeness = context.get(
        "closeness",
        0
    )


    bond = context.get(
        "bond",
        0
    )



    strategies = {

        "celebrate": {
            "emotion": "excited",
            "style": "encouraging",
            "ask_question": True
        },


        "seek_support": {
            "emotion": "calm",
            "style": "empathetic",
            "ask_question": True
        },


        "casual_chat": {
            "emotion": "friendly",
            "style": "light",
            "ask_question": True
        },


        "support_failure": {
            "emotion": "concerned",
            "style": "supportive",
            "ask_question": True
        },


        "show_curiosity": {
            "emotion": "curious",
            "style": "interested",
            "ask_question": True
        },


        "deep_support": {
            "emotion": "warm",
            "style": "thoughtful",
            "ask_question": True
        },


        "comfort": {
            "emotion": "calm",
            "style": "supportive",
            "ask_question": True
        },


        "explain": {
            "emotion": "patient",
            "style": "clear",
            "ask_question": False
        },


        "motivate": {
            "emotion": "encouraging",
            "style": "positive",
            "ask_question": True
        },


        "accept_compliment": {
            "emotion": "happy",
            "style": "playful",
            "ask_question": False
        },


        "accept_gratitude": {
            "emotion": "warm",
            "style": "friendly",
            "ask_question": False
        },


        "apology_response": {
            "emotion": "calm",
            "style": "forgiving",
            "ask_question": False
        },


        "explore_opinion": {
            "emotion": "curious",
            "style": "conversational",
            "ask_question": True
        },


        "understand_decision": {
            "emotion": "curious",
            "style": "reflective",
            "ask_question": True
        },


        "normal_conversation": {
            "emotion": "curious",
            "style": "interested",
            "ask_question": True
        }

    }



    # Создаем копию,
    # чтобы не менять оригинальный словарь

    strategy = strategies.get(
        intent,
        strategies["casual_chat"]
    ).copy()
    strategy["voice"] = get_personality_voice(
    context,
    strategy
)



    # =================================
    # RELATIONSHIP INFLUENCE
    # =================================


    if closeness < 20:


        strategy["personal_level"] = "stranger"

        strategy["memory_reference_allowed"] = False

        strategy["teasing_allowed"] = False

        strategy["emotional_depth"] = "low"



    elif closeness < 50:


        strategy["personal_level"] = "acquaintance"

        strategy["memory_reference_allowed"] = True

        strategy["teasing_allowed"] = False

        strategy["emotional_depth"] = "medium"



    elif closeness < 80:


        strategy["personal_level"] = "friend"

        strategy["memory_reference_allowed"] = True

        strategy["teasing_allowed"] = True

        strategy["emotional_depth"] = "medium"



    else:


        strategy["personal_level"] = "close_friend"

        strategy["memory_reference_allowed"] = True

        strategy["teasing_allowed"] = True

        strategy["emotional_depth"] = "high"



    # =================================
    # RELATIONSHIP STAGE CHECK
    # =================================


    if relationship == "trusted_friend":

        strategy["personal_level"] = "trusted_friend"

        strategy["emotional_depth"] = "high"



    # =================================
    # BOND INFLUENCE
    # =================================


    strategy["warmth_boost"] = (
        bond >= 50
    )



    # =================================
    # PERSONALITY INFLUENCE
    # =================================


    strategy["humor_allowed"] = (
        humor >= 70
    )



    return strategy