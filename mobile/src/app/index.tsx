
import { Pressable, StyleSheet, Text, View } from "react-native";
import { router } from "expo-router";
import { useEffect } from "react";
import { useAuth } from "../auth/AuthContext";

export default function Index() {
  const { user, loading } = useAuth();

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [loading, user]);

  if (loading || !user) {
    return null;
  }

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.sakura}>🌸</Text>

        <Text style={styles.title}>Mirai</Text>

        <Text style={styles.subtitle}>
          Your companion for learning and growing
        </Text>

        <Pressable
          style={({ pressed }) => [
            styles.button,
            pressed && styles.buttonPressed,
          ]}
          onPress={() => router.replace("/chat")}
        >
          <Text style={styles.buttonText}>Start</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F7F0E6",
    justifyContent: "center",
    alignItems: "center",
  },

  content: {
    alignItems: "center",
    width: "100%",
    paddingHorizontal: 32,
  },

  sakura: {
    fontSize: 58,
    marginBottom: 8,
  },

  title: {
    fontSize: 52,
    fontWeight: "600",
    color: "#D9A6A6",
    letterSpacing: 1,
  },

  subtitle: {
    marginTop: 12,
    fontSize: 16,
    color: "#8E7C72",
    textAlign: "center",
  },

  button: {
    marginTop: 48,
    width: 220,
    height: 56,
    borderRadius: 28,
    backgroundColor: "#D9A6A6",
    justifyContent: "center",
    alignItems: "center",
  },

  buttonPressed: {
    opacity: 0.7,
  },

  buttonText: {
    color: "#FFFFFF",
    fontSize: 18,
    fontWeight: "600",
  },
});
