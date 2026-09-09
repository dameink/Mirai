import { useState } from "react";
import {
  Alert,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { router, useLocalSearchParams } from "expo-router";

export default function ResetCodeScreen() {
  const { email } = useLocalSearchParams<{ email?: string }>();

  const [code, setCode] = useState("");

  const handleContinue = () => {
    if (!email) {
      Alert.alert("Error", "Email is missing.");
      return;
    }

    if (code.length !== 6) {
      Alert.alert("Invalid code", "Please enter the 6-digit code.");
      return;
    }

    router.push({
      pathname: "/new-password",
      params: {
        email,
        code,
      },
    });
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <View style={styles.content}>
        <Text style={styles.logo}>Mirai 🌸</Text>

        <Text style={styles.title}>Enter reset code</Text>

        <Text style={styles.description}>
          We sent a 6-digit reset code to{" "}
          <Text style={styles.email}>
            {email || "your email"}
          </Text>
        </Text>

        <TextInput
          style={styles.codeInput}
          value={code}
          onChangeText={(text) =>
            setCode(
              text.replace(/[^0-9]/g, "").slice(0, 6)
            )
          }
          placeholder="000000"
          placeholderTextColor="#B8A9A0"
          keyboardType="number-pad"
          maxLength={6}
          textAlign="center"
        />

        <Pressable
          onPress={handleContinue}
          style={({ pressed }) => [
            styles.button,
            pressed && styles.buttonPressed,
          ]}
        >
          <Text style={styles.buttonText}>Continue</Text>
        </Pressable>

        <Pressable
          onPress={() => router.back()}
          style={({ pressed }) => [
            styles.backButton,
            pressed && styles.buttonPressed,
          ]}
        >
          <Text style={styles.backText}>Back</Text>
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F7F0E6",
  },

  content: {
    flex: 1,
    justifyContent: "center",
    paddingHorizontal: 28,
  },

  logo: {
    fontSize: 24,
    fontWeight: "700",
    color: "#5C4A42",
    textAlign: "center",
    marginBottom: 36,
  },

  title: {
    fontSize: 28,
    fontWeight: "700",
    color: "#3F332E",
    textAlign: "center",
    marginBottom: 14,
  },

  description: {
    fontSize: 15,
    lineHeight: 22,
    color: "#7C6B63",
    textAlign: "center",
    marginBottom: 28,
  },

  email: {
    fontWeight: "600",
    color: "#5C4A42",
  },

  codeInput: {
    height: 58,
    backgroundColor: "#FFFFFF",
    borderRadius: 16,
    fontSize: 24,
    letterSpacing: 8,
    color: "#3F332E",
    marginBottom: 18,
    paddingHorizontal: 20,
  },

  button: {
    height: 54,
    borderRadius: 16,
    backgroundColor: "#D9A6A6",
    alignItems: "center",
    justifyContent: "center",
  },

  buttonPressed: {
    opacity: 0.7,
  },

  buttonText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "700",
  },

  backButton: {
    alignItems: "center",
    marginTop: 16,
    paddingVertical: 8,
  },

  backText: {
    color: "#B27F7F",
    fontSize: 14,
    fontWeight: "600",
  },
});