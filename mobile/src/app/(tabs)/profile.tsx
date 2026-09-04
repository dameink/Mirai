import { useCallback, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { useFocusEffect } from "@react-navigation/native";
import { router } from "expo-router";
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

function clamp(value: number): number {
  if (!Number.isFinite(value)) return 0;
  return Math.max(0, Math.min(100, value));
}

function formatTitle(value: unknown): string {
  if (value === null || value === undefined || value === "") {
    return "Learning";
  }

  return String(value)
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function getProgress(profile: LearningProfile): number {
  const skills = profile.learner?.skills;

  if (!skills || typeof skills !== "object") {
    return 0;
  }

  const values: number[] = [];

  Object.values(skills).forEach((category) => {
    if (!category || typeof category !== "object") return;

    Object.values(category).forEach((skill) => {
      if (
        skill &&
        typeof skill.value === "number" &&
        Number.isFinite(skill.value) &&
        typeof skill.evidence_count === "number" &&
        Number.isFinite(skill.evidence_count) &&
        skill.evidence_count > 0
      ) {
        values.push(clamp(skill.value));
      }
    });
  });

  if (values.length === 0) return 0;

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

function getLevelProgress(progress: number, level: string): number {
  const ranges: Record<string, [number, number]> = {
    A1: [0, 20],
    A2: [20, 40],
    B1: [40, 60],
    B2: [60, 75],
    C1: [75, 90],
    C2: [90, 100],
  };

  if (level === "C2") return 100;

  const [start, end] = ranges[level] ?? [0, 100];

  if (end <= start) return 0;

  return clamp(
    Math.round(((clamp(progress) - start) / (end - start)) * 100)
  );
}

function getConfidenceLabel(confidence: number): string {
  const value = clamp(confidence);

  if (value < 25) return "Just getting started";
  if (value < 50) return "Building confidence";
  if (value < 75) return "Growing confidence";

  return "Feeling confident";
}

function getDifficultyLabel(value: unknown): string {
  if (!value) return "Adaptive";

  const formatted = formatTitle(value);

  return formatted === "Learning" ? "Adaptive" : formatted;
}

function getModeLabel(value: unknown): string {
  if (!value) return "Balanced";

  const formatted = formatTitle(value);

  return formatted === "Learning" ? "Balanced" : formatted;
}

export default function ProfileScreen() {
  const [profile, setProfile] = useState<LearningProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadProfile = useCallback(async () => {
    try {
      setError(null);
      setLoading(true);

      const response = await authFetch("/learning/profile");

      if (!response.ok) {
        throw new Error(
          `Request failed with status ${response.status}`
        );
      }

      const data = (await response.json()) as LearningProfile;

      console.log("Learning profile updated:", data);

      setProfile(data);
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

  /*
   * Every time the Profile tab becomes active,
   * request the newest learning state from the backend.
   *
   * This means:
   * Chat with Mirai
   * → backend updates learning
   * → open Profile
   * → Profile requests fresh data
   * → numbers change.
   */
  useFocusEffect(
    useCallback(() => {
      loadProfile();
    }, [loadProfile])
  );

  const progress = profile ? getProgress(profile) : 0;

  const level = getCEFR(progress);
  const nextLevel = getNextLevel(level);
  const levelProgress = getLevelProgress(progress, level);

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

  const confidenceLabel = getConfidenceLabel(confidence);

  const difficulty = getDifficultyLabel(
    profile?.analysis?.difficulty?.difficulty
  );

  const mode = getModeLabel(
    profile?.analysis?.mode?.mode
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
                  {confidenceLabel}
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
    fontSize: 13,
    color: "#8E858A",
    marginTop: 6,
    lineHeight: 19,
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
    fontSize: 14,
    color: "#8E858A",
    marginTop: 4,
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
    fontSize: 18,
    fontWeight: "700",
    color: "#292529",
    marginBottom: 12,
  },

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
    fontSize: 11,
    fontWeight: "700",
    letterSpacing: 0.7,
    color: "#8E858A",
    marginBottom: 3,
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
    borderRadius: 4,
    backgroundColor: "#F0E6EA",
    overflow: "hidden",
    marginTop: 15,
  },

  progress: {
    height: "100%",
    borderRadius: 4,
    backgroundColor: "#FF8FBA",
  },

  levelFooter: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
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
    fontSize: 13,
    lineHeight: 18,
    color: "#8E858A",
    marginTop: 8,
  },

  statsRow: {
    flexDirection: "row",
    marginBottom: 24,
  },

  statCard: {
    flex: 1,
    backgroundColor: "#FFFFFF",
    borderRadius: 20,
    borderWidth: 1,
    borderColor: "#F1ECEF",
    paddingVertical: 17,
    alignItems: "center",
  },

  statCardSecond: {
    marginLeft: 10,
  },

  statIcon: {
    fontSize: 19,
    marginBottom: 5,
  },

  statValue: {
    fontSize: 22,
    fontWeight: "700",
    color: "#292529",
  },

  statLabel: {
    fontSize: 12,
    color: "#8E858A",
    marginTop: 3,
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
    fontSize: 17,
    fontWeight: "700",
    color: "#292529",
    marginTop: 3,
  },

  stateValue: {
    fontSize: 22,
    fontWeight: "700",
    color: "#292529",
  },

  stateDescription: {
    fontSize: 12,
    lineHeight: 17,
    color: "#8E858A",
    marginTop: 10,
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
    fontSize: 20,
    marginBottom: 9,
  },

  preferenceLabel: {
    fontSize: 9,
    fontWeight: "700",
    letterSpacing: 0.7,
    color: "#FF6FA7",
  },

  preferenceValue: {
    fontSize: 15,
    fontWeight: "600",
    color: "#292529",
    marginTop: 3,
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
    fontSize: 17,
    fontWeight: "700",
    color: "#292529",
    marginTop: 3,
  },

  goalDescription: {
    fontSize: 12,
    lineHeight: 17,
    color: "#8E858A",
    marginTop: 3,
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
    fontSize: 12,
    color: "#8E858A",
    marginTop: 3,
  },

  arrow: {
    fontSize: 28,
    color: "#B7ADB2",
    marginLeft: 10,
  },
});