import { useCallback, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { router, useFocusEffect } from "expo-router";

import { SectionScreen } from "../../components/section-screen";
import { authFetch } from "../../auth/auth";

type Skill = {
  value?: number;
  evidence_count?: number;
};

type LearningProfile = {
  learner?: {
    skills?: Record<string, Record<string, Skill>>;
  };

  analysis?: {
    goal?: {
      goal?: string;
    };

    state?: {
      confidence?: number;
      [key: string]: unknown;
    };

    difficulty?: {
      difficulty?: string;
    };

    mode?: {
      mode?: string;
    };
  };

  sessions?: unknown[];

  strategy?: {
    goal?: string;
  };
};

type Achievement = {
  id: string;
  title: string;
  description: string;
  icon: string;
  unlocked: boolean;
};

type GamificationData = {
  xp: number;
  level: number;
  xp_to_next_level: number;
  streak: number;
  daily_goal: {
    target: number;
    progress: number;
    completed: boolean;
  };
  achievements: Achievement[];
};

function clamp(value: number): number {
  if (!Number.isFinite(value)) {
    return 0;
  }

  return Math.max(0, Math.min(100, value));
}

function formatTitle(value: unknown): string {
  if (value === null || value === undefined || value === "") {
    return "Learning";
  }

  return String(value)
    .replace(/\_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function getProgress(profile: LearningProfile): number {
  const skills = profile.learner?.skills;

  if (!skills || typeof skills !== "object") {
    return 0;
  }

  const values: number[] = [];

  Object.values(skills).forEach((category) => {
    if (!category || typeof category !== "object") {
      return;
    }

    Object.values(category).forEach((skill) => {
      if (!skill || typeof skill !== "object") {
        return;
      }

      const value = skill.value;
      const evidence = skill.evidence_count;

      if (
        typeof value === "number" &&
        Number.isFinite(value) &&
        typeof evidence === "number" &&
        Number.isFinite(evidence) &&
        evidence > 0
      ) {
        values.push(clamp(value));
      }
    });
  });

  if (values.length === 0) {
    return 0;
  }

  const average =
    values.reduce((sum, value) => sum + value, 0) / values.length;

  return Math.round(clamp(average));
}

function getCEFR(progress: number): string {
  const value = clamp(progress);

  if (value < 20) return "A1";
  if (value < 40) return "A2";
  if (value < 60) return "B1";
  if (value < 75) return "B2";
  if (value < 90) return "C1";

  return "C2";
}

function getNextLevel(level: string): string {
  const levels: Record<string, string> = {
    A1: "A2",
    A2: "B1",
    B1: "B2",
    B2: "C1",
    C1: "C2",
    C2: "C2",
  };

  return levels[level] ?? "B1";
}

function getLevelProgress(
  progress: number,
  level: string
): number {
  const ranges: Record<string, [number, number]> = {
    A1: [0, 20],
    A2: [20, 40],
    B1: [40, 60],
    B2: [60, 75],
    C1: [75, 90],
    C2: [90, 100],
  };

  if (level === "C2") {
    return 100;
  }

  const [start, end] = ranges[level] ?? [0, 100];

  if (end <= start) {
    return 0;
  }

  return clamp(
    Math.round(
      ((clamp(progress) - start) / (end - start)) * 100
    )
  );
}

function getConfidenceLabel(confidence: number): string {
  const value = clamp(confidence);

  if (value < 25) {
    return "Just getting started";
  }

  if (value < 50) {
    return "Building confidence";
  }

  if (value < 75) {
    return "Growing confidence";
  }

  return "Feeling confident";
}

function getDifficultyLabel(value: unknown): string {
  if (!value) {
    return "Adaptive";
  }

  const formatted = formatTitle(value);

  return formatted === "Learning" ? "Adaptive" : formatted;
}

function getModeLabel(value: unknown): string {
  if (!value) {
    return "Balanced";
  }

  const formatted = formatTitle(value);

  return formatted === "Learning" ? "Balanced" : formatted;
}

export default function ProfileScreen() {
  const [profile, setProfile] =
    useState<LearningProfile | null>(null);

  const [gamification, setGamification] =
    useState<GamificationData | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadProfile = useCallback(async () => {
    try {
      setError(null);
      setLoading(true);

      const [profileResponse, gamificationResponse] =
        await Promise.all([
          authFetch("/learning/profile"),
          authFetch("/gamification"),
        ]);

      if (!profileResponse.ok) {
        throw new Error(
          `Request failed with status ${profileResponse.status}`
        );
      }

      if (!gamificationResponse.ok) {
        throw new Error(
          `Gamification request failed with status ${gamificationResponse.status}`
        );
      }

      const data =
        (await profileResponse.json()) as LearningProfile;

      const gamificationData =
        (await gamificationResponse.json()) as GamificationData;

      console.log("Learning profile updated:", data);
      console.log("Gamification updated:", gamificationData);

      setProfile(data);
      setGamification(gamificationData);
    } catch (error) {
      console.log("Failed to load profile:", error);

      setError(
        error instanceof Error
          ? error.message
          : "Failed to load profile"
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      loadProfile();
    }, [loadProfile])
  );

  const progress = profile
    ? getProgress(profile)
    : 0;

  const level = getCEFR(progress);
  const nextLevel = getNextLevel(level);

  const levelProgress = getLevelProgress(
    progress,
    level
  );

  const goal =
    profile?.analysis?.goal?.goal ??
    profile?.strategy?.goal ??
    "English";

  const sessions = Array.isArray(profile?.sessions)
    ? profile.sessions.length
    : 0;

  const confidence = clamp(
    typeof profile?.analysis?.state?.confidence === "number"
      ? profile.analysis.state.confidence
      : 0
  );

  const difficulty = getDifficultyLabel(
    profile?.analysis?.difficulty?.difficulty
  );

  const mode = getModeLabel(
    profile?.analysis?.mode?.mode
  );

  const gamificationXP = gamification?.xp ?? 0;
  const gamificationLevel = gamification?.level ?? 1;
  const gamificationStreak = gamification?.streak ?? 0;

  const dailyGoalTarget =
    gamification?.daily_goal.target ?? 5;

  const dailyGoalProgress =
    gamification?.daily_goal.progress ?? 0;

  const dailyGoalCompleted =
    gamification?.daily_goal.completed ?? false;

  const dailyGoalPercent =
    dailyGoalTarget > 0
      ? Math.min(
          100,
          Math.round(
            (dailyGoalProgress / dailyGoalTarget) * 100
          )
        )
      : 0;

  const xpProgress = Math.min(
    100,
    Math.max(0, gamificationXP)
  );

  return (
    <SectionScreen
      activeRoute="profile"
      eyebrow="PROFILE"
      title="Your journey"
      description="Everything about your learning journey in one place."
    >
      {loading ? (
        <View style={styles.loading}>
          <ActivityIndicator />

          <Text style={styles.loadingText}>
            Loading your profile...
          </Text>
        </View>
      ) : error ? (
        <View style={styles.errorCard}>
          <Text style={styles.errorTitle}>
            Couldn't load profile
          </Text>

          <Text style={styles.errorText}>
            {error}
          </Text>

          <Pressable
            style={styles.retryButton}
            onPress={loadProfile}
          >
            <Text style={styles.retryText}>
              Try again
            </Text>
          </Pressable>
        </View>
      ) : (
        <>
          {/* PROFILE */}

          <View style={styles.profileCard}>
            <View style={styles.avatar}>
              <Text style={styles.avatarText}>
                👤
              </Text>
            </View>

            <Text style={styles.name}>
              You
            </Text>

            <Text style={styles.subtitle}>
              English learner
            </Text>

            <View style={styles.profileBadge}>
              <Text style={styles.profileBadgeText}>
                {level} learner
              </Text>
            </View>
          </View>

          {/* GAMIFICATION */}

          <Text style={styles.sectionTitle}>
            Your achievements
          </Text>

          <View style={styles.gamificationCard}>
            <View style={styles.gamificationHeader}>
              <View style={styles.miraiLevelIcon}>
                <Text style={styles.miraiLevelEmoji}>
                  🌸
                </Text>
              </View>

              <View style={styles.gamificationHeaderInfo}>
                <Text style={styles.gamificationLabel}>
                  MIRAI LEVEL
                </Text>

                <Text style={styles.gamificationLevel}>
                  Level {gamificationLevel}
                </Text>

                <Text style={styles.gamificationXPText}>
                  {gamificationXP} XP
                </Text>
              </View>

              <View style={styles.streakBadge}>
                <Text style={styles.streakEmoji}>
                  🔥
                </Text>

                <Text style={styles.streakValue}>
                  {gamificationStreak}
                </Text>

                <Text style={styles.streakLabel}>
                  day streak
                </Text>
              </View>
            </View>

            <View style={styles.xpProgressBackground}>
              <View
                style={[
                  styles.xpProgress,
                  {
                    width: `${xpProgress}%`,
                  },
                ]}
              />
            </View>

            <View style={styles.xpFooter}>
              <Text style={styles.xpFooterText}>
                {gamificationXP} / 100 XP
              </Text>

              <Text style={styles.xpNextText}>
                {gamification?.xp_to_next_level ?? 100} XP to next level
              </Text>
            </View>
          </View>

          {/* DAILY GOAL */}

          <View style={styles.dailyGoalCard}>
            <View style={styles.dailyGoalHeader}>
              <View>
                <Text style={styles.dailyGoalLabel}>
                  TODAY'S GOAL
                </Text>

                <Text style={styles.dailyGoalTitle}>
                  {dailyGoalCompleted
                    ? "Goal completed! 🎉"
                    : "Keep going!"}
                </Text>
              </View>

              <Text style={styles.dailyGoalCount}>
                {dailyGoalProgress}/{dailyGoalTarget}
              </Text>
            </View>

            <View style={styles.dailyGoalProgressBackground}>
              <View
                style={[
                  styles.dailyGoalProgress,
                  {
                    width: `${dailyGoalPercent}%`,
                  },
                ]}
              />
            </View>

            <Text style={styles.dailyGoalDescription}>
              {dailyGoalCompleted
                ? "You completed today's learning goal."
                : `${dailyGoalTarget - dailyGoalProgress} more ${
                    dailyGoalTarget - dailyGoalProgress === 1
                      ? "activity"
                      : "activities"
                  } to complete today's goal.`}
            </Text>
          </View>

          {/* ACHIEVEMENTS */}

          <View style={styles.achievementsCard}>
            <View style={styles.achievementsHeader}>
              <View>
                <Text style={styles.achievementsTitle}>
                  Achievements
                </Text>

                <Text style={styles.achievementsSubtitle}>
                  Small steps become big progress.
                </Text>
              </View>

              <Text style={styles.achievementCount}>
                {gamification?.achievements.filter(
                  (achievement) => achievement.unlocked
                ).length ?? 0}
                /
                {gamification?.achievements.length ?? 0}
              </Text>
            </View>

            <View style={styles.achievementsList}>
              {gamification?.achievements.map(
                (achievement, index) => (
                  <View
                    key={achievement.id}
                    style={[
                      styles.achievementRow,
                      index > 0 &&
                        styles.achievementRowBorder,
                      !achievement.unlocked &&
                        styles.achievementLocked,
                    ]}
                  >
                    <View
                      style={[
                        styles.achievementIcon,
                        !achievement.unlocked &&
                          styles.achievementIconLocked,
                      ]}
                    >
                      <Text
                        style={[
                          styles.achievementEmoji,
                          !achievement.unlocked &&
                            styles.achievementEmojiLocked,
                        ]}
                      >
                        {achievement.icon}
                      </Text>
                    </View>

                    <View style={styles.achievementInfo}>
                      <View style={styles.achievementTitleRow}>
                        <Text
                          style={[
                            styles.achievementTitle,
                            !achievement.unlocked &&
                              styles.achievementTitleLocked,
                          ]}
                        >
                          {achievement.title}
                        </Text>

                        {achievement.unlocked && (
                          <Text style={styles.unlockedText}>
                            ✓
                          </Text>
                        )}
                      </View>

                      <Text
                        style={[
                          styles.achievementDescription,
                          !achievement.unlocked &&
                            styles.achievementDescriptionLocked,
                        ]}
                      >
                        {achievement.description}
                      </Text>
                    </View>
                  </View>
                )
              )}
            </View>
          </View>

          {/* LEVEL */}

          <Text style={styles.sectionTitle}>
            Your level
          </Text>

          <View style={styles.levelCard}>
            <View style={styles.levelHeader}>
              <View>
                <Text style={styles.levelLabel}>
                  CEFR LEVEL
                </Text>

                <Text style={styles.level}>
                  {level}
                </Text>
              </View>

              <View style={styles.levelFlower}>
                <Text style={styles.flower}>
                  🌸
                </Text>
              </View>
            </View>

            <View style={styles.progressBackground}>
              <View
                style={[
                  styles.progress,
                  {
                    width: `${levelProgress}%`,
                  },
                ]}
              />
            </View>

            <View style={styles.levelFooter}>
              <Text style={styles.levelProgressText}>
                {levelProgress}% through {level}
              </Text>

              {level !== "C2" && (
                <Text style={styles.nextLevel}>
                  Next: {nextLevel}
                </Text>
              )}
            </View>

            <Text style={styles.description}>
              {level === "C2"
                ? "You've reached the highest CEFR level."
                : `Keep learning to move towards ${nextLevel}.`}
            </Text>
          </View>

          {/* PROGRESS */}

          <Text style={styles.sectionTitle}>
            Your progress
          </Text>

          <View style={styles.statsRow}>
            <View style={styles.statCard}>
              <Text style={styles.statIcon}>
                📚
              </Text>

              <Text style={styles.statValue}>
                {sessions}
              </Text>

              <Text style={styles.statLabel}>
                sessions
              </Text>
            </View>

            <View
              style={[
                styles.statCard,
                styles.statCardSecond,
              ]}
            >
              <Text style={styles.statIcon}>
                🌸
              </Text>

              <Text style={styles.statValue}>
                {progress}%
              </Text>

              <Text style={styles.statLabel}>
                progress
              </Text>
            </View>
          </View>

          {/* LEARNING STATE */}

          <Text style={styles.sectionTitle}>
            Learning state
          </Text>

          <View style={styles.stateCard}>
            <View style={styles.stateHeader}>
              <View>
                <Text style={styles.stateLabel}>
                  CONFIDENCE
                </Text>

                <Text style={styles.stateTitle}>
                  {getConfidenceLabel(confidence)}
                </Text>
              </View>

              <Text style={styles.stateValue}>
                {Math.round(confidence)}%
              </Text>
            </View>

            <View style={styles.progressBackground}>
              <View
                style={[
                  styles.progress,
                  {
                    width: `${confidence}%`,
                  },
                ]}
              />
            </View>

            <Text style={styles.stateDescription}>
              Mirai adjusts your learning experience
              based on how you are progressing.
            </Text>
          </View>

          {/* PREFERENCES */}

          <View style={styles.preferenceRow}>
            <View style={styles.preferenceCard}>
              <Text style={styles.preferenceIcon}>
                🎚️
              </Text>

              <Text style={styles.preferenceLabel}>
                DIFFICULTY
              </Text>

              <Text style={styles.preferenceValue}>
                {difficulty}
              </Text>
            </View>

            <View
              style={[
                styles.preferenceCard,
                styles.preferenceCardSecond,
              ]}
            >
              <Text style={styles.preferenceIcon}>
                🧠
              </Text>

              <Text style={styles.preferenceLabel}>
                MODE
              </Text>

              <Text style={styles.preferenceValue}>
                {mode}
              </Text>
            </View>
          </View>

          {/* GOAL */}

          <Text style={styles.sectionTitle}>
            Current goal
          </Text>

          <View style={styles.goalCard}>
            <View style={styles.goalIcon}>
              <Text style={styles.goalEmoji}>
                🎯
              </Text>
            </View>

            <View style={styles.goalInfo}>
              <Text style={styles.goalLabel}>
                CURRENT GOAL
              </Text>

              <Text style={styles.goalTitle}>
                {formatTitle(goal)}
              </Text>

              <Text style={styles.goalDescription}>
                Mirai uses this goal to personalize
                your learning experience.
              </Text>
            </View>
          </View>

          {/* SETTINGS */}

          <Text style={styles.sectionTitle}>
            App
          </Text>

          <Pressable
            style={({ pressed }) => [
              styles.settingsButton,
              pressed && styles.settingsButtonPressed,
            ]}
            onPress={() => router.push("./settings")}
          >
            <View style={styles.settingsIcon}>
              <Text style={styles.settingsEmoji}>
                ⚙️
              </Text>
            </View>

            <View style={styles.settingsInfo}>
              <Text style={styles.settingsTitle}>
                Settings
              </Text>

              <Text style={styles.settingsDescription}>
                Preferences and app settings
              </Text>
            </View>

            <Text style={styles.arrow}>
              ›
            </Text>
          </Pressable>
        </>
      )}
    </SectionScreen>
  );
}

const styles = StyleSheet.create({
  loading: {
    alignItems: "center",
    paddingVertical: 40,
  },

  loadingText: {
    marginTop: 10,
    fontSize: 13,
    color: "#8E858A",
  },

  errorCard: {
    backgroundColor: "#FFF7FA",
    borderRadius: 20,
    padding: 20,
    marginBottom: 20,
  },

  errorTitle: {
    fontSize: 17,
    fontWeight: "700",
    color: "#292529",
  },

  errorText: {
    marginTop: 6,
    fontSize: 13,
    lineHeight: 19,
    color: "#8E858A",
  },

  retryButton: {
    alignSelf: "flex-start",
    marginTop: 14,
    paddingVertical: 9,
    paddingHorizontal: 16,
    borderRadius: 12,
    backgroundColor: "#FF8FBA",
  },

  retryText: {
    color: "#FFFFFF",
    fontWeight: "600",
  },

  profileCard: {
    alignItems: "center",
    backgroundColor: "#FFF7FA",
    borderRadius: 24,
    paddingVertical: 28,
    marginBottom: 24,
  },

  avatar: {
    width: 76,
    height: 76,
    borderRadius: 38,
    backgroundColor: "#FFEAF3",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 12,
  },

  avatarText: {
    fontSize: 34,
  },

  name: {
    fontSize: 24,
    fontWeight: "700",
    color: "#292529",
  },

  subtitle: {
    marginTop: 4,
    fontSize: 14,
    color: "#8E858A",
  },

  profileBadge: {
    marginTop: 12,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    backgroundColor: "#FFFFFF",
  },

  profileBadgeText: {
    fontSize: 11,
    fontWeight: "600",
    color: "#FF6FA7",
  },

  sectionTitle: {
    marginBottom: 12,
    fontSize: 18,
    fontWeight: "700",
    color: "#292529",
  },

  /* GAMIFICATION */

  gamificationCard: {
    backgroundColor: "#FFF7FA",
    borderRadius: 22,
    padding: 18,
    marginBottom: 12,
  },

  gamificationHeader: {
    flexDirection: "row",
    alignItems: "center",
  },

  miraiLevelIcon: {
    width: 54,
    height: 54,
    borderRadius: 18,
    backgroundColor: "#FFFFFF",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 12,
  },

  miraiLevelEmoji: {
    fontSize: 28,
  },

  gamificationHeaderInfo: {
    flex: 1,
  },

  gamificationLabel: {
    fontSize: 9,
    fontWeight: "700",
    letterSpacing: 0.8,
    color: "#FF6FA7",
  },

  gamificationLevel: {
    marginTop: 2,
    fontSize: 19,
    fontWeight: "700",
    color: "#292529",
  },

  gamificationXPText: {
    marginTop: 2,
    fontSize: 12,
    color: "#8E858A",
  },

  streakBadge: {
    alignItems: "center",
    minWidth: 62,
    paddingVertical: 7,
    paddingHorizontal: 7,
    borderRadius: 15,
    backgroundColor: "#FFFFFF",
  },

  streakEmoji: {
    fontSize: 18,
  },

  streakValue: {
    marginTop: 1,
    fontSize: 18,
    fontWeight: "700",
    color: "#292529",
  },

  streakLabel: {
    marginTop: 1,
    fontSize: 8,
    color: "#8E858A",
  },

  xpProgressBackground: {
    height: 9,
    marginTop: 17,
    borderRadius: 5,
    backgroundColor: "#F0E6EA",
    overflow: "hidden",
  },

  xpProgress: {
    height: "100%",
    borderRadius: 5,
    backgroundColor: "#FF8FBA",
  },

  xpFooter: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginTop: 8,
  },

  xpFooterText: {
    fontSize: 10,
    fontWeight: "600",
    color: "#8E858A",
  },

  xpNextText: {
    fontSize: 10,
    color: "#A39A9F",
  },

  dailyGoalCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 20,
    borderWidth: 1,
    borderColor: "#F1ECEF",
    padding: 17,
    marginBottom: 12,
  },

  dailyGoalHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },

  dailyGoalLabel: {
    fontSize: 9,
    fontWeight: "700",
    letterSpacing: 0.8,
    color: "#FF6FA7",
  },

  dailyGoalTitle: {
    marginTop: 3,
    fontSize: 16,
    fontWeight: "700",
    color: "#292529",
  },

  dailyGoalCount: {
    fontSize: 22,
    fontWeight: "700",
    color: "#292529",
  },

  dailyGoalProgressBackground: {
    height: 7,
    marginTop: 13,
    borderRadius: 4,
    backgroundColor: "#F0E6EA",
    overflow: "hidden",
  },

  dailyGoalProgress: {
    height: "100%",
    borderRadius: 4,
    backgroundColor: "#FF8FBA",
  },

  dailyGoalDescription: {
    marginTop: 8,
    fontSize: 11,
    lineHeight: 16,
    color: "#8E858A",
  },

  achievementsCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 20,
    borderWidth: 1,
    borderColor: "#F1ECEF",
    padding: 17,
    marginBottom: 24,
  },

  achievementsHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 4,
  },

  achievementsTitle: {
    fontSize: 17,
    fontWeight: "700",
    color: "#292529",
  },

  achievementsSubtitle: {
    marginTop: 3,
    fontSize: 11,
    color: "#8E858A",
  },

  achievementCount: {
    fontSize: 13,
    fontWeight: "700",
    color: "#FF6FA7",
  },

  achievementsList: {
    marginTop: 8,
  },

  achievementRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 12,
  },

  achievementRowBorder: {
    borderTopWidth: 1,
    borderTopColor: "#F3EEF0",
  },

  achievementLocked: {
    opacity: 0.48,
  },

  achievementIcon: {
    width: 45,
    height: 45,
    borderRadius: 14,
    backgroundColor: "#FFF3F7",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 12,
  },

  achievementIconLocked: {
    backgroundColor: "#F4F1F2",
  },

  achievementEmoji: {
    fontSize: 22,
  },

  achievementEmojiLocked: {
    opacity: 0.65,
  },

  achievementInfo: {
    flex: 1,
  },

  achievementTitleRow: {
    flexDirection: "row",
    alignItems: "center",
  },

  achievementTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: "#292529",
  },

  achievementTitleLocked: {
    color: "#8E858A",
  },

  unlockedText: {
    marginLeft: 6,
    fontSize: 13,
    fontWeight: "700",
    color: "#FF6FA7",
  },

  achievementDescription: {
    marginTop: 3,
    fontSize: 11,
    lineHeight: 16,
    color: "#8E858A",
  },

  achievementDescriptionLocked: {
    color: "#A9A1A5",
  },

  /* EXISTING LEVEL */

  levelCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 20,
    borderWidth: 1,
    borderColor: "#F1ECEF",
    padding: 18,
    marginBottom: 24,
  },

  levelHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },

  levelLabel: {
    marginBottom: 3,
    fontSize: 11,
    fontWeight: "700",
    letterSpacing: 0.7,
    color: "#8E858A",
  },

  level: {
    fontSize: 30,
    fontWeight: "700",
    color: "#292529",
  },

  levelFlower: {
    width: 52,
    height: 52,
    borderRadius: 17,
    backgroundColor: "#FFF3F7",
    justifyContent: "center",
    alignItems: "center",
  },

  flower: {
    fontSize: 29,
  },

  progressBackground: {
    height: 8,
    marginTop: 15,
    borderRadius: 4,
    backgroundColor: "#F0E6EA",
    overflow: "hidden",
  },

  progress: {
    height: "100%",
    borderRadius: 4,
    backgroundColor: "#FF8FBA",
  },

  levelFooter: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginTop: 8,
  },

  levelProgressText: {
    fontSize: 11,
    color: "#A39A9F",
  },

  nextLevel: {
    fontSize: 11,
    fontWeight: "600",
    color: "#FF6FA7",
  },

  description: {
    marginTop: 8,
    fontSize: 13,
    lineHeight: 18,
    color: "#8E858A",
  },

  statsRow: {
    flexDirection: "row",
    marginBottom: 24,
  },

  statCard: {
    flex: 1,
    alignItems: "center",
    backgroundColor: "#FFFFFF",
    borderRadius: 20,
    borderWidth: 1,
    borderColor: "#F1ECEF",
    paddingVertical: 17,
  },

  statCardSecond: {
    marginLeft: 10,
  },

  statIcon: {
    marginBottom: 5,
    fontSize: 19,
  },

  statValue: {
    fontSize: 22,
    fontWeight: "700",
    color: "#292529",
  },

  statLabel: {
    marginTop: 3,
    fontSize: 12,
    color: "#8E858A",
  },

  stateCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 20,
    borderWidth: 1,
    borderColor: "#F1ECEF",
    padding: 18,
    marginBottom: 12,
  },

  stateHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },

  stateLabel: {
    fontSize: 10,
    fontWeight: "700",
    letterSpacing: 0.7,
    color: "#FF6FA7",
  },

  stateTitle: {
    marginTop: 3,
    fontSize: 17,
    fontWeight: "700",
    color: "#292529",
  },

  stateValue: {
    fontSize: 22,
    fontWeight: "700",
    color: "#292529",
  },

  stateDescription: {
    marginTop: 10,
    fontSize: 12,
    lineHeight: 17,
    color: "#8E858A",
  },

  preferenceRow: {
    flexDirection: "row",
    marginBottom: 24,
  },

  preferenceCard: {
    flex: 1,
    backgroundColor: "#FFF7FA",
    borderRadius: 20,
    padding: 15,
  },

  preferenceCardSecond: {
    marginLeft: 10,
  },

  preferenceIcon: {
    marginBottom: 9,
    fontSize: 20,
  },

  preferenceLabel: {
    fontSize: 9,
    fontWeight: "700",
    letterSpacing: 0.7,
    color: "#FF6FA7",
  },

  preferenceValue: {
    marginTop: 3,
    fontSize: 15,
    fontWeight: "600",
    color: "#292529",
  },

  goalCard: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#FFF7FA",
    borderRadius: 20,
    padding: 16,
    marginBottom: 24,
  },

  goalIcon: {
    width: 48,
    height: 48,
    borderRadius: 16,
    backgroundColor: "#FFFFFF",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 13,
  },

  goalEmoji: {
    fontSize: 23,
  },

  goalInfo: {
    flex: 1,
  },

  goalLabel: {
    fontSize: 10,
    fontWeight: "700",
    letterSpacing: 0.7,
    color: "#FF6FA7",
  },

  goalTitle: {
    marginTop: 3,
    fontSize: 17,
    fontWeight: "700",
    color: "#292529",
  },

  goalDescription: {
    marginTop: 3,
    fontSize: 12,
    lineHeight: 17,
    color: "#8E858A",
  },

  settingsButton: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#FFFFFF",
    borderRadius: 20,
    borderWidth: 1,
    borderColor: "#F1ECEF",
    padding: 16,
    marginBottom: 24,
  },

  settingsButtonPressed: {
    opacity: 0.7,
  },

  settingsIcon: {
    width: 46,
    height: 46,
    borderRadius: 15,
    backgroundColor: "#FFF3F7",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 13,
  },

  settingsEmoji: {
    fontSize: 21,
  },

  settingsInfo: {
    flex: 1,
  },

  settingsTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#292529",
  },

  settingsDescription: {
    marginTop: 3,
    fontSize: 12,
    color: "#8E858A",
  },

  arrow: {
    marginLeft: 10,
    fontSize: 28,
    color: "#B7ADB2",
  },
});