
import { useState } from "react";
import {
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
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setError("");
    setLoading(true);

    try {
      if (isRegister) {
        await register(email.trim(), password);
      } else {
        await login(email.trim(), password);
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

  return (
    <View style={styles.container}>
      <Text style={styles.sakura}>🌸</Text>

      <Text style={styles.title}>Mirai</Text>

      <Text style={styles.heading}>
        {isRegister ? "Create account" : "Welcome back"}
      </Text>

      <TextInput
        style={styles.input}
        placeholder="Email"
        placeholderTextColor="#A99A91"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        keyboardType="email-address"
      />

      <TextInput
        style={styles.input}
        placeholder="Password"
        placeholderTextColor="#A99A91"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />

      {error ? <Text style={styles.error}>{error}</Text> : null}

      <Pressable
        style={({ pressed }) => [
          styles.button,
          pressed && styles.buttonPressed,
          loading && styles.disabled,
        ]}
        onPress={handleSubmit}
        disabled={loading}
      >
        <Text style={styles.buttonText}>
          {loading
            ? "Please wait..."
            : isRegister
            ? "Create account"
            : "Login"}
        </Text>
      </Pressable>

      <Pressable
        onPress={() => {
          setIsRegister(!isRegister);
          setError("");
        }}
      >
        <Text style={styles.switchText}>
          {isRegister
            ? "Already have an account? Login"
            : "Don't have an account? Register"}
        </Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F7F0E6",
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 32,
  },

  sakura: {
    fontSize: 50,
    marginBottom: 8,
  },

  title: {
    fontSize: 46,
    fontWeight: "600",
    color: "#D9A6A6",
    letterSpacing: 1,
  },

  heading: {
    marginTop: 24,
    marginBottom: 24,
    fontSize: 22,
    fontWeight: "600",
    color: "#6F625B",
  },

  input: {
    width: "100%",
    height: 52,
    borderRadius: 26,
    backgroundColor: "#FFFFFF",
    paddingHorizontal: 20,
    marginBottom: 14,
    color: "#4F4540",
  },

  error: {
    color: "#B85C5C",
    textAlign: "center",
    marginBottom: 12,
  },

  button: {
    marginTop: 10,
    width: "100%",
    height: 54,
    borderRadius: 27,
    backgroundColor: "#D9A6A6",
    justifyContent: "center",
    alignItems: "center",
  },

  buttonPressed: {
    opacity: 0.7,
  },

  disabled: {
    opacity: 0.5,
  },

  buttonText: {
    color: "#FFFFFF",
    fontSize: 17,
    fontWeight: "600",
  },

  switchText: {
    marginTop: 22,
    color: "#8E7C72",
    fontSize: 14,
  },
});