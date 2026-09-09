import { useState } from "react";
import {
  Alert,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { router } from "expo-router";

export default function ForgotPasswordScreen() {
  const [email, setEmail] = useState("");
  const [focused, setFocused] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSendCode = async () => {
    setError("");

    const trimmedEmail = email.trim();

    if (!trimmedEmail) {
      setError("Please enter your email.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `${process.env.EXPO_PUBLIC_API_URL}/auth/forgot-password`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: trimmedEmail,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        setError(
          data.detail || "Could not send reset code. Please try again."
        );
        return;
      }

      router.push({
        pathname: "/reset-code",
        params: {
          email: trimmedEmail,
        },
      });
    } catch {
      setError(
        "Could not connect to the server. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.screen}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
    >
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.container}>
          <View style={styles.brand}>
            <Text style={styles.sakura}>🌸</Text>

            <Text style={styles.title}>Mirai</Text>

            <Text style={styles.subtitle}>
              Reset your password
            </Text>
          </View>

          <View style={styles.card}>
            <Pressable
              onPress={() => router.back()}
              disabled={loading}
              style={({ pressed }) => [
                styles.backButton,
                pressed && styles.buttonPressed,
              ]}
            >
              <Text style={styles.backText}>‹ Back</Text>
            </Pressable>

            <Text style={styles.heading}>
              Forgot your password?
            </Text>

            <Text style={styles.description}>
              Enter your email and we'll send you a code to reset
              your password.
            </Text>

            <View style={styles.form}>
              <View>
                <Text style={styles.label}>Email</Text>

                <TextInput
                  style={[
                    styles.input,
                    focused && styles.inputFocused,
                    error && styles.inputError,
                  ]}
                  placeholder="Enter your email"
                  placeholderTextColor="#B4A69E"
                  value={email}
                  onChangeText={(text) => {
                    setEmail(text);
                    if (error) {
                      setError("");
                    }
                  }}
                  autoCapitalize="none"
                  autoCorrect={false}
                  keyboardType="email-address"
                  textContentType="emailAddress"
                  onFocus={() => setFocused(true)}
                  onBlur={() => setFocused(false)}
                  editable={!loading}
                />
              </View>
            </View>

            {error ? (
              <View style={styles.errorBox}>
                <Text style={styles.errorText}>{error}</Text>
              </View>
            ) : null}

            <Pressable
              onPress={handleSendCode}
              disabled={loading}
              style={({ pressed }) => [
                styles.button,
                pressed && styles.buttonPressed,
                loading && styles.buttonDisabled,
              ]}
            >
              <Text style={styles.buttonText}>
                {loading ? "Sending..." : "Send reset code"}
              </Text>
            </Pressable>
          </View>

          <Text style={styles.footer}>
            Learn languages. Build memories. Grow with Mirai.
          </Text>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: "#F7F0E6",
  },

  scrollContent: {
    flexGrow: 1,
    justifyContent: "center",
    paddingVertical: 24,
  },

  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 24,
  },

  brand: {
    alignItems: "center",
    marginBottom: 28,
  },

  sakura: {
    fontSize: 42,
    marginBottom: 4,
  },

  title: {
    fontSize: 44,
    fontWeight: "600",
    color: "#D9A6A6",
    letterSpacing: 1,
  },

  subtitle: {
    marginTop: 7,
    color: "#8E7C72",
    fontSize: 14,
    textAlign: "center",
  },

  card: {
    width: "100%",
    maxWidth: 420,
    backgroundColor: "#FFFDFC",
    borderRadius: 28,
    paddingHorizontal: 24,
    paddingVertical: 28,

    shadowColor: "#6F625B",
    shadowOffset: {
      width: 0,
      height: 8,
    },
    shadowOpacity: 0.08,
    shadowRadius: 20,
    elevation: 5,
  },

  backButton: {
    alignSelf: "flex-start",
    paddingVertical: 4,
    marginBottom: 12,
  },

  backText: {
    color: "#B27F7F",
    fontSize: 14,
    fontWeight: "600",
  },

  heading: {
    fontSize: 24,
    fontWeight: "600",
    color: "#514640",
    textAlign: "center",
  },

  description: {
    marginTop: 8,
    marginBottom: 24,
    color: "#9A8B82",
    fontSize: 14,
    lineHeight: 20,
    textAlign: "center",
  },

  form: {
    gap: 16,
  },

  label: {
    marginBottom: 7,
    marginLeft: 4,
    color: "#6F625B",
    fontSize: 13,
    fontWeight: "600",
  },

  input: {
    width: "100%",
    height: 54,
    borderRadius: 16,
    backgroundColor: "#F7F0E6",
    borderWidth: 1,
    borderColor: "#EEE3D8",
    paddingHorizontal: 17,
    color: "#4F4540",
    fontSize: 15,
  },

  inputFocused: {
    borderColor: "#D9A6A6",
    backgroundColor: "#FFFDFC",
  },

  inputError: {
    borderColor: "#D88D8D",
  },

  errorBox: {
    marginTop: 14,
    paddingHorizontal: 14,
    paddingVertical: 11,
    borderRadius: 14,
    backgroundColor: "#FCEEEE",
  },

  errorText: {
    color: "#B85C5C",
    fontSize: 13,
    lineHeight: 18,
    textAlign: "center",
  },

  button: {
    width: "100%",
    height: 54,
    marginTop: 20,
    borderRadius: 27,
    backgroundColor: "#D9A6A6",
    justifyContent: "center",
    alignItems: "center",

    shadowColor: "#C88F8F",
    shadowOffset: {
      width: 0,
      height: 5,
    },
    shadowOpacity: 0.18,
    shadowRadius: 10,
    elevation: 3,
  },

  buttonPressed: {
    opacity: 0.75,
    transform: [{ scale: 0.99 }],
  },

  buttonDisabled: {
    opacity: 0.55,
  },

  buttonText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "600",
  },

  footer: {
    marginTop: 22,
    color: "#AA9B91",
    fontSize: 11,
    textAlign: "center",
  },
});