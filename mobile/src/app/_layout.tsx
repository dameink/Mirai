import { Stack } from "expo-router";
import { ActivityIndicator, Pressable, Text, View } from "react-native";
import { useEffect } from "react";
import { SettingsProvider } from "../../context/settings-context";
import { AuthProvider, useAuth } from "../auth/AuthContext";
import { getAccessToken } from "../auth/auth";
import { registerForPushNotificationsAsync } from "../notifications/notifications";

function NotificationRegistration() {
  const { user, loading } = useAuth();

  useEffect(() => {
    if (loading || !user) {
      return;
    }

    const registerNotifications = async () => {
      const token = await getAccessToken();

      if (!token) {
        return;
      }

      try {
        await registerForPushNotificationsAsync();
      } catch (error) {
        console.log("Push notification registration failed:", error);
      }
    };

    registerNotifications();
  }, [user, loading]);

  return null;
}

function SessionGate({ children }: { children: React.ReactNode }) {
  const { loading, sessionError, retrySession } = useAuth();
  if (!loading && !sessionError) return children;
  return <View style={{ flex: 1, justifyContent: "center", alignItems: "center", padding: 32, backgroundColor: "#FFFDFE" }}>
    {loading ? <><ActivityIndicator /><Text style={{ marginTop: 16 }}>Connecting to Mirai…</Text></> : <>
      <Text style={{ textAlign: "center", marginBottom: 20 }}>Could not reconnect. Your sign-in is saved.</Text>
      <Pressable accessibilityRole="button" onPress={() => void retrySession()} style={{ padding: 16 }}><Text>Try again</Text></Pressable>
    </>}
  </View>;
}

export default function RootLayout() {
  return (
    <AuthProvider>
      <SessionGate>
      <SettingsProvider>
        <NotificationRegistration />

        <Stack>
          <Stack.Screen name="index" options={{ headerShown: false }} />
          <Stack.Screen name="login" options={{ headerShown: false }} />
          <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        </Stack>
      </SettingsProvider>
      </SessionGate>
    </AuthProvider>
  );
}