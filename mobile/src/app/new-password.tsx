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

export default function NewPasswordScreen() {
  const { email, code } = useLocalSearchParams<{
    email?: string;
    code?: string;
  }>();

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] =
    useState(false);
  const [loading, setLoading] = useState(false);

  const handleResetPassword = async () => {
    if (!email || !code) {
      Alert.alert("Error", "Reset information is missing.");
      return;
    }

    if (password.length < 8) {
      Alert.alert(
        "Password too short",
        "Your password must contain at least 8 characters."
      );
      return;
    }

    if (password !== confirmPassword) {
      Alert.alert(
        "Passwords do not match",
        "Please make sure both passwords are identical."
      );
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `${process.env.EXPO_PUBLIC_API_URL}/auth/reset-password`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email,
            code,
            new_password: password,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        Alert.alert(
          "Password reset failed",
          data.detail || "Could not reset your password."
        );
        return;
      }

      Alert.alert(
        "Password changed",
        "Your password has been successfully changed.",
        [
          {
            text: "Continue",
            onPress: () => router.replace("/login"),
          },
        ]
      );
    } catch {
      Alert.alert(
        "Connection error",
        "Could not connect to the server."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <View style={styles.content}>
        <Text style={styles.logo}>Mirai 🌸</Text>

        <Text style={styles.title}>Create a new password</Text>

        <Text style={styles.description}>
          Choose a new password for your Mirai account.
        </Text>

        <View style={styles.inputContainer}>
          <Text style={styles.label}>New password</Text>

          <View style={styles.passwordWrapper}>
            <TextInput
              style={styles.passwordInput}
              value={password}
              onChangeText={setPassword}
              placeholder="Enter new password"
              placeholderTextColor="#B8A9A0"
              secureTextEntry={!showPassword}
              autoCapitalize="none"
              autoCorrect={false}
              editable={!loading}
            />

            <Pressable
              onPress={() => setShowPassword(!showPassword)}
              disabled={loading}
              style={styles.showButton}
            >
              <Text style={styles.showText}>
                {showPassword ? "Hide" : "Show"}
              </Text>
            </Pressable>
          </View>
        </View>

        <View style={styles.inputContainer}>
          <Text style={styles.label}>Confirm password</Text>

          <View style={styles.passwordWrapper}>
            <TextInput
              style={styles.passwordInput}
              value={confirmPassword}
              onChangeText={setConfirmPassword}
              placeholder="Confirm new password"
              placeholderTextColor="#B8A9A0"
              secureTextEntry={!showConfirmPassword}
              autoCapitalize="none"
              autoCorrect={false}
              editable={!loading}
            />

            <Pressable
              onPress={() =>
                setShowConfirmPassword(!showConfirmPassword)
              }
              disabled={loading}
              style={styles.showButton}
            >
              <Text style={styles.showText}>
                {showConfirmPassword ? "Hide" : "Show"}
              </Text>
            </Pressable>
          </View>
        </View>

        <Text style={styles.requirement}>
          Password must be at least 8 characters.
        </Text>

        <Pressable
          onPress={handleResetPassword}
          disabled={loading}
          style={({ pressed }) => [
            styles.button,
            pressed && styles.buttonPressed,
            loading && styles.buttonDisabled,
          ]}
        >
          <Text style={styles.buttonText}>
            {loading ? "Changing password..." : "Change password"}
          </Text>
        </Pressable>

        <Pressable
          onPress={() => router.back()}
          disabled={loading}
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
    textAlignVertical: "center",
  },

  inputContainer: {
    marginBottom: 18,
  },

  label: {
    marginBottom: 7,
    marginLeft: 4,
    color: "#6F625B",
    fontSize: 13,
    fontWeight: "600",
  },

  passwordWrapper: {
    height: 54,
    backgroundColor: "#FFFFFF",
    borderRadius: 16,
    flexDirection: "row",
    alignItems: "center",
    paddingLeft: 17,
    paddingRight: 8,
  },

  passwordInput: {
    flex: 1,
    color: "#3F332E",
    fontSize: 15,
  },

  showButton: {
    paddingHorizontal: 10,
    paddingVertical: 8,
  },

  showText: {
    color: "#B27F7F",
    fontSize: 13,
    fontWeight: "600",
  },

  requirement: {
    color: "#9A8B82",
    fontSize: 12,
    marginTop: -4,
    marginLeft: 4,
  },

  button: {
    height: 54,
    borderRadius: 16,
    backgroundColor: "#D9A6A6",
    alignItems: "center",
    justifyContent: "center",
    marginTop: 24,
  },

  buttonPressed: {
    opacity: 0.7,
  },

  buttonDisabled: {
    opacity: 0.55,
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

