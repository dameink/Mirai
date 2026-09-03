
import { useState } from "react";
import {
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { router } from "expo-router";
import { useAuth } from "../auth/AuthContext";

export default function LoginScreen() {
  const { login, register } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isRegister, setIsRegister] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [focusedField, setFocusedField] = useState<"email" | "password" | null>(
    null
  );

  const handleSubmit = async () => {
    setError("");

    const trimmedEmail = email.trim();

    if (!trimmedEmail || !password) {
      setError("Please enter your email and password.");
      return;
    }

    setLoading(true);

    try {
      if (isRegister) {
        await register(trimmedEmail, password);
      } else {
        await login(trimmedEmail, password);
      }

      router.replace("/chat");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Authentication failed"
      );
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setIsRegister((current) => !current);
    setError("");
    setPassword("");
  };

  return (
    <KeyboardAvoidingView
      style={styles.screen}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <View style={styles.container}>
        <View style={styles.brand}>
          <Text style={styles.sakura}>🌸</Text>
          <Text style={styles.title}>Mirai</Text>
          <Text style={styles.subtitle}>
            {isRegister
              ? "Start your journey with Mirai"
              : "Welcome back"}
          </Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.heading}>
            {isRegister ? "Create your account" : "Sign in"}
          </Text>

          <Text style={styles.description}>
            {isRegister
              ? "Create an account to begin your language journey."
              : "Continue your language journey with Mirai."}
          </Text>

          <View style={styles.form}>
            <View>
              <Text style={styles.label}>Email</Text>

              <TextInput
                style={[
                  styles.input,
                  focusedField === "email" && styles.inputFocused,
                  error && styles.inputError,
                ]}
                placeholder="Enter your email"
                placeholderTextColor="#B4A69E"
                value={email}
                onChangeText={(text) => {
                  setEmail(text);
                  if (error) setError("");
                }}
                autoCapitalize="none"
                autoCorrect={false}
                keyboardType="email-address"
                textContentType="emailAddress"
                onFocus={() => setFocusedField("email")}
                onBlur={() => setFocusedField(null)}
                editable={!loading}
              />
            </View>

            <View>
              <Text style={styles.label}>Password</Text>

              <View
                style={[
                  styles.passwordContainer,
                  focusedField === "password" && styles.inputFocused,
                  error && styles.inputError,
                ]}
              >
                <TextInput
                  style={styles.passwordInput}
                  placeholder="Enter your password"
                  placeholderTextColor="#B4A69E"
                  value={password}
                  onChangeText={(text) => {
                    setPassword(text);
                    if (error) setError("");
                  }}
                  secureTextEntry={!showPassword}
                  autoCapitalize="none"
                  autoCorrect={false}
                  textContentType="password"
                  onFocus={() => setFocusedField("password")}
                  onBlur={() => setFocusedField(null)}
                  editable={!loading}
                />

                <Pressable
                  onPress={() => setShowPassword((current) => !current)}
                  style={styles.showButton}
                  disabled={loading}
                >
                  <Text style={styles.showText}>
                    {showPassword ? "Hide" : "Show"}
                  </Text>
                </Pressable>
              </View>
            </View>
          </View>

          {error ? (
            <View style={styles.errorBox}>
              <Text style={styles.errorText}>{error}</Text>
            </View>
          ) : null}

          <Pressable
            style={({ pressed }) => [
              styles.button,
              pressed && styles.buttonPressed,
              loading && styles.buttonDisabled,
            ]}
            onPress={handleSubmit}
            disabled={loading}
          >
            <Text style={styles.buttonText}>
              {loading
                ? isRegister
                  ? "Creating account..."
                  : "Signing in..."
                : isRegister
                ? "Create account"
                : "Login"}
            </Text>
          </Pressable>

          <View style={styles.divider}>
            <View style={styles.dividerLine} />
            <Text style={styles.dividerText}>or</Text>
            <View style={styles.dividerLine} />
          </View>

          <Pressable
            onPress={toggleMode}
            disabled={loading}
            style={({ pressed }) => [
              styles.switchButton,
              pressed && styles.switchPressed,
            ]}
          >
            <Text style={styles.switchQuestion}>
              {isRegister
                ? "Already have an account?"
                : "Don't have an account?"}
            </Text>

            <Text style={styles.switchAction}>
              {isRegister ? "Login" : "Create account"}
            </Text>
          </Pressable>
        </View>

        <Text style={styles.footer}>
          Learn languages. Build memories. Grow with Mirai.
        </Text>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: "#F7F0E6",
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

  passwordContainer: {
    width: "100%",
    height: 54,
    flexDirection: "row",
    alignItems: "center",
    borderRadius: 16,
    backgroundColor: "#F7F0E6",
    borderWidth: 1,
    borderColor: "#EEE3D8",
  },

  passwordInput: {
    flex: 1,
    height: "100%",
    paddingHorizontal: 17,
    color: "#4F4540",
    fontSize: 15,
  },

  showButton: {
    paddingHorizontal: 16,
    height: "100%",
    justifyContent: "center",
  },

  showText: {
    color: "#B27F7F",
    fontSize: 13,
    fontWeight: "600",
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

  divider: {
    flexDirection: "row",
    alignItems: "center",
    marginVertical: 22,
  },

  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: "#EEE3D8",
  },

  dividerText: {
    marginHorizontal: 12,
    color: "#B4A69E",
    fontSize: 12,
  },

  switchButton: {
    alignItems: "center",
    paddingVertical: 3,
  },

  switchPressed: {
    opacity: 0.6,
  },

  switchQuestion: {
    color: "#9A8B82",
    fontSize: 13,
  },

  switchAction: {
    marginTop: 4,
    color: "#B27F7F",
    fontSize: 14,
    fontWeight: "600",
  },

  footer: {
    marginTop: 22,
    color: "#AA9B91",
    fontSize: 11,
    textAlign: "center",
  },
});
