import re
from datetime import datetime


class MemoryAnalyzer:


    def __init__(self):


        self.emotion_words = {

            "nervous": "anxiety",
            "worried": "anxiety",
            "anxious": "anxiety",
            "afraid": "fear",
            "scared": "fear",

            "happy": "happiness",
            "excited": "happiness",
            "proud": "pride",
            "satisfied": "happiness",

            "angry": "frustration",
            "frustrated": "frustration",
            "annoyed": "frustration",

            "sad": "sadness",
            "lonely": "sadness"

        }



        self.success_words = [

            "passed",
            "finished",
            "completed",
            "achieved",
            "won",
            "built",
            "created"

        ]



        self.goal_words = [

            "want to become",
            "want to be",
            "my goal",
            "i want"

        ]



        self.dislike_words = [

            "dont like",
            "don't like",
            "do not like",
            "hate",
            "anymore"

        ]



        self.relationship_words = [

            "thank you",
            "thanks",
            "helped me",
            "appreciate",
            "you helped"

        ]



        self.change_words = [

            "changed my mind",
            "anymore",
            "no longer",
            "different now"

        ]



        self.event_words = [

            "started",
            "began",
            "yesterday",
            "today",
            "recently"

        ]



    # =====================================
    # TEXT PROCESSING
    # =====================================


    def clean_text(self, message):

        text = message.lower()

        text = re.sub(
            r"[^a-zA-Z0-9\s']",
            "",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()



    # =====================================
    # EMOTION ANALYSIS
    # =====================================


    def detect_emotion(self,text):


        # special success context


        if any(
            word in text
            for word in self.success_words
        ):


            if "proud" in text:

                return {
                    "emotion":"pride",
                    "intensity":90
                }


            return {
                "emotion":"happiness",
                "intensity":80
            }



        for word,emotion in self.emotion_words.items():

            if word in text:


                intensity=70


                if any(
                    x in text
                    for x in [
                        "very",
                        "really",
                        "extremely"
                    ]
                ):

                    intensity=90



                return {

                    "emotion":emotion,

                    "intensity":intensity

                }



        return None




    # =====================================
    # SEMANTIC MEMORY
    # =====================================


    def detect_semantic(self,message,text):


        memories=[]



        # achievements


        if any(
            word in text
            for word in self.success_words
        ):


            memories.append({

                "type":"semantic",

                "category":"achievement",

                "content":message,

                "importance":80

            })



        # goals


        if any(
            word in text
            for word in self.goal_words
        ):


            memories.append({

                "type":"semantic",

                "category":"goal",

                "content":message,

                "importance":90

            })



        # dislikes


        if any(
            word in text
            for word in self.dislike_words
        ):


            memories.append({

                "type":"semantic",

                "category":"dislike",

                "content":message,

                "importance":65

            })



        return memories




    # =====================================
    # EPISODIC MEMORY
    # =====================================


    def detect_episodic(self,message,text):


        memories=[]



        if any(
            word in text
            for word in self.event_words
        ):


            memories.append({

                "type":"episodic",

                "category":"event",

                "content":message,

                "importance":70

            })



        # project milestone


        if (
            "project" in text
            and
            any(
                word in text
                for word in [
                    "finished",
                    "completed",
                    "built",
                    "created"
                ]
            )
        ):


            memories.append({

                "type":"episodic",

                "category":"milestone",

                "content":message,

                "importance":90

            })


        return memories




    # =====================================
    # RELATIONSHIP MEMORY
    # =====================================


    def detect_relationship(self,message,text):


        if any(
            word in text
            for word in self.relationship_words
        ):


            return [{

                "type":"relationship",

                "category":"interaction",

                "content":message,

                "importance":75

            }]


        return []




    # =====================================
    # EMOTIONAL MEMORY
    # =====================================


    def create_emotional_memory(
            self,
            message,
            emotion
    ):


        if emotion is None:

            return []



        return [{

            "type":"emotional",

            "category":"emotion",

            "content":message,

            "importance":70

        }]




    # =====================================
    # CHANGE DETECTION
    # =====================================


    def detect_change(self,text):


        if "changed my mind" in text:

            return "opinion_change"



        if (
            "anymore" in text
            and
            (
                "dont like" in text
                or
                "don't like" in text
            )
        ):

            return "loss_of_interest"



        return None




    # =====================================
    # IMPORTANCE
    # =====================================


    def calculate_importance(
            self,
            memories,
            emotion,
            change
    ):


        score=20



        for memory in memories:


            category=memory["category"]



            if category=="goal":

                score+=50



            elif category=="achievement":

                score+=35



            elif category=="milestone":

                score+=40



            elif category=="interaction":

                score+=35



            elif category=="dislike":

                score+=30



            elif memory["type"]=="emotional":

                score+=25




        if emotion:

            score+=15



        if change:

            score+=35



        return min(score,100)




    # =====================================
    # MAIN ANALYZER
    # =====================================


    def analyze(self,message):


        text=self.clean_text(message)



        memories=[]



        memories.extend(
            self.detect_semantic(
                message,
                text
            )
        )



        memories.extend(
            self.detect_episodic(
                message,
                text
            )
        )



        memories.extend(
            self.detect_relationship(
                message,
                text
            )
        )



        emotion=self.detect_emotion(text)



# Save emotional memory only when emotion is personal/relevant

        if emotion and (
            emotion["emotion"] in [
                "anxiety",
                "fear",
                "sadness",
                "frustration",
                "pride"
            ]
        ):


            memories.extend(
                self.create_emotional_memory(
                    message,
                    emotion
                )
            )



        change=self.detect_change(text)



        importance=self.calculate_importance(
            memories,
            emotion,
            change
        )



        confidence=60


        if change:

            confidence+=20


        if emotion:

            confidence+=10


        if len(memories)>1:

            confidence+=10



        return {


            "remember":
            importance>=50,


            "memories":
            memories,


            "emotion":
            emotion,


            "memory_change":
            change,


            "importance":
            importance,


            "confidence":
            min(confidence,100),


            "timestamp":
            datetime.now().isoformat()

        }