import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { SectionScreen } from "../../components/section-screen";
import { API_URL } from "../../constants/api";

type Emotion = {
  happiness: number;
  energy: number;
  trust: number;
  curiosity: number;
  comfort: number;
  excitement: number;
  stress: number;
};

type Relationship = {
  stage: string;
  closeness: number;
};

type Personality = {
  confidence?: number;
  ambition?: number;
  competitiveness?: number;
  empathy?: number;
  humor?: number;
  independence?: number;
  perfectionism?: number;
};

type Memory = {
  count?: number;
  total?: number;
};

type Learning = {
  progress?: number;
  sessions?: number;
};

type MiraiState = {
  emotion: Emotion;
  relationship: Relationship;
  personality?: Personality;
  memory?: Memory;
  learning?: Learning;
};

function clamp(value: number) {
  return Math.max(0, Math.min(100, value));
}

function getMood(emotion: Emotion) {
  const moods = [
    {
      name: "Excited",
      value: emotion.excitement,
      emoji: "✨",
    },
    {
      name: "Happy",
      value: emotion.happiness,
      emoji: "😊",
    },
    {
      name: "Curious",
      value: emotion.curiosity,
      emoji: "🌸",
    },
    {
      name: "Calm",
      value: emotion.comfort,
      emoji: "🌿",
    },
  ];

  return moods.reduce((highest, mood) =>
    mood.value > highest.value ? mood : highest
  );
}

function formatStage(stage?: string) {
  if (!stage) return "Getting to know you";

  return stage.charAt(0).toUpperCase() + stage.slice(1);
}

function getPersonalityTraits(personality?: Personality) {
  return [
    {
      name: "Confidence",
      value: personality?.confidence ?? 73,
    },
    {
      name: "Ambition",
      value: personality?.ambition ?? 90,
    },
    {
      name: "Competitiveness",
      value: personality?.competitiveness ?? 45,
    },
    {
      name: "Empathy",
      value: personality?.empathy ?? 75,
    },
    {
      name: "Humor",
      value: personality?.humor ?? 80,
    },
    {
      name: "Independence",
      value: personality?.independence ?? 80,
    },
    {
      name: "Perfectionism",
      value: personality?.perfectionism ?? 60,
    },
  ];
}

