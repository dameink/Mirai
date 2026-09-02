import { router } from "expo-router";
import {
  Alert,
  Animated,
  Easing,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { useEffect, useRef } from "react";
import { API_URL } from "../../constants/api";
import { useSettings } from "../../../context/settings-context";

export type Mode = "Auto" | "Casual" | "Learning";

const MODES: {
  value: Mode;
  title: string;
  description: string;
}[] = [
  {
    value: "Auto",
    title: "Auto",
    description:
      "Mirai decides when to chat casually and when to help you learn.",
  },
  {
    value: "Casual",
    title: "Casual",
    description:
      "Focus on natural conversation. Mirai won't constantly turn the chat into a lesson.",
  },
  {
    value: "Learning",
    title: "Learning",
    description:
      "Focus on language practice, corrections, questions, and active learning.",
  },
];

function AnimatedRow({
  children,
  onPress,
  style,
}: {
  children: React.ReactNode;
  onPress: () => void;
  style?: any;
}) {
  const scale = useRef(new Animated.Value(1)).current;

  const animatePress = (pressed: boolean) => {
    Animated.spring(scale, {
      toValue: pressed ? 0.985 : 1,
      useNativeDriver: true,
      speed: 35,
      bounciness: 4,
    }).start();
  };

  return (
    <Animated.View style={[{ transform: [{ scale }] }, style]}>
      <Pressable
        onPress={onPress}
        onPressIn={() => animatePress(true)}
        onPressOut={() => animatePress(false)}
        style={({ pressed }) => [
          styles.row,
          pressed && styles.rowPressed,
        ]}
      >
        {children}
      </Pressable>
    </Animated.View>
  );
}

function AnimatedModeRow({
  item,
  selected,
  onPress,
}: {
  item: (typeof MODES)[number];
  selected: boolean;
  onPress: () => void;
}) {
  const scale = useRef(new Animated.Value(1)).current;
  const radioScale = useRef(
    new Animated.Value(selected ? 1 : 0),
  ).current;
  const activeOpacity = useRef(
    new Animated.Value(selected ? 1 : 0),
  ).current;

  useEffect(() => {
    Animated.parallel([
      Animated.spring(radioScale, {
        toValue: selected ? 1 : 0,
        useNativeDriver: true,
        speed: 20,
        bounciness: 8,
      }),
      Animated.timing(activeOpacity, {
        toValue: selected ? 1 : 0,
        duration: 180,
        easing: Easing.out(Easing.ease),
        useNativeDriver: true,
      }),
    ]).start();
  }, [selected]);

  const animatePress = (pressed: boolean) => {
    Animated.spring(scale, {
      toValue: pressed ? 0.985 : 1,
      useNativeDriver: true,
      speed: 35,
      bounciness: 4,
    }).start();
  };

  return (
    <Animated.View
      style={{
        transform: [{ scale }],
      }}
    >
      <Pressable
        onPress={onPress}
        onPressIn={() => animatePress(true)}
        onPressOut={() => animatePress(false)}
        style={[
          styles.modeRow,
          selected && styles.modeRowSelected,
        ]}
      >
        <View style={styles.modeRadio}>
          <Animated.View
            style={[
              styles.modeRadioInner,
              {
                opacity: radioScale,
                transform: [
                  {
                    scale: radioScale,
                  },
                ],
              },
            ]}
          />
        </View>

        <View style={styles.modeText}>
          <View style={styles.modeTitleRow}>
            <Text
              style={[
                styles.modeTitle,
                selected && styles.modeTitleSelected,
              ]}
            >
              {item.title}
            </Text>

            <Animated.Text
              style={[
                styles.activeText,
                {
                  opacity: activeOpacity,
                  transform: [
                    {
                      translateX: activeOpacity.interpolate({
                        inputRange: [0, 1],
                        outputRange: [-5, 0],
                      }),
                    },
                  ],
                },
              ]}
            >
              ACTIVE
            </Animated.Text>
          </View>

          <Text style={styles.modeDescription}>
            {item.description}
          </Text>
        </View>
      </Pressable>
    </Animated.View>
  );
}

export default function SettingsScreen() {
  const {
    language,
    mode,
    setLanguage,
    setMode,
  } = useSettings();

  const screenOpacity = useRef(new Animated.Value(0)).current;
  const screenTranslate = useRef(
    new Animated.Value(12),
  ).current;

  const preferencesOpacity = useRef(
    new Animated.Value(0),
  ).current;
  const preferencesTranslate = useRef(
    new Animated.Value(12),
  ).current;

  const miraiOpacity = useRef(
    new Animated.Value(0),
  ).current;
  const miraiTranslate = useRef(
    new Animated.Value(12),
  ).current;

  const modesOpacity = useRef(
    new Animated.Value(0),
  ).current;
  const modesTranslate = useRef(
    new Animated.Value(12),
  ).current;

  const footerOpacity = useRef(
    new Animated.Value(0),
  ).current;

  useEffect(() => {
    const createEntrance = (
      opacity: Animated.Value,
      translate: Animated.Value,
      delay: number,
    ) =>
      Animated.parallel([
        Animated.timing(opacity, {
          toValue: 1,
          duration: 400,
          delay,
          easing: Easing.out(Easing.cubic),
          useNativeDriver: true,
        }),
        Animated.timing(translate, {
          toValue: 0,
          duration: 400,
          delay,
          easing: Easing.out(Easing.cubic),
          useNativeDriver: true,
        }),
      ]);

    Animated.parallel([
      createEntrance(
        screenOpacity,
        screenTranslate,
        0,
      ),
      createEntrance(
        preferencesOpacity,
        preferencesTranslate,
        80,
      ),
      createEntrance(
        miraiOpacity,
        miraiTranslate,
        160,
      ),
      createEntrance(
        modesOpacity,
        modesTranslate,
        240,
      ),
      Animated.timing(footerOpacity, {
        toValue: 1,
        duration: 450,
        delay: 350,
        easing: Easing.out(Easing.ease),
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  const chooseLanguage = () => {
    Alert.alert(
      "Learning language",
      "Choose the language you want to learn.",
      [
        {
          text: "English",
          onPress: () => setLanguage("English"),
        },
        {
          text: "Japanese",
          onPress: () => setLanguage("Japanese"),
        },
        {
          text: "Spanish",
          onPress: () => setLanguage("Spanish"),
        },
        {
          text: "Cancel",
          style: "cancel",
        },
      ],
    );
  };

  const chooseMode = () => {
    Alert.alert(
      "Conversation mode",
      "Choose how Mirai should interact with you.",
      [
        {
          text: "Auto",
          onPress: () => setMode("Auto"),
        },
        {
          text: "Casual",
          onPress: () => setMode("Casual"),
        },
        {
          text: "Learning",
          onPress: () => setMode("Learning"),
        },
        {
          text: "Cancel",
          style: "cancel",
        },
      ],
    );
  };

  const showAbout = () => {
    Alert.alert(
      "Mirai",
      "Mirai is your AI language-learning companion.\n\nLearn, practice, and grow together.",
      [
        {
          text: "Close",
          style: "cancel",
        },
      ],
    );
  };

  const clearConversation = () => {
    Alert.alert(
      "Clear conversation?",
      "This will remove your current conversation history. This action cannot be undone.",
      [
        {
          text: "Cancel",
          style: "cancel",
        },
        {
          text: "Clear",
          style: "destructive",
          onPress: async () => {
            try {
              const response = await fetch(
                `${API_URL}/conversation`,
                {
                  method: "DELETE",
                },
              );

              if (!response.ok) {
                throw new Error(
                  `Failed to clear conversation: ${response.status}`,
                );
              }

              Alert.alert(
                "Conversation cleared",
                "Your conversation history has been cleared.",
              );
            } catch (error) {
              console.error(
                "Failed to clear conversation:",
                error,
              );

              Alert.alert(
                "Something went wrong",
                "I couldn't clear the conversation. Please try again.",
              );
            }
          },
        },
      ],
    );
  };

  const resetMirai = () => {
    Alert.alert(
      "Reset Mirai?",
      "This will reset Mirai's conversation and current state. This action cannot be undone.",
      [
        {
          text: "Cancel",
          style: "cancel",
        },
        {
          text: "Reset",
          style: "destructive",
          onPress: async () => {
            try {
              const response = await fetch(
                `${API_URL}/reset`,
                {
                  method: "DELETE",
                },
              );

              if (!response.ok) {
                throw new Error(
                  `Failed to reset Mirai: ${response.status}`,
                );
              }

              Alert.alert(
                "Mirai reset",
                "Mirai has been reset successfully.",
              );
            } catch (error) {
              console.error(
                "Failed to reset Mirai:",
                error,
              );

              Alert.alert(
                "Something went wrong",
                "I couldn't reset Mirai. Please try again.",
              );
            }
          },
        },
      ],
    );
  };

  return (
    <View style={styles.container}>
      <Animated.View
        style={[
          styles.header,
          {
            opacity: screenOpacity,
            transform: [
              {
                translateY: screenTranslate,
              },
            ],
          },
        ]}
      >
        <Pressable
          accessibilityLabel="Back"
          accessibilityRole="button"
          hitSlop={12}
          onPress={() => router.back()}
          style={({ pressed }) => [
            styles.backButton,
            pressed && styles.pressed,
          ]}
        >
          <Text style={styles.back}>‹</Text>
        </Pressable>

        <Text style={styles.title}>Settings</Text>

        <View style={styles.headerSpacer} />
      </Animated.View>

      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        <Animated.View
          style={{
            opacity: preferencesOpacity,
            transform: [
              {
                translateY: preferencesTranslate,
              },
            ],
          }}
        >
          <Text style={styles.sectionLabel}>
            PREFERENCES
          </Text>

          <View style={styles.group}>
            <AnimatedRow onPress={chooseLanguage}>
              <View style={styles.rowText}>
                <Text style={styles.rowLabel}>
                  Learning language
                </Text>

                <Text style={styles.rowDescription}>
                  The language you're learning
                </Text>
              </View>

              <View style={styles.valueContainer}>
                <Text style={styles.rowValue}>
                  {language}
                </Text>

                <Text style={styles.arrow}>›</Text>
              </View>
            </AnimatedRow>

            <View style={styles.rowBorder} />

            <AnimatedRow onPress={chooseMode}>
              <View style={styles.rowText}>
                <Text style={styles.rowLabel}>
                  Conversation mode
                </Text>

                <Text style={styles.rowDescription}>
                  Control how Mirai interacts with you
                </Text>
              </View>

              <View style={styles.valueContainer}>
                <Text style={styles.rowValue}>
                  {mode}
                </Text>

                <Text style={styles.arrow}>›</Text>
              </View>
            </AnimatedRow>
          </View>
        </Animated.View>

        <Animated.View
          style={{
            opacity: miraiOpacity,
            transform: [
              {
                translateY: miraiTranslate,
              },
            ],
          }}
        >
          <Text style={styles.sectionLabel}>
            MIRAI
          </Text>

          <View style={styles.group}>
            <AnimatedRow onPress={showAbout}>
              <View style={styles.rowText}>
                <Text style={styles.rowLabel}>
                  About Mirai
                </Text>

                <Text style={styles.rowDescription}>
                  Learn more about your companion
                </Text>
              </View>

              <Text style={styles.arrow}>›</Text>
            </AnimatedRow>

            <View style={styles.rowBorder} />

            <AnimatedRow onPress={clearConversation}>
              <View style={styles.rowText}>
                <Text
                  style={[
                    styles.rowLabel,
                    styles.dangerLabel,
                  ]}
                >
                  Clear conversation
                </Text>

                <Text style={styles.rowDescription}>
                  Remove your current chat history
                </Text>
              </View>

              <Text
                style={[
                  styles.arrow,
                  styles.dangerArrow,
                ]}
              >
                ›
              </Text>
            </AnimatedRow>

            <View style={styles.rowBorder} />

            <AnimatedRow onPress={resetMirai}>
              <View style={styles.rowText}>
                <Text
                  style={[
                    styles.rowLabel,
                    styles.dangerLabel,
                  ]}
                >
                  Reset Mirai
                </Text>

                <Text style={styles.rowDescription}>
                  Reset Mirai's current state
                </Text>
              </View>

              <Text
                style={[
                  styles.arrow,
                  styles.dangerArrow,
                ]}
              >
                ›
              </Text>
            </AnimatedRow>
          </View>
        </Animated.View>

        <Animated.View
          style={{
            opacity: modesOpacity,
            transform: [
              {
                translateY: modesTranslate,
              },
            ],
          }}
        >
          <Text style={styles.sectionLabel}>
            MODES
          </Text>

          <View style={styles.modeGroup}>
            {MODES.map((item, index) => (
              <View key={item.value}>
                <AnimatedModeRow
                  item={item}
                  selected={mode === item.value}
                  onPress={() => setMode(item.value)}
                />

                {index < MODES.length - 1 && (
                  <View style={styles.rowBorder} />
                )}
              </View>
            ))}
          </View>
        </Animated.View>

        <Animated.View
          style={[
            styles.footer,
            {
              opacity: footerOpacity,
            },
          ]}
        >
          <Text style={styles.footerFlower}>
            🌸
          </Text>

          <Text style={styles.footerTitle}>
            Mirai
          </Text>

          <Text style={styles.version}>
            Version 1.0.0
          </Text>

          <Text style={styles.footerText}>
            Your future starts with one conversation.
          </Text>
        </Animated.View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#FFFDFE",
  },

  header: {
    height: 96,
    paddingTop: 42,
    paddingHorizontal: 20,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    backgroundColor: "#FFFFFF",
    borderBottomWidth: 1,
    borderBottomColor: "#F1ECEF",
  },

  backButton: {
    width: 32,
    height: 38,
    justifyContent: "center",
    alignItems: "flex-start",
  },

  back: {
    fontSize: 36,
    lineHeight: 36,
    color: "#2A2528",
    fontWeight: "300",
  },

  title: {
    fontSize: 18,
    fontWeight: "700",
    color: "#2A2528",
  },

  headerSpacer: {
    width: 32,
  },

  scroll: {
    flex: 1,
  },

  content: {
    paddingHorizontal: 20,
    paddingTop: 24,
    paddingBottom: 45,
  },

  sectionLabel: {
    fontSize: 11,
    fontWeight: "700",
    letterSpacing: 0.9,
    color: "#A49A9F",
    marginBottom: 9,
    marginTop: 7,
  },

  group: {
    borderRadius: 20,
    overflow: "hidden",
    backgroundColor: "#FFFFFF",
    borderWidth: 1,
    borderColor: "#F1ECEF",
    marginBottom: 23,
  },

  row: {
    minHeight: 72,
    paddingHorizontal: 18,
    paddingVertical: 12,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },

  rowPressed: {
    backgroundColor: "#FFFAFC",
  },

  pressed: {
    opacity: 0.6,
  },

  rowText: {
    flex: 1,
    paddingRight: 12,
  },

  rowLabel: {
    fontSize: 15,
    fontWeight: "600",
    color: "#2A2528",
  },

  rowDescription: {
    fontSize: 12,
    lineHeight: 17,
    color: "#9A9095",
    marginTop: 3,
    maxWidth: 230,
  },

  rowBorder: {
    height: 1,
    backgroundColor: "#F1ECEF",
    marginLeft: 18,
  },

  valueContainer: {
    flexDirection: "row",
    alignItems: "center",
    marginLeft: 8,
  },

  rowValue: {
    fontSize: 13,
    fontWeight: "500",
    color: "#8B8186",
  },

  arrow: {
    fontSize: 25,
    lineHeight: 27,
    color: "#B7ADB2",
    marginLeft: 6,
    fontWeight: "300",
  },

  dangerLabel: {
    color: "#C96C84",
  },

  dangerArrow: {
    color: "#D99AAA",
  },

  modeGroup: {
    borderRadius: 20,
    overflow: "hidden",
    backgroundColor: "#FFFFFF",
    borderWidth: 1,
    borderColor: "#F1ECEF",
    marginBottom: 23,
  },

  modeRow: {
    minHeight: 88,
    paddingHorizontal: 18,
    paddingVertical: 14,
    flexDirection: "row",
    alignItems: "center",
  },

  modeRowSelected: {
    backgroundColor: "#FFF7FA",
  },

  modeRadio: {
    width: 22,
    height: 22,
    borderRadius: 11,
    borderWidth: 2,
    borderColor: "#D8CDD2",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 13,
  },

  modeRadioInner: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: "#FF8FBA",
  },

  modeText: {
    flex: 1,
  },

  modeTitleRow: {
    flexDirection: "row",
    alignItems: "center",
  },

  modeTitle: {
    fontSize: 15,
    fontWeight: "700",
    color: "#2A2528",
  },

  modeTitleSelected: {
    color: "#D96B88",
  },

  activeText: {
    marginLeft: 8,
    fontSize: 9,
    fontWeight: "800",
    letterSpacing: 0.7,
    color: "#D96B88",
  },

  modeDescription: {
    fontSize: 12,
    lineHeight: 17,
    color: "#9A9095",
    marginTop: 4,
    paddingRight: 8,
  },

  footer: {
    alignItems: "center",
    paddingTop: 10,
    paddingBottom: 12,
  },

  footerFlower: {
    fontSize: 25,
    marginBottom: 7,
  },

  footerTitle: {
    fontSize: 15,
    fontWeight: "700",
    color: "#2A2528",
  },

  version: {
    fontSize: 11,
    color: "#B5ACB0",
    marginTop: 3,
  },

  footerText: {
    fontSize: 11,
    color: "#B5ACB0",
    marginTop: 8,
  },
});