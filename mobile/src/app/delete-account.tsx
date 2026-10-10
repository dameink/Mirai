import { useState } from "react";
import { Alert, Pressable, StyleSheet, Text, TextInput, View } from "react-native";
import { router } from "expo-router";
import { useAuth } from "../auth/AuthContext";
import { clearPending } from "../storage/outbox";
import * as SecureStore from "expo-secure-store";
import { authFetch, clearTokens } from "../auth/auth";

export default function DeleteAccountScreen() {
  const { user } = useAuth();
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const removeAccount = async () => {
    setBusy(true);
    setError("");
    try {
      const response = await authFetch("/auth/account", {
        method: "DELETE", body: JSON.stringify({ password }),
      });
      if (!response.ok) {
        if (response.status === 403) throw new Error("Incorrect password.");
        if (response.status === 429) throw new Error("Too many attempts. Please wait a minute.");
        throw new Error("Deletion was not confirmed. Please try again.");
      }
      const cleanup = user ? await Promise.allSettled([
        clearPending(String(user.id)),
        SecureStore.deleteItemAsync(`mirai_settings_${user.id}`),
      ]) : [];
      // A failed local cleanup must not leave a deleted account signed in.
      await clearTokens();
      setPassword("");
      if (cleanup.some(result => result.status === "rejected")) {
        Alert.alert("Account deleted", "Some saved data could not be removed from this device. Clear the app's storage in Android settings before sharing the device.");
      }
      router.replace("/login");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Deletion was not confirmed. Please try again.");
    } finally {
      setBusy(false);
    }
  };

  const confirm = () => Alert.alert(
    "Permanently delete account?",
    "Your account, conversations, memories and learning progress will be deleted. This cannot be undone.",
    [
      { text: "Cancel", style: "cancel" },
      { text: "Delete account", style: "destructive", onPress: () => { void removeAccount(); } },
    ],
  );

  return <View style={styles.container}>
    <Text style={styles.title}>Delete account</Text>
    <Text>Your conversations, memories and learning progress will be permanently removed from the active service. Enter your password to continue.</Text>
    <TextInput accessibilityLabel="Current password" placeholder="Current password" secureTextEntry autoCapitalize="none" autoCorrect={false} textContentType="password" value={password} onChangeText={setPassword} editable={!busy} style={styles.input} />
    {error ? <Text accessibilityRole="alert" style={styles.error}>{error}</Text> : null}
    <Pressable accessibilityRole="button" disabled={busy || !password} onPress={confirm} style={[styles.button, (busy || !password) && styles.disabled]}>
      <Text style={styles.buttonText}>{busy ? "Deleting…" : "Delete account permanently"}</Text>
    </Pressable>
    <Pressable accessibilityRole="button" disabled={busy} onPress={() => router.back()} style={styles.cancel}><Text>Cancel</Text></Pressable>
  </View>;
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, paddingTop: 90, gap: 20, backgroundColor: "#FFFDFE" },
  title: { fontSize: 24, fontWeight: "700" },
  input: { borderWidth: 1, borderColor: "#D8CDD2", borderRadius: 12, padding: 16 },
  button: { backgroundColor: "#A72C48", borderRadius: 12, padding: 16, alignItems: "center" },
  buttonText: { color: "white", fontWeight: "700" },
  disabled: { opacity: 0.5 },
  error: { color: "#A72C48" },
  cancel: { padding: 16, alignItems: "center" },
});