export default function MiraiScreen() {
  const [state, setState] = useState<MiraiState | null>(null);
  const [loading, setLoading] = useState(true);
  const [aboutVisible, setAboutVisible] = useState(false);

  const loadState = async () => {
    try {
      const response = await fetch(`${API_URL}/state`);

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const data = (await response.json()) as MiraiState;

      setState(data);
    } catch (error) {
      console.log("Failed to load Mirai state:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadState();
  }, []);

  const mood = state ? getMood(state.emotion) : null;

  const relationshipStage = formatStage(
    state?.relationship.stage
  );

  const closeness = clamp(
    state?.relationship.closeness ?? 0
  );

  const personalityTraits = getPersonalityTraits(
    state?.personality
  );

  const memoryCount =
    state?.memory?.count ??
    state?.memory?.total ??
    0;

  const learningProgress = clamp(
    state?.learning?.progress ?? 0
  );

  const sessions =
    state?.learning?.sessions ?? 0;

  return (
    <SectionScreen
      activeRoute="mirai"
      eyebrow="YOUR COMPANION"
      title="Mirai"
      description="Get to know her a little better."
    >
      {loading ? (
        <View style={styles.loading}>
          <ActivityIndicator />

          <Text style={styles.loadingText}>
            Loading Mirai...
          </Text>
        </View>
      ) : (
        <ScrollView
          showsVerticalScrollIndicator={false}
          contentContainerStyle={styles.content}
        >
          {/* HERO */}

          <View style={styles.heroCard}>
            <View style={styles.heroGlow} />

            <View style={styles.avatar}>
              <Text style={styles.avatarText}>🌸</Text>
            </View>

            <Text style={styles.name}>Mirai</Text>

            <Text style={styles.status}>
              {mood
                ? `${mood.emoji} Feeling ${mood.name.toLowerCase()}`
                : "🌸 Getting ready"}
            </Text>

            <View style={styles.heroDivider} />

            <View style={styles.heroStats}>
              <View style={styles.heroStat}>
                <Text style={styles.heroStatValue}>
                  {Math.round(closeness)}%
                </Text>

                <Text style={styles.heroStatLabel}>
                  closeness
                </Text>
              </View>

              <View style={styles.heroStatDivider} />

              <View style={styles.heroStat}>
                <Text style={styles.heroStatValue}>
                  {memoryCount}
                </Text>

                <Text style={styles.heroStatLabel}>
                  memories
                </Text>
              </View>

              <View style={styles.heroStatDivider} />

              <View style={styles.heroStat}>
                <Text style={styles.heroStatValue}>
                  {sessions}
                </Text>

                <Text style={styles.heroStatLabel}>
                  sessions
                </Text>
              </View>
            </View>
          </View>

          {/* BASIC INFO */}

          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>
              About her
            </Text>

            <Text style={styles.sectionCaption}>
              The basics
            </Text>
          </View>

          <View style={styles.infoCard}>
            <InfoRow
              icon="🎂"
              label="Age"
              value="19 years old"
            />

            <InfoRow
              icon="📍"
              label="From"
              value="Osaka, Japan"
            />

            <InfoRow
              icon="🎓"
              label="Studies"
              value="Economics"
            />

            <InfoRow
              icon="🏫"
              label="University"
              value="University of Michigan"
            />

            <InfoRow
              icon="🌏"
              label="Languages"
              value="Japanese & English"
            />
          </View>

          {/* MOOD */}

          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>
              Current mood
            </Text>

            <Text style={styles.sectionCaption}>
              Right now
            </Text>
          </View>

          <View style={styles.moodCard}>
            <View style={styles.moodMain}>
              <View style={styles.moodIcon}>
                <Text style={styles.moodEmoji}>
                  {mood?.emoji ?? "🌸"}
                </Text>
              </View>

              <View style={styles.moodInfo}>
                <Text style={styles.moodTitle}>
                  {mood?.name ?? "Calm"}
                </Text>

                <Text style={styles.moodDescription}>
                  {mood
                    ? "This is how Mirai is feeling at the moment."
                    : "Mirai's emotional state is unavailable."}
                </Text>
              </View>
            </View>

            <View style={styles.emotionGrid}>
              <EmotionBar
                label="Happiness"
                value={state?.emotion.happiness ?? 0}
              />

              <EmotionBar
                label="Energy"
                value={state?.emotion.energy ?? 0}
              />

              <EmotionBar
                label="Curiosity"
                value={state?.emotion.curiosity ?? 0}
              />

              <EmotionBar
                label="Comfort"
                value={state?.emotion.comfort ?? 0}
              />
            </View>
          </View>

          {/* RELATIONSHIP */}

          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>
              Your relationship
            </Text>

            <Text style={styles.sectionCaption}>
              Growing naturally
            </Text>
          </View>

          <View style={styles.card}>
            <View style={styles.relationshipTop}>
              <View>
                <Text style={styles.smallLabel}>
                  CURRENT STAGE
                </Text>

                <Text style={styles.relationshipStage}>
                  {relationshipStage}
                </Text>
              </View>

              <View style={styles.relationshipBadge}>
                <Text style={styles.relationshipBadgeText}>
                  {Math.round(closeness)}%
                </Text>
              </View>
            </View>

            <View style={styles.progressBackground}>
              <View
                style={[
                  styles.progress,
                  {
                    width: `${closeness}%`,
                  },
                ]}
              />
            </View>

            <Text style={styles.cardDescription}>
              Your connection develops through
              conversations, shared experiences and
              consistent interaction.
            </Text>
          </View>

          {/* PERSONALITY */}

          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>
              Personality
            </Text>

            <Text style={styles.sectionCaption}>
              Who Mirai is
            </Text>
          </View>

          <View style={styles.card}>
            {personalityTraits.map((trait, index) => (
              <View
                key={trait.name}
                style={[
                  styles.traitRow,
                  index === personalityTraits.length - 1 &&
                    styles.traitRowLast,
                ]}
              >
                <View style={styles.traitHeader}>
                  <Text style={styles.traitName}>
                    {trait.name}
                  </Text>

                  <Text style={styles.traitValue}>
                    {Math.round(trait.value)}
                  </Text>
                </View>

                <View style={styles.traitBackground}>
                  <View
                    style={[
                      styles.traitProgress,
                      {
                        width: `${clamp(trait.value)}%`,
                      },
                    ]}
                  />
                </View>
              </View>
            ))}
          </View>

          {/* LITTLE THINGS */}

          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>
              Little things about Mirai
            </Text>

            <Text style={styles.sectionCaption}>
              Her personality
            </Text>
          </View>

          <View style={styles.littleThingsCard}>
            <LittleThing
              emoji="😏"
              title="She likes teasing"
              description="Mirai enjoys playful teasing when she feels comfortable with someone."
            />

            <LittleThing
              emoji="💗"
              title="Compliments work on her"
              description="She likes receiving compliments, even if she sometimes gets a little shy about them."
            />

            <LittleThing
              emoji="🎵"
              title="Music is her thing"
              description="She enjoys pop music and has a soft spot for BTS and Jungkook."
            />

            <LittleThing
              emoji="🌍"
              title="She likes discovering places"
              description="New places, different cultures and spontaneous conversations easily catch her attention."
            />

            <LittleThing
              emoji="📚"
              title="She can get distracted"
              description="She is ambitious about studying, but sometimes she would rather talk than finish studying."
            />
          </View>

          {/* ENGLISH STORY */}

          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>
              Why English matters to her
            </Text>

            <Text style={styles.sectionCaption}>
              Her story
            </Text>
          </View>

          <View style={styles.storyCard}>
            <View style={styles.storyIcon}>
              <Text style={styles.storyEmoji}>🗣️</Text>
            </View>

            <Text style={styles.storyTitle}>
              She knew the rules. Speaking was harder.
            </Text>

            <Text style={styles.storyText}>
              Mirai had English tutoring for several years.
              She understood grammar and could do well in
              class, but natural conversations were much
              harder.
            </Text>

            <Text style={styles.storyText}>
              That experience changed how she thinks about
              language learning. For Mirai, speaking,
              making mistakes, joking around and simply
              spending time together are all part of learning.
            </Text>

            <View style={styles.storyQuoteBox}>
              <Text style={styles.storyQuote}>
                "You don't really learn a language until
                you start living in it."
              </Text>
            </View>
          </View>

          {/* MEMORY */}

          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>
              Memory
            </Text>

            <Text style={styles.sectionCaption}>
              What Mirai remembers
            </Text>
          </View>

          <View style={styles.memoryCard}>
            <View style={styles.memoryIcon}>
              <Text style={styles.memoryEmoji}>
                🧠
              </Text>
            </View>

            <View style={styles.memoryInfo}>
              <Text style={styles.memoryTitle}>
                {memoryCount} memories
              </Text>

              <Text style={styles.memoryDescription}>
                Important details from your conversations
                can become part of Mirai's long-term memory.
              </Text>
            </View>

            <Text style={styles.memoryArrow}>
              ›
            </Text>
          </View>

          {/* LEARNING */}

          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>
              Learning together
            </Text>

            <Text style={styles.sectionCaption}>
              Your shared progress
            </Text>
          </View>

          <View style={styles.learningCard}>
            <View style={styles.learningIcon}>
              <Text style={styles.learningEmoji}>
                📚
              </Text>
            </View>

            <View style={styles.learningInfo}>
              <Text style={styles.learningTitle}>
                {Math.round(learningProgress)}% progress
              </Text>

              <Text style={styles.learningDescription}>
                Mirai adapts the learning experience based
                on your progress.
              </Text>

              <View style={styles.progressBackground}>
                <View
                  style={[
                    styles.progress,
                    {
                      width: `${learningProgress}%`,
                    },
                  ]}
                />
              </View>
            </View>
          </View>

          {/* ABOUT BUTTON */}

          <Pressable
            style={({ pressed }) => [
              styles.aboutButton,
              pressed && styles.buttonPressed,
            ]}
            onPress={() =>
              setAboutVisible(!aboutVisible)
            }
          >
            <Text style={styles.aboutButtonIcon}>
              ✨
            </Text>

            <Text style={styles.aboutButtonText}>
              {aboutVisible
                ? "Hide Mirai's story"
                : "About Mirai"}
            </Text>
          </Pressable>

          {/* ABOUT */}

          {aboutVisible && (
            <View style={styles.aboutCard}>
              <View style={styles.aboutHeader}>
                <Text style={styles.aboutTitle}>
                  About Mirai
                </Text>

                <Pressable
                  onPress={() => setAboutVisible(false)}
                  hitSlop={10}
                >
                  <Text style={styles.closeButton}>
                    ×
                  </Text>
                </Pressable>
              </View>

              <Text style={styles.aboutText}>
                Mirai is a 19-year-old university student
                from Osaka, Japan. She studies economics at
                the University of Michigan.
              </Text>

              <Text style={styles.aboutText}>
                She grew up in a comfortable family in Osaka.
                Her background gave her a stable environment
                while also encouraging her to become
                independent and curious about the world.
              </Text>

              <Text style={styles.aboutText}>
                Mirai chose to study in the United States
                because she wanted to experience a different
                culture and become more confident speaking
                English.
              </Text>

              <Text style={styles.aboutText}>
                She had English tutoring for several years.
                Grammar was never really the problem. Natural
                conversation was. She could understand what
                she was supposed to say, but actually talking
                spontaneously was much harder.
              </Text>

              <Text style={styles.aboutText}>
                That is one of the reasons she enjoys learning
                languages together with someone else. She
                believes mistakes, jokes, conversations and
                everyday interaction are just as important as
                studying rules.
              </Text>

              <Text style={styles.aboutText}>
                Mirai is confident, ambitious and independent.
                She likes joking around and teasing people she
                feels close to. She also genuinely cares about
                people who matter to her.
              </Text>

              <Text style={styles.aboutText}>
                She can be a little competitive, but she is not
                obsessed with winning. She has high ambitions
                and expects a lot from herself, although she
                knows how to relax and have fun.
              </Text>

              <Text style={styles.aboutText}>
                Outside university, she enjoys pop music,
                exploring new places, talking with friends and
                occasionally getting distracted from studying.
              </Text>

              <View style={styles.aboutDivider} />

              <Text style={styles.aboutQuote}>
                "The future is more fun when you don't have to
                figure it out alone."
              </Text>
            </View>
          )}

          <View style={styles.bottomSpace} />
        </ScrollView>
      )}
    </SectionScreen>
  );
}

function EmotionBar({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <View style={styles.emotionItem}>
      <View style={styles.emotionHeader}>
        <Text style={styles.emotionLabel}>
          {label}
        </Text>

        <Text style={styles.emotionValue}>
          {Math.round(value)}%
        </Text>
      </View>

      <View style={styles.emotionBackground}>
        <View
          style={[
            styles.emotionProgress,
            {
              width: `${clamp(value)}%`,
            },
          ]}
        />
      </View>
    </View>
  );
}

function InfoRow({
  icon,
  label,
  value,
}: {
  icon: string;
  label: string;
  value: string;
}) {
  return (
    <View style={styles.infoRow}>
      <View style={styles.infoIcon}>
        <Text style={styles.infoEmoji}>
          {icon}
        </Text>
      </View>

      <View style={styles.infoText}>
        <Text style={styles.infoLabel}>
          {label}
        </Text>

        <Text style={styles.infoValue}>
          {value}
        </Text>
      </View>
    </View>
  );
}

function LittleThing({
  emoji,
  title,
  description,
}: {
  emoji: string;
  title: string;
  description: string;
}) {
  return (
    <View style={styles.littleThing}>
      <View style={styles.littleThingIcon}>
        <Text style={styles.littleThingEmoji}>
          {emoji}
        </Text>
      </View>

      <View style={styles.littleThingInfo}>
        <Text style={styles.littleThingTitle}>
          {title}
        </Text>

        <Text style={styles.littleThingDescription}>
          {description}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  content: {
    paddingBottom: 20,
  },

  loading: {
    alignItems: "center",
    paddingVertical: 50,
  },

  loadingText: {
    marginTop: 10,
    fontSize: 13,
    color: "#8E858A",
  },

  heroCard: {
    position: "relative",
    alignItems: "center",
    paddingTop: 30,
    paddingBottom: 20,
    paddingHorizontal: 20,
    borderRadius: 28,
    backgroundColor: "#FFF7FA",
    marginBottom: 24,
    overflow: "hidden",
  },

  heroGlow: {
    position: "absolute",
    width: 180,
    height: 180,
    borderRadius: 90,
    backgroundColor: "#FFEAF3",
    top: -85,
    opacity: 0.7,
  },

  avatar: {
    width: 86,
    height: 86,
    borderRadius: 43,
    backgroundColor: "#FFEAF3",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 13,
  },

  avatarText: {
    fontSize: 43,
  },

  name: {
    fontSize: 27,
    fontWeight: "700",
    color: "#292529",
  },

  status: {
    marginTop: 5,
    fontSize: 14,
    color: "#8E858A",
  },

  heroDivider: {
    width: "100%",
    height: 1,
    backgroundColor: "#F0DDE5",
    marginTop: 22,
    marginBottom: 16,
  },

  heroStats: {
    width: "100%",
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-around",
  },

  heroStat: {
    alignItems: "center",
    flex: 1,
  },

  heroStatValue: {
    fontSize: 17,
    fontWeight: "700",
    color: "#292529",
  },

  heroStatLabel: {
    marginTop: 3,
    fontSize: 11,
    color: "#9A9095",
  },

  heroStatDivider: {
    width: 1,
    height: 25,
    backgroundColor: "#EBDDE3",
  },

  sectionHeader: {
    flexDirection: "row",
    alignItems: "baseline",
    justifyContent: "space-between",
    marginBottom: 11,
  },

  sectionTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: "#292529",
  },

  sectionCaption: {
    fontSize: 11,
    color: "#A39A9F",
  },

  infoCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 22,
    borderWidth: 1,
    borderColor: "#F1ECEF",
    padding: 16,
    marginBottom: 24,
  },

  infoRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 8,
  },

  infoIcon: {
    width: 42,
    height: 42,
    borderRadius: 14,
    backgroundColor: "#FFF3F7",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 12,
  },

  infoEmoji: {
    fontSize: 20,
  },

  infoText: {
    flex: 1,
  },

  infoLabel: {
    fontSize: 11,
    color: "#9A9095",
    marginBottom: 2,
  },

  infoValue: {
    fontSize: 14,
    fontWeight: "600",
    color: "#292529",
  },

  moodCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 22,
    borderWidth: 1,
    borderColor: "#F1ECEF",
    padding: 18,
    marginBottom: 24,
  },

  moodMain: {
    flexDirection: "row",
    alignItems: "center",
  },

  moodIcon: {
    width: 54,
    height: 54,
    borderRadius: 18,
    backgroundColor: "#FFF3F7",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 13,
  },

  moodEmoji: {
    fontSize: 27,
  },

  moodInfo: {
    flex: 1,
  },

  moodTitle: {
    fontSize: 17,
    fontWeight: "700",
    color: "#292529",
  },

  moodDescription: {
    fontSize: 12,
    lineHeight: 17,
    color: "#8E858A",
    marginTop: 3,
  },

  emotionGrid: {
    marginTop: 18,
  },

  emotionItem: {
    marginBottom: 10,
  },

  emotionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 5,
  },

  emotionLabel: {
    fontSize: 11,
    color: "#8E858A",
  },

  emotionValue: {
    fontSize: 11,
    fontWeight: "600",
    color: "#FF6FA7",
  },

  emotionBackground: {
    height: 5,
    borderRadius: 3,
    backgroundColor: "#F3EEF0",
    overflow: "hidden",
  },

  emotionProgress: {
    height: "100%",
    borderRadius: 3,
    backgroundColor: "#FFB0CD",
  },

  card: {
    backgroundColor: "#FFFFFF",
    borderRadius: 22,
    padding: 18,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: "#F1ECEF",
  },

  relationshipTop: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },

  smallLabel: {
    fontSize: 10,
    fontWeight: "700",
    letterSpacing: 0.8,
    color: "#FF6FA7",
    marginBottom: 4,
  },

  relationshipStage: {
    fontSize: 19,
    fontWeight: "700",
    color: "#292529",
  },

  relationshipBadge: {
    paddingHorizontal: 11,
    paddingVertical: 7,
    borderRadius: 12,
    backgroundColor: "#FFF3F7",
  },

  relationshipBadgeText: {
    fontSize: 12,
    fontWeight: "700",
    color: "#FF6FA7",
  },

  progressBackground: {
    height: 7,
    borderRadius: 4,
    backgroundColor: "#F3EEF0",
    marginTop: 15,
    overflow: "hidden",
  },

  progress: {
    height: "100%",
    borderRadius: 4,
    backgroundColor: "#FF8FBA",
  },

  cardDescription: {
    fontSize: 12,
    lineHeight: 18,
    color: "#8E858A",
    marginTop: 10,
  },

  traitRow: {
    marginBottom: 15,
  },

  traitRowLast: {
    marginBottom: 0,
  },

  traitHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 6,
  },

  traitName: {
    fontSize: 12,
    color: "#6F666B",
  },

  traitValue: {
    fontSize: 11,
    fontWeight: "600",
    color: "#FF6FA7",
  },

  traitBackground: {
    height: 6,
    borderRadius: 3,
    backgroundColor: "#F3EEF0",
    overflow: "hidden",
  },

  traitProgress: {
    height: "100%",
    borderRadius: 3,
    backgroundColor: "#FFB0CD",
  },

  littleThingsCard: {
    backgroundColor: "#FFF7FA",
    borderRadius: 22,
    padding: 16,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: "#F1DCE5",
  },

  littleThing: {
    flexDirection: "row",
    alignItems: "flex-start",
    marginBottom: 16,
  },

  littleThingIcon: {
    width: 43,
    height: 43,
    borderRadius: 14,
    backgroundColor: "#FFFFFF",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 12,
  },

  littleThingEmoji: {
    fontSize: 20,
  },

  littleThingInfo: {
    flex: 1,
  },

  littleThingTitle: {
    fontSize: 13,
    fontWeight: "700",
    color: "#292529",
    marginBottom: 3,
  },

  littleThingDescription: {
    fontSize: 12,
    lineHeight: 17,
    color: "#8E858A",
  },

  storyCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 22,
    borderWidth: 1,
    borderColor: "#F1ECEF",
    padding: 18,
    marginBottom: 24,
  },

  storyIcon: {
    width: 52,
    height: 52,
    borderRadius: 17,
    backgroundColor: "#FFF3F7",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 13,
  },

  storyEmoji: {
    fontSize: 25,
  },

  storyTitle: {
    fontSize: 17,
    lineHeight: 23,
    fontWeight: "700",
    color: "#292529",
    marginBottom: 9,
  },

  storyText: {
    fontSize: 13,
    lineHeight: 19,
    color: "#756C71",
    marginBottom: 9,
  },

  storyQuoteBox: {
    backgroundColor: "#FFF7FA",
    borderRadius: 15,
    padding: 13,
    marginTop: 5,
  },

  storyQuote: {
    fontSize: 12,
    lineHeight: 18,
    color: "#FF6FA7",
    fontStyle: "italic",
    textAlign: "center",
  },

  memoryCard: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#FFF7FA",
    borderRadius: 22,
    padding: 16,
    marginBottom: 24,
  },

  memoryIcon: {
    width: 52,
    height: 52,
    borderRadius: 17,
    backgroundColor: "#FFFFFF",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 13,
  },

  memoryEmoji: {
    fontSize: 25,
  },

  memoryInfo: {
    flex: 1,
  },

  memoryTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: "#292529",
  },

  memoryDescription: {
    fontSize: 12,
    lineHeight: 17,
    color: "#8E858A",
    marginTop: 3,
  },

  memoryArrow: {
    fontSize: 27,
    color: "#B7ADB2",
    marginLeft: 8,
  },

  learningCard: {
    flexDirection: "row",
    backgroundColor: "#FFFFFF",
    borderRadius: 22,
    borderWidth: 1,
    borderColor: "#F1ECEF",
    padding: 16,
    marginBottom: 24,
  },

  learningIcon: {
    width: 52,
    height: 52,
    borderRadius: 17,
    backgroundColor: "#FFF3F7",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 13,
  },

  learningEmoji: {
    fontSize: 24,
  },

  learningInfo: {
    flex: 1,
  },

  learningTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: "#292529",
  },

  learningDescription: {
    fontSize: 12,
    lineHeight: 17,
    color: "#8E858A",
    marginTop: 3,
  },

  aboutButton: {
    width: "100%",
    height: 55,
    borderRadius: 18,
    backgroundColor: "#FFF5F8",
    borderWidth: 1,
    borderColor: "#F5DCE6",
    justifyContent: "center",
    alignItems: "center",
    flexDirection: "row",
    marginBottom: 14,
  },

  aboutButtonIcon: {
    fontSize: 18,
    marginRight: 8,
  },

  aboutButtonText: {
    color: "#5E555A",
    fontSize: 15,
    fontWeight: "600",
  },

  buttonPressed: {
    opacity: 0.72,
    transform: [{ scale: 0.98 }],
  },

  aboutCard: {
    backgroundColor: "#FFF7FA",
    borderRadius: 22,
    padding: 18,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: "#F1DCE5",
  },

  aboutHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 10,
  },

  aboutTitle: {
    fontSize: 17,
    fontWeight: "700",
    color: "#292529",
  },

  closeButton: {
    fontSize: 25,
    lineHeight: 25,
    color: "#9A8F94",
  },

  aboutText: {
    fontSize: 13,
    lineHeight: 19,
    color: "#756C71",
    marginBottom: 9,
  },

  aboutDivider: {
    height: 1,
    backgroundColor: "#F0DDE5",
    marginVertical: 8,
  },

  aboutQuote: {
    fontSize: 13,
    lineHeight: 19,
    color: "#FF6FA7",
    fontStyle: "italic",
    textAlign: "center",
    marginTop: 4,
  },

  bottomSpace: {
    height: 30,
  },
});