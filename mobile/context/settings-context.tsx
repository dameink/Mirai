import { createContext, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import { Alert } from "react-native";
import * as SecureStore from "expo-secure-store";
import { useAuth } from "../src/auth/AuthContext";
import { authFetch } from "../src/auth/auth";

export type Mode = "Auto" | "Casual" | "Learning";
type Settings = { language: string; mode: Mode; notificationsEnabled: boolean };
type SettingsContextType = Settings & {
  setLanguage: (language: string) => void;
  setMode: (mode: Mode) => void;
  setNotificationsEnabled: (enabled: boolean) => void;
};
const defaults: Settings = { language: "English", mode: "Auto", notificationsEnabled: true };
const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

export function SettingsProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const uid = user ? String(user.id) : null;
  const [state, setState] = useState<{ owner: string | null; values: Settings }>({ owner: null, values: defaults });
  const revision = useRef(0);
  const owner = useRef(uid);
  const writes = useRef<Promise<unknown>>(Promise.resolve());
  const values = state.owner === uid ? state.values : defaults;

  useEffect(() => {
    owner.current = uid;
    const version = ++revision.current;
    if (!uid) return;
    const current = () => owner.current === uid && revision.current === version;
    const key = `mirai_settings_${uid}`;
    void (async () => {
      try {
        const saved = await SecureStore.getItemAsync(key);
        if (saved && current()) {
          const cached = JSON.parse(saved);
          if (["English", "Japanese", "Spanish"].includes(cached.language) && ["Auto", "Casual", "Learning"].includes(cached.mode)) {
            setState({ owner: uid, values: { ...defaults, ...cached } });
          }
        }
        const [preferences, notifications] = await Promise.all([authFetch("/preferences"), authFetch("/notifications/settings")]);
        if (!preferences.ok || !notifications.ok) return;
        const [p, n] = await Promise.all([preferences.json(), notifications.json()]);
        if (current()) {
          const next = { language: p.language, mode: p.mode, notificationsEnabled: n.notifications_enabled };
          setState({ owner: uid, values: next });
          await SecureStore.setItemAsync(key, JSON.stringify(next));
        }
      } catch { /* Keep this account's cached preferences when offline. */ }
    })();
    return () => { if (owner.current === uid) owner.current = null; };
  }, [uid]);

  const update = (change: Partial<Settings>) => {
    if (!uid) return;
    ++revision.current; // Do not let an earlier profile fetch overwrite an edit.
    writes.current = writes.current.catch(() => {}).then(async () => {
      if (owner.current !== uid) return;
      const notifications = change.notificationsEnabled !== undefined;
      try {
        const response = await authFetch(notifications ? "/notifications/settings" : "/preferences", {
          method: "PATCH",
          body: JSON.stringify(notifications ? { enabled: change.notificationsEnabled } : change),
        });
        if (!response.ok) throw new Error("Settings could not be saved");
        if (owner.current !== uid) return;
        // Functional merge preserves independently queued edits.
        setState(previous => ({ owner: uid, values: { ...(previous.owner === uid ? previous.values : defaults), ...change } }));
        const key = `mirai_settings_${uid}`;
        const saved = await SecureStore.getItemAsync(key);
        await SecureStore.setItemAsync(key, JSON.stringify({ ...defaults, ...(saved ? JSON.parse(saved) : {}), ...change }));
      } catch {
        if (owner.current === uid) Alert.alert("Settings not saved", "Please check your connection and try again.");
      }
    });
  };

  return <SettingsContext.Provider value={{ ...values,
    setLanguage: language => update({ language }),
    setMode: mode => update({ mode }),
    setNotificationsEnabled: notificationsEnabled => update({ notificationsEnabled }),
  }}>{children}</SettingsContext.Provider>;
}

export function useSettings() {
  const context = useContext(SettingsContext);
  if (!context) throw new Error("useSettings must be used inside SettingsProvider");
  return context;
}
