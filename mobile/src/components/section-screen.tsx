import { ReactNode } from "react";
import { ScrollView, StyleSheet, Text, View } from "react-native";
import {
  BottomNavigation,
  TabRouteName,
} from "./bottom-navigation";

type RouteName = Exclude<TabRouteName, "chat">;

type SectionScreenProps = {
  activeRoute: RouteName;
  eyebrow: string;
  title: string;
  description: string;
  children?: ReactNode;
};

export function SectionScreen({
  activeRoute,
  eyebrow,
  title,
  description,
  children,
}: SectionScreenProps) {
  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        <Text style={styles.eyebrow}>{eyebrow}</Text>

        <Text style={styles.title}>{title}</Text>

        <Text style={styles.description}>
          {description}
        </Text>

        {children}
      </ScrollView>

      <BottomNavigation activeRoute={activeRoute} />
    </View>
  );
}

export const sectionStyles = StyleSheet.create({
  card: {
    marginTop: 32,
    padding: 20,
    borderRadius: 22,
    backgroundColor: "#FFF0F6",
  },

  cardTitle: {
    fontSize: 17,
    fontWeight: "700",
    color: "#2A2528",
    marginBottom: 7,
  },

  cardText: {
    fontSize: 15,
    lineHeight: 22,
    color: "#746B70",
  },

  settingsButton: {
    marginTop: 14,
    paddingHorizontal: 20,
    minHeight: 58,
    borderRadius: 18,
    backgroundColor: "#FFFFFF",
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    borderWidth: 1,
    borderColor: "#F1ECEF",
  },

  settingsButtonText: {
    fontSize: 16,
    fontWeight: "600",
    color: "#2A2528",
  },

  settingsArrow: {
    fontSize: 28,
    color: "#FF6FA7",
    lineHeight: 30,
  },
});

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#FFFDFE",
  },

  scroll: {
    flex: 1,
  },

  content: {
    paddingHorizontal: 24,
    paddingTop: 68,
    paddingBottom: 32,
  },

  eyebrow: {
    fontSize: 14,
    fontWeight: "600",
    color: "#FF6FA7",
    marginBottom: 12,
  },

  title: {
    fontSize: 34,
    lineHeight: 40,
    fontWeight: "700",
    color: "#282326",
  },

  description: {
    marginTop: 12,
    fontSize: 16,
    lineHeight: 24,
    color: "#746B70",
  },
});