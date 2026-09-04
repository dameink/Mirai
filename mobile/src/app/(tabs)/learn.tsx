
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { useFocusEffect } from "expo-router/react-navigation";
import { SectionScreen } from "../../components/section-screen";
import { authFetch } from "../../auth/auth";

type Skill = {
  value?: number;
  certainty?: number;
  evidence_count?: number;
  trend?: number;
};

type SkillGroup = Record<string, Skill>;

type LearningProfile = {
  learner?: {
    skills?: Record<string, SkillGroup>;
  };

  analysis?: {
    state?: {
      confidence?: number;
      weakest_skill?: {
        category?: string;
        skill?: string;
        value?: number;
      };
      [key: string]: unknown;
    };

    goal?: {
      goal?: string;
    };

    mode?: {
      mode?: string;
    };

    difficulty?: {
      difficulty?: string;
    };

    activity?: {
      name?: string;
      title?: string;
      type?: string;
      category?: string;
      skill?: string;
      subskill?: string;
    };
  };

  sessions?: unknown[];
};

type SkillItem = {
  category: string;
  skill: string;
  value: number;
  certainty: number;
  evidence: number;
  trend: number;
};

function clamp(value: number) {
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

function getSkillList(profile: LearningProfile): SkillItem[] {
  const skills = profile.learner?.skills;

  if (!skills) {
    return [];
  }

  const result: SkillItem[] = [];

  Object.entries(skills).forEach(([category, categorySkills]) => {
    Object.entries(categorySkills || {}).forEach(
      ([skillName, skill]) => {
        if (
          typeof skill?.value === "number" &&
          typeof skill?.evidence_count === "number" &&
          skill.evidence_count > 0
        ) {
          result.push({
            category,
            skill: skillName,
            value: clamp(skill.value),
            certainty:
              typeof skill.certainty === "number"
                ? clamp(skill.certainty)
                : 0,
            evidence: skill.evidence_count,
            trend:
              typeof skill.trend === "number"
                ? skill.trend
                : 0,
          });
        }
      }
    );
  });

  return result;
}

function getProgress(skills: SkillItem[]) {
  if (!skills.length) {
    return 0;
  }

  return Math.round(
    clamp(
      skills.reduce((sum, skill) => sum + skill.value, 0) /
        skills.length
    )
  );
}

function getAverageCertainty(skills: SkillItem[]) {
  if (!skills.length) {
    return 0;
  }

  return Math.round(
    skills.reduce((sum, skill) => sum + skill.certainty, 0) /
      skills.length
  );
}

function getEvidence(skills: SkillItem[]) {
  return skills.reduce((sum, skill) => sum + skill.evidence, 0);
}

function getAverageTrend(skills: SkillItem[]) {
  if (!skills.length) {
    return 0;
  }

  return (
    skills.reduce((sum, skill) => sum + skill.trend, 0) /
    skills.length
  );
}

function getTrendLabel(trend: number) {
  if (trend > 1) {
    return "Improving";
  }

  if (trend < -1) {
    return "Needs attention";
  }

  return "Stable";
}

function getTrendEmoji(trend: number) {
  if (trend > 1) {
    return "↗";
  }

  if (trend < -1) {
    return "↘";
  }

  return "→";
}

function getCategoryStats(skills: SkillItem[]) {
  const categories: Record<
    string,
    {
      values: number[];
      evidence: number;
      trend: number[];
    }
  > = {};

  skills.forEach((skill) => {
    if (!categories[skill.category]) {
      categories[skill.category] = {
        values: [],
        evidence: 0,
        trend: [],
      };
    }

    categories[skill.category].values.push(skill.value);
    categories[skill.category].evidence += skill.evidence;
    categories[skill.category].trend.push(skill.trend);
  });

  return Object.entries(categories)
    .map(([category, data]) => ({
      category,
      value: Math.round(
        data.values.reduce((a, b) => a + b, 0) /
          data.values.length
      ),
      evidence: data.evidence,
      trend:
        data.trend.reduce((a, b) => a + b, 0) /
        data.trend.length,
    }))
    .sort((a, b) => a.value - b.value);
}

export default function LearnScreen() {
  const [profile, setProfile] =
    useState<LearningProfile | null>(null);

  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);
  const [showAllSkills, setShowAllSkills] = useState(false);
  const [showCategories, setShowCategories] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadLearning = useCallback(async () => {
    try {
      setError(null);

      const controller = new AbortController();

      const timeout = setTimeout(() => {
        controller.abort();
      }, 10000);

      try {
        const response = await authFetch(
          "/learning/profile",
          {
            signal: controller.signal,
          }
        );

        if (!response.ok) {
          throw new Error(
            `Request failed with status ${response.status}`
          );
        }

        const data =
          (await response.json()) as LearningProfile;

        setProfile(data);
      } finally {
        clearTimeout(timeout);
      }
    } catch (error) {
      console.log(
        "Failed to load learning profile:",
        error
      );

      setError(
        error instanceof DOMException &&
        error.name === "AbortError"
          ? "Learning profile request timed out"
          : error instanceof Error
          ? error.message
          : "Failed to load learning data"
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadLearning();
  }, [loadLearning]);

  /*
   * Важно:
   * после Chat / Practice пользователь может изменить
   * learning state. Поэтому при возвращении на экран
   * профиль снова запрашивается с backend.
   */
  useFocusEffect(
    useCallback(() => {
      loadLearning();
    }, [loadLearning])
  );

  const startSession = async () => {
    if (starting) {
      return;
    }

    try {
      setStarting(true);
      setError(null);

      const response = await authFetch(
        "/learning/session/start",
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        throw new Error(
          `Request failed with status ${response.status}`
        );
      }

      await response.json();

      await loadLearning();
    } catch (error) {
      console.log(
        "Failed to start learning session:",
        error
      );

      setError(
        error instanceof Error
          ? error.message
          : "Failed to start learning session"
      );
    } finally {
      setStarting(false);
    }
  };

  const skills = useMemo(
    () => (profile ? getSkillList(profile) : []),
    [profile]
  );

  const progress = getProgress(skills);
  const certainty = getAverageCertainty(skills);
  const evidence = getEvidence(skills);
  const averageTrend = getAverageTrend(skills);

  const categories = useMemo(
    () => getCategoryStats(skills),
    [skills]
  );

  const analysis = profile?.analysis;

  const goal =
    analysis?.goal?.goal ?? "English";

  const mode =
    analysis?.mode?.mode ?? "Practice";

  const difficulty =
    analysis?.difficulty?.difficulty ?? "Adaptive";

  const activity = analysis?.activity;

  const activityName =
    activity?.name ??
    activity?.title ??
    "Grammar Practice";

  const activityType =
    activity?.type ??
    activity?.category ??
    "Practice";

  const weakestSkill =
    analysis?.state?.weakest_skill;

  const learningTrend =
    getTrendLabel(averageTrend);

  const trendEmoji =
    getTrendEmoji(averageTrend);

  const visibleSkills = showAllSkills
    ? skills
    : skills.slice(0, 4);

  return (
    <SectionScreen
      activeRoute="learn"
      eyebrow="YOUR LEARNING"
      title="Learning profile"
      description="A little picture of how you're growing."
    >
      {loading ? (
        <View style={styles.loading}>
          <ActivityIndicator />

          <Text style={styles.loadingText}>
            Loading your learning profile...
          </Text>
        </View>
      ) : error ? (
        <View style={styles.errorCard}>
          <Text style={styles.errorTitle}>
            Couldn't load learning
          </Text>

          <Text style={styles.errorText}>
            {error}
          </Text>

          <Pressable
            style={styles.retryButton}
            onPress={loadLearning}
          >
            <Text style={styles.retryText}>
              Try again
            </Text>
          </Pressable>
        </View>
      ) : (
        <>
          <View style={styles.heroCard}>
            <View style={styles.heroTop}>
              <View>
                <Text style={styles.heroEyebrow}>
                  OVERALL PROGRESS
                </Text>

                <Text style={styles.heroValue}>
                  {progress}%
                </Text>

                <Text style={styles.heroDescription}>
                  Your learning profile is evolving
                  through practice.
                </Text>
              </View>

              <View style={styles.heroFlower}>
                <Text style={styles.heroFlowerText}>
                  🌸
                </Text>
              </View>
            </View>

            <View style={styles.heroProgressBackground}>
              <View
                style={[
                  styles.heroProgress,
                  { width: `${progress}%` },
                ]}
              />
            </View>

            <View style={styles.statRow}>
              <View style={styles.stat}>
                <Text style={styles.statValue}>
                  {skills.length}
                </Text>

                <Text style={styles.statLabel}>
                  skills
                </Text>
              </View>

              <View style={styles.statDivider} />

              <View style={styles.stat}>
                <Text style={styles.statValue}>
                  {evidence}
                </Text>

                <Text style={styles.statLabel}>
                  evidence
                </Text>
              </View>

              <View style={styles.statDivider} />

              <View style={styles.stat}>
                <Text style={styles.statValue}>
                  {certainty}%
                </Text>

                <Text style={styles.statLabel}>
                  certainty
                </Text>
              </View>
            </View>
          </View>

          <View style={styles.momentumCard}>
            <View style={styles.momentumIcon}>
              <Text style={styles.momentumEmoji}>
                {trendEmoji}
              </Text>
            </View>

            <View style={styles.momentumInfo}>
              <Text style={styles.momentumLabel}>
                LEARNING MOMENTUM
              </Text>

              <Text style={styles.momentumTitle}>
                {learningTrend}
              </Text>

              <Text style={styles.momentumText}>
                Based on changes across your
                current skill profile.
              </Text>
            </View>
          </View>

          <Text style={styles.sectionTitle}>
            Learning snapshot
          </Text>

          <View style={styles.snapshotCard}>
            <View style={styles.snapshotItem}>
              <Text style={styles.snapshotIcon}>
                🎯
              </Text>

              <View style={styles.snapshotInfo}>
                <Text style={styles.snapshotLabel}>
                  Goal
                </Text>

                <Text style={styles.snapshotValue}>
                  {formatTitle(goal)}
                </Text>
              </View>
            </View>

            <View style={styles.snapshotDivider} />

            <View style={styles.snapshotItem}>
              <Text style={styles.snapshotIcon}>
                💬
              </Text>

              <View style={styles.snapshotInfo}>
                <Text style={styles.snapshotLabel}>
                  Mode
                </Text>

                <Text style={styles.snapshotValue}>
                  {formatTitle(mode)}
                </Text>
              </View>
            </View>

            <View style={styles.snapshotDivider} />

            <View style={styles.snapshotItem}>
              <Text style={styles.snapshotIcon}>
                ⚡
              </Text>

              <View style={styles.snapshotInfo}>
                <Text style={styles.snapshotLabel}>
                  Difficulty
                </Text>

                <Text style={styles.snapshotValue}>
                  {formatTitle(difficulty)}
                </Text>
              </View>
            </View>
          </View>

          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>
              Skill profile
            </Text>

            {skills.length > 4 && (
              <Pressable
                onPress={() =>
                  setShowAllSkills((value) => !value)
                }
                hitSlop={8}
              >
                <Text style={styles.viewAll}>
                  {showAllSkills
                    ? "Show less"
                    : "View all"}
                </Text>
              </Pressable>
            )}
          </View>

          {visibleSkills.length > 0 ? (
            <View style={styles.skillsCard}>
              {visibleSkills.map((item, index) => (
                <View
                  key={`${item.category}.${item.skill}`}
                  style={[
                    styles.skillItem,
                    index === visibleSkills.length - 1 &&
                      styles.skillItemLast,
                  ]}
                >
                  <View style={styles.skillHeader}>
                    <View style={styles.skillNameArea}>
                      <Text style={styles.skillName}>
                        {formatTitle(item.skill)}
                      </Text>

                      <Text style={styles.skillCategory}>
                        {formatTitle(item.category)}
                      </Text>
                    </View>

                    <Text style={styles.skillValue}>
                      {item.value}%
                    </Text>
                  </View>

                  <View style={styles.skillBackground}>
                    <View
                      style={[
                        styles.skillProgress,
                        {
                          width: `${item.value}%`,
                        },
                      ]}
                    />
                  </View>
                </View>
              ))}
            </View>
          ) : (
            <View style={styles.emptyCard}>
              <Text style={styles.emptyTitle}>
                Your profile is still growing
              </Text>

              <Text style={styles.emptyText}>
                Start practicing to build your
                first skill evidence.
              </Text>
            </View>
          )}

          {categories.length > 0 && (
            <>
              <Pressable
                style={styles.categoryHeader}
                onPress={() =>
                  setShowCategories((value) => !value)
                }
              >
                <View>
                  <Text style={styles.categoryHeaderTitle}>
                    Skill categories
                  </Text>

                  <Text style={styles.categoryHeaderText}>
                    See how different areas compare
                  </Text>
                </View>

                <Text style={styles.categoryArrow}>
                  {showCategories ? "⌃" : "⌄"}
                </Text>
              </Pressable>

              {showCategories && (
                <View style={styles.categoriesCard}>
                  {categories.map((category, index) => (
                    <View
                      key={category.category}
                      style={[
                        styles.categoryItem,
                        index === categories.length - 1 &&
                          styles.categoryItemLast,
                      ]}
                    >
                      <View style={styles.categoryTop}>
                        <Text style={styles.categoryName}>
                          {formatTitle(category.category)}
                        </Text>

                        <Text style={styles.categoryValue}>
                          {category.value}%
                        </Text>
                      </View>

                      <View style={styles.categoryBackground}>
                        <View
                          style={[
                            styles.categoryProgress,
                            {
                              width: `${category.value}%`,
                            },
                          ]}
                        />
                      </View>

                      <Text style={styles.categoryMeta}>
                        {category.evidence} pieces of evidence ·{" "}
                        {getTrendLabel(category.trend)}
                      </Text>
                    </View>
                  ))}
                </View>
              )}
            </>
          )}

          {weakestSkill?.skill && (
            <>
              <Text style={styles.sectionTitle}>
                Focus area
              </Text>

              <View style={styles.focusCard}>
                <View style={styles.focusIcon}>
                  <Text style={styles.focusEmoji}>
                    🌱
                  </Text>
                </View>

                <View style={styles.focusInfo}>
                  <Text style={styles.focusLabel}>
                    NEXT TO GROW
                  </Text>

                  <Text style={styles.focusTitle}>
                    {formatTitle(weakestSkill.skill)}
                  </Text>

                  <Text style={styles.focusText}>
                    This is the skill that could
                    benefit most from your next
                    practice.
                  </Text>
                </View>
              </View>
            </>
          )}

          <Text style={styles.sectionTitle}>
            Your next activity
          </Text>

          <View style={styles.activityCard}>
            <View style={styles.activityIcon}>
              <Text style={styles.activityEmoji}>
                🎤
              </Text>
            </View>

            <View style={styles.activityInfo}>
              <Text style={styles.activityLabel}>
                RECOMMENDED PRACTICE
              </Text>

              <Text style={styles.activityTitle}>
                {formatTitle(activityName)}
              </Text>

              <Text style={styles.activitySubtitle}>
                {formatTitle(activityType)}
                {activity?.skill
                  ? ` · ${formatTitle(activity.skill)}`
                  : ""}
              </Text>
            </View>
          </View>

          <Pressable
            style={[
              styles.startButton,
              starting && styles.startButtonDisabled,
            ]}
            onPress={startSession}
            disabled={starting}
          >
            {starting ? (
              <ActivityIndicator color="#FFFFFF" />
            ) : (
              <Text style={styles.startButtonText}>
                Start practice
              </Text>
            )}
          </Pressable>
        </>
      )}
    </SectionScreen>
  );
}

const styles = StyleSheet.create({
  loading: {
    alignItems: "center",
    paddingVertical: 50,
  },

  loadingText: {
    marginTop: 10,
    fontSize: 13,
    color: "#8E858A",
  },

  errorCard: {
    backgroundColor: "#FFF7FA",
    borderRadius: 22,
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

  heroCard: {
    backgroundColor: "#FFF7FA",
    borderRadius: 26,
    padding: 21,
    marginBottom: 14,
  },

  heroTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },

  heroEyebrow: {
    fontSize: 10,
    fontWeight: "700",
    letterSpacing: 0.9,
    color: "#FF6FA7",
  },

  heroValue: {
    fontSize: 38,
    fontWeight: "700",
    color: "#292529",
    marginTop: 3,
  },

  heroDescription: {
    maxWidth: 250,
    fontSize: 13,
    lineHeight: 18,
    color: "#8E858A",
    marginTop: 3,
  },

  heroFlower: {
    width: 66,
    height: 66,
    borderRadius: 23,
    backgroundColor: "#FFFFFF",
    justifyContent: "center",
    alignItems: "center",
  },

  heroFlowerText: {
    fontSize: 34,
  },

  heroProgressBackground: {
    height: 9,
    borderRadius: 5,
    backgroundColor: "#F0E6EA",
    overflow: "hidden",
    marginTop: 20,
  },

  heroProgress: {
    height: "100%",
    borderRadius: 5,
    backgroundColor: "#FF8FBA",
  },

  statRow: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: 19,
  },

  stat: {
    flex: 1,
    alignItems: "center",
  },

  statValue: {
    fontSize: 16,
    fontWeight: "700",
    color: "#292529",
  },

  statLabel: {
    fontSize: 11,
    color: "#9A9095",
    marginTop: 2,
  },

  statDivider: {
    width: 1,
    height: 28,
    backgroundColor: "#EBDDE3",
  },

  momentumCard: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#FFFFFF",
    borderWidth: 1,
    borderColor: "#F1ECEF",
    borderRadius: 21,
    padding: 16,
    marginBottom: 25,
  },

  momentumIcon: {
    width: 48,
    height: 48,
    borderRadius: 16,
    backgroundColor: "#FFF3F7",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 13,
  },

  momentumEmoji: {
    fontSize: 25,
    color: "#FF6FA7",
  },

  momentumInfo: {
    flex: 1,
  },

  momentumLabel: {
    fontSize: 10,
    fontWeight: "700",
    letterSpacing: 0.7,
    color: "#FF6FA7",
  },

  momentumTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: "#292529",
    marginTop: 2,
  },

  momentumText: {
    fontSize: 12,
    lineHeight: 17,
    color: "#8E858A",
    marginTop: 2,
  },

  sectionTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: "#292529",
    marginBottom: 12,
  },

  snapshotCard: {
    backgroundColor: "#FFFFFF",
    borderWidth: 1,
    borderColor: "#F1ECEF",
    borderRadius: 21,
    padding: 16,
    marginBottom: 25,
  },

  snapshotItem: {
    flexDirection: "row",
    alignItems: "center",
    minHeight: 42,
  },

  snapshotIcon: {
    fontSize: 19,
    width: 38,
  },

  snapshotInfo: {
    flex: 1,
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },

  snapshotLabel: {
    fontSize: 13,
    color: "#8E858A",
  },

  snapshotValue: {
    fontSize: 14,
    fontWeight: "600",
    color: "#FF6FA7",
  },

  snapshotDivider: {
    height: 1,
    backgroundColor: "#F3EEF0",
    marginVertical: 7,
  },

  sectionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },

  viewAll: {
    fontSize: 13,
    fontWeight: "600",
    color: "#FF6FA7",
    marginBottom: 12,
  },

  skillsCard: {
    backgroundColor: "#FFFFFF",
    borderWidth: 1,
    borderColor: "#F1ECEF",
    borderRadius: 21,
    padding: 17,
    marginBottom: 14,
  },

  skillItem: {
    marginBottom: 20,
  },

  skillItemLast: {
    marginBottom: 0,
  },

  skillHeader: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 8,
  },

  skillNameArea: {
    flex: 1,
  },

  skillName: {
    fontSize: 14,
    fontWeight: "600",
    color: "#292529",
  },

  skillCategory: {
    fontSize: 10,
    color: "#AAA0A5",
    marginTop: 2,
  },

  skillValue: {
    fontSize: 13,
    fontWeight: "700",
    color: "#FF6FA7",
  },

  skillBackground: {
    height: 6,
    borderRadius: 3,
    backgroundColor: "#F0E6EA",
    overflow: "hidden",
  },

  skillProgress: {
    height: "100%",
    borderRadius: 3,
    backgroundColor: "#FF8FBA",
  },

  emptyCard: {
    backgroundColor: "#FFFFFF",
    borderWidth: 1,
    borderColor: "#F1ECEF",
    borderRadius: 21,
    padding: 18,
    marginBottom: 14,
  },

  emptyTitle: {
    fontSize: 15,
    fontWeight: "600",
    color: "#292529",
  },

  emptyText: {
    fontSize: 13,
    lineHeight: 19,
    color: "#8E858A",
    marginTop: 5,
  },

  categoryHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    backgroundColor: "#FFF7FA",
    borderRadius: 19,
    padding: 16,
    marginBottom: 10,
  },

  categoryHeaderTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: "#292529",
  },

  categoryHeaderText: {
    fontSize: 11,
    color: "#8E858A",
    marginTop: 3,
  },

  categoryArrow: {
    fontSize: 21,
    color: "#FF6FA7",
  },

  categoriesCard: {
    backgroundColor: "#FFFFFF",
    borderWidth: 1,
    borderColor: "#F1ECEF",
    borderRadius: 21,
    padding: 17,
    marginBottom: 25,
  },

  categoryItem: {
    marginBottom: 19,
  },

  categoryItemLast: {
    marginBottom: 0,
  },

  categoryTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 7,
  },

  categoryName: {
    fontSize: 14,
    fontWeight: "600",
    color: "#292529",
  },

  categoryValue: {
    fontSize: 13,
    fontWeight: "700",
    color: "#FF6FA7",
  },

  categoryBackground: {
    height: 5,
    borderRadius: 3,
    backgroundColor: "#F0E6EA",
    overflow: "hidden",
  },

  categoryProgress: {
    height: "100%",
    borderRadius: 3,
    backgroundColor: "#FF8FBA",
  },

  categoryMeta: {
    fontSize: 10,
    color: "#A39A9F",
    marginTop: 5,
  },

  focusCard: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#FFF7FA",
    borderRadius: 21,
    padding: 16,
    marginBottom: 25,
  },

  focusIcon: {
    width: 50,
    height: 50,
    borderRadius: 17,
    backgroundColor: "#FFFFFF",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 13,
  },

  focusEmoji: {
    fontSize: 25,
  },

  focusInfo: {
    flex: 1,
  },

  focusLabel: {
    fontSize: 10,
    fontWeight: "700",
    letterSpacing: 0.7,
    color: "#FF6FA7",
  },

  focusTitle: {
    fontSize: 17,
    fontWeight: "700",
    color: "#292529",
    marginTop: 3,
  },

  focusText: {
    fontSize: 12,
    lineHeight: 17,
    color: "#8E858A",
    marginTop: 3,
  },

  activityCard: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#FFFFFF",
    borderWidth: 1,
    borderColor: "#F1ECEF",
    borderRadius: 21,
    padding: 15,
    marginBottom: 12,
  },

  activityIcon: {
    width: 51,
    height: 51,
    borderRadius: 17,
    backgroundColor: "#FFF3F7",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 13,
  },

  activityEmoji: {
    fontSize: 24,
  },

  activityInfo: {
    flex: 1,
  },

  activityLabel: {
    fontSize: 9,
    fontWeight: "700",
    letterSpacing: 0.7,
    color: "#FF6FA7",
  },

  activityTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: "#292529",
    marginTop: 3,
  },

  activitySubtitle: {
    fontSize: 12,
    color: "#8E858A",
    marginTop: 3,
  },

  startButton: {
    height: 53,
    borderRadius: 17,
    backgroundColor: "#FF8FBA",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 27,
  },

  startButtonDisabled: {
    opacity: 0.65,
  },

  startButtonText: {
    fontSize: 15,
    fontWeight: "700",
    color: "#FFFFFF",
  },
});
