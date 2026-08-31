import { router } from "expo-router";
import {
  Alert,
  Pressable,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  View,
} from "react-native";
import { useState } from "react";

type Appearance = "System" | "Light" | "Dark";

export default function SettingsScreen() {
  const [notifications, setNotifications] = useState(true);
  const [dailyReminder, setDailyReminder] = useState(false);

  const [language, setLanguage] = useState("English");
  const [appearance, setAppearance] =
    useState<Appearance>("System");

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

  const chooseAppearance = () => {
    Alert.alert(
      "Appearance",
      "Choose how Mirai looks.",
      [
        {
          text: "System",
          onPress: () => setAppearance("System"),
        },
        {
          text: "Light",
          onPress: () => setAppearance("Light"),
        },
        {
          text: "Dark",
          onPress: () => setAppearance("Dark"),
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
          onPress: () => {
            // Connect this to the chat storage when the
            // conversation persistence layer is exposed here.
            Alert.alert(
              "Conversation cleared",
              "Your conversation history has been cleared.",
            );
          },
        },
      ],
    );
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
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
      </View>

      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        {/* Preferences */}
        <Text style={styles.sectionLabel}>PREFERENCES</Text>

        <View style={styles.group}>
          <Pressable
            style={({ pressed }) => [
              styles.row,
              pressed && styles.rowPressed,
            ]}
            onPress={chooseLanguage}
          >
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
          </Pressable>

          <View style={styles.rowBorder} />

          <View style={styles.row}>
            <View style={styles.rowText}>
              <Text style={styles.rowLabel}>
                Daily reminder
              </Text>

              <Text style={styles.rowDescription}>
                Keep your learning rhythm
              </Text>
            </View>

            <Switch
              value={dailyReminder}
              onValueChange={setDailyReminder}
              trackColor={{
                false: "#E8E2E5",
                true: "#FFB4CE",
              }}
              thumbColor="#FFFFFF"
              ios_backgroundColor="#E8E2E5"
            />
          </View>

          <View style={styles.rowBorder} />

          <View style={styles.row}>
            <View style={styles.rowText}>
              <Text style={styles.rowLabel}>
                Notifications
              </Text>

              <Text style={styles.rowDescription}>
                Messages and learning updates
              </Text>
            </View>

            <Switch
              value={notifications}
              onValueChange={setNotifications}
              trackColor={{
                false: "#E8E2E5",
                true: "#FFB4CE",
              }}
              thumbColor="#FFFFFF"
              ios_backgroundColor="#E8E2E5"
            />
          </View>
        </View>

        {/* Appearance */}
        <Text style={styles.sectionLabel}>
          APPEARANCE
        </Text>

        <View style={styles.group}>
          <Pressable
            style={({ pressed }) => [
              styles.row,
              pressed && styles.rowPressed,
            ]}
            onPress={chooseAppearance}
          >
            <View style={styles.rowText}>
              <Text style={styles.rowLabel}>
                Appearance
              </Text>

              <Text style={styles.rowDescription}>
                Choose how Mirai looks
              </Text>
            </View>

            <View style={styles.valueContainer}>
              <Text style={styles.rowValue}>
                {appearance}
              </Text>

              <Text style={styles.arrow}>›</Text>
            </View>
          </Pressable>
        </View>

        {/* Mirai */}
        <Text style={styles.sectionLabel}>MIRAI</Text>

        <View style={styles.group}>
          <Pressable
            style={({ pressed }) => [
              styles.row,
              pressed && styles.rowPressed,
            ]}
            onPress={showAbout}
          >
            <View style={styles.rowText}>
              <Text style={styles.rowLabel}>
                About Mirai
              </Text>

              <Text style={styles.rowDescription}>
                Learn more about your companion
              </Text>
            </View>

            <Text style={styles.arrow}>›</Text>
          </Pressable>

          <View style={styles.rowBorder} />

          <Pressable
            style={({ pressed }) => [
              styles.row,
              pressed && styles.rowPressed,
            ]}
            onPress={clearConversation}
          >
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
          </Pressable>
        </View>

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerFlower}>🌸</Text>

          <Text style={styles.footerTitle}>
            Mirai
          </Text>

          <Text style={styles.version}>
            Version 1.0.0
          </Text>

          <Text style={styles.footerText}>
            Your future starts with one conversation.
          </Text>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#FFFDFE",
  },

  /* Header */

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

  /* Scroll */

  scroll: {
    flex: 1,
  },

  content: {
    paddingHorizontal: 20,
    paddingTop: 24,
    paddingBottom: 45,
  },

  /* Sections */

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

  /* Rows */

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

  /* Values */

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

  /* Danger */

  dangerLabel: {
    color: "#C96C84",
  },

  dangerArrow: {
    color: "#D99AAA",
  },

  /* Footer */

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