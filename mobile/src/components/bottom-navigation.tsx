
import { router } from "expo-router";
import { Pressable, StyleSheet, Text, View } from "react-native";

export type TabRouteName =
  | "chat"
  | "mirai"
  | "learn"
  | "profile";

const items: {
  route: TabRouteName;
  icon: string;
  label: string;
}[] = [
  {
    route: "chat",
    icon: "💬",
    label: "Chat",
  },
  {
    route: "mirai",
    icon: "💗",
    label: "Mirai",
  },
  {
    route: "learn",
    icon: "📚",
    label: "Learn",
  },
  {
    route: "profile",
    icon: "👤",
    label: "Me",
  },
];

export function BottomNavigation({
  activeRoute,
}: {
  activeRoute: TabRouteName;
}) {
  const navigateToTab = (targetRoute: TabRouteName) => {
    if (targetRoute === activeRoute) {
      return;
    }

    router.push(`/(tabs)/${targetRoute}`);
  };

  return (
    <View style={styles.bottomBar}>
      {items.map((item) => {
        const isActive = item.route === activeRoute;

        return (
          <Pressable
            key={item.route}
            accessibilityRole="tab"
            accessibilityState={{
              selected: isActive,
            }}
            style={styles.navItem}
            onPress={() => navigateToTab(item.route)}
          >
            <Text
              style={[
                styles.navIcon,
                isActive && styles.navIconActive,
              ]}
            >
              {item.icon}
            </Text>

            <Text
              style={[
                styles.navText,
                isActive && styles.navTextActive,
              ]}
            >
              {item.label}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  bottomBar: {
    height: 78,
    paddingBottom: 8,
    paddingTop: 8,
    flexDirection: "row",
    justifyContent: "space-around",
    alignItems: "center",
    backgroundColor: "#FFFFFF",
    borderTopWidth: 1,
    borderTopColor: "#F1ECEF",
  },

  navItem: {
    alignItems: "center",
    justifyContent: "center",
    width: 70,
  },

  navIcon: {
    fontSize: 21,
    opacity: 0.55,
  },

  navIconActive: {
    opacity: 1,
  },

  navText: {
    fontSize: 11,
    color: "#999999",
    marginTop: 3,
  },

  navTextActive: {
    color: "#FF6FA7",
    fontWeight: "600",
  },
});
