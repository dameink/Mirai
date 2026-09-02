import {
  createContext,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";

export type Mode = "Auto" | "Casual" | "Learning";

type SettingsContextType = {
  language: string;
  mode: Mode;
  setLanguage: (language: string) => void;
  setMode: (mode: Mode) => void;
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

  const value = useMemo(
    () => ({
      language,
      mode,
      setLanguage,
      setMode,
    }),
    [language, mode],
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