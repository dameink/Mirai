import { View, Text, StyleSheet } from "react-native";

export default function ChatScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.avatar}>🌸</Text>

      <Text style={styles.title}>
        Mirai
      </Text>

      <Text>
        Hey! How was your day?
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },

  avatar: {
    fontSize: 70,
  },

  title: {
    fontSize: 36,
    fontWeight: "bold",
    marginBottom: 20,
  },
});