import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { authFetch } from "../src/auth/auth";

export type Mode = "Auto" | "Casual" | "Learning";

type SettingsContextType = {
  language: string;
  mode: Mode;
  notificationsEnabled: boolean;
  setLanguage: (language: string) => void;
  setMode: (mode: Mode) => void;
  setNotificationsEnabled: (enabled: boolean) => void;
};

const SettingsContext =
  createContext<SettingsContextType | undefined>(undefined);

export function SettingsProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [language, setLanguage] = useState("English");
  const [mode, setMode] = useState<Mode>("Auto");

  const [notificationsEnabled, setNotificationsEnabled] =
    useState(true);

  useEffect(() => {
    const loadNotificationSettings = async () => {
      try {
        const response = await authFetch(
          "/notifications/settings",
        );

        if (!response.ok) {
          console.log(
            "Failed to load notification settings:",
            response.status,
          );
          return;
        }

        const data = await response.json();

        if (
          typeof data.notifications_enabled ===
          "boolean"
        ) {
          setNotificationsEnabled(
            data.notifications_enabled,
          );
        }
      } catch (error) {
        console.log(
          "Failed to load notification settings:",
          error,
        );
      }
    };

    loadNotificationSettings();
  }, []);

  const updateNotificationsEnabled = async (
    enabled: boolean,
  ) => {
    const previousValue = notificationsEnabled;

    // Update UI immediately
    setNotificationsEnabled(enabled);

    try {
      const response = await authFetch(
        "/notifications/settings",
        {
          method: "PATCH",
          body: JSON.stringify({
            enabled,
          }),
        },
      );

      if (!response.ok) {
        console.log(
          "Failed to update notification settings:",
          response.status,
        );

        // Roll back if server update failed
        setNotificationsEnabled(previousValue);
      }
    } catch (error) {
      console.log(
        "Failed to update notification settings:",
        error,
      );

      // Roll back if request failed
      setNotificationsEnabled(previousValue);
    }
  };

  const value = useMemo(
    () => ({
      language,
      mode,
      notificationsEnabled,
      setLanguage,
      setMode,
      setNotificationsEnabled:
        updateNotificationsEnabled,
    }),
    [
      language,
      mode,
      notificationsEnabled,
    ],
  );

  return (
    <SettingsContext.Provider value={value}>
      {children}
    </SettingsContext.Provider>
  );
}

export function useSettings() {
  const context = useContext(SettingsContext);

  if (!context) {
    throw new Error(
      "useSettings must be used inside SettingsProvider",
    );
  }

  return context;
}