import { Stack } from "expo-router";
import { SettingsProvider } from "../../context/settings-context";
import { AuthProvider } from "../auth/AuthContext";

export default function RootLayout() {
  return (
    <AuthProvider>
      <Stack>
        ...
      </Stack>
    </AuthProvider>
  );
}