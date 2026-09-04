import { Stack } from "expo-router";
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
        await registerForPushNotificationsAsync(token);
      } catch (error) {
        console.log("Push notification registration failed:", error);
      }
    };

    registerNotifications();
  }, [user, loading]);

  return null;
}

export default function RootLayout() {
  return (
    <AuthProvider>
      <SettingsProvider>
        <NotificationRegistration />

        <Stack>
          <Stack.Screen name="index" options={{ headerShown: false }} />
          <Stack.Screen name="login" options={{ headerShown: false }} />
          <Stack.Screen name="register" options={{ headerShown: false }} />
          <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        </Stack>
      </SettingsProvider>
    </AuthProvider>
  );
}