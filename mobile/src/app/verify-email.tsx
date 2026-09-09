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

export default function VerifyEmailScreen() {
  const { email } = useLocalSearchParams<{ email?: string }>();

  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);

  const handleVerify = async () => {
    if (!email) {
      Alert.alert("Error", "Email is missing.");
      return;
    }

    if (code.length !== 6) {
      Alert.alert("Invalid code", "Please enter the 6-digit code.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `${process.env.EXPO_PUBLIC_API_URL}/auth/verify-email`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email,
            code,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        Alert.alert(
          "Verification failed",
          data.detail || "Invalid or expired verification code."
        );
        return;
      }

      Alert.alert(
        "Email verified",
        "Your email has been successfully verified.",
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

  const handleResend = async () => {
    if (!email) {
      Alert.alert("Error", "Email is missing.");
      return;
    }

    setResending(true);

    try {
      const response = await fetch(
        `${process.env.EXPO_PUBLIC_API_URL}/auth/resend-verification`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        Alert.alert(
          "Could not resend code",
          data.detail || "Please try again later."
        );
        return;
      }

      setCode("");

      Alert.alert(
        "Code sent",
        "A new verification code has been sent to your email."
      );
    } catch {
      Alert.alert(
        "Connection error",
        "Could not connect to the server."
      );
    } finally {
      setResending(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <View style={styles.content}>
        <Text style={styles.logo}>Mirai 🌸</Text>

        <Text style={styles.title}>Verify your email</Text>

        <Text style={styles.description}>
          We sent a 6-digit verification code to{" "}
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
          editable={!loading && !resending}
        />

        <Pressable
          onPress={handleVerify}
          disabled={loading || resending}
          style={({ pressed }) => [
            styles.button,
            pressed && styles.buttonPressed,
            (loading || resending) && styles.buttonDisabled,
          ]}
        >
          <Text style={styles.buttonText}>
            {loading ? "Verifying..." : "Verify email"}
          </Text>
        </Pressable>

        <Pressable
          onPress={handleResend}
          disabled={loading || resending}
          style={({ pressed }) => [
            styles.resendButton,
            pressed && styles.buttonPressed,
            (loading || resending) && styles.buttonDisabled,
          ]}
        >
          <Text style={styles.resendText}>
            {resending ? "Sending..." : "Resend code"}
          </Text>
        </Pressable>

        <Pressable
          onPress={() => router.back()}
          disabled={loading || resending}
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

  buttonDisabled: {
    opacity: 0.55,
  },

  buttonText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "700",
  },

  resendButton: {
    alignItems: "center",
    marginTop: 16,
    paddingVertical: 6,
  },

  resendText: {
    color: "#B27F7F",
    fontSize: 14,
    fontWeight: "600",
  },

  backButton: {
    alignItems: "center",
    marginTop: 12,
    paddingVertical: 8,
  },

  backText: {
    color: "#B27F7F",
    fontSize: 14,
    fontWeight: "600",
  },
});