import React, {
  createContext,
  useContext,
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  getAccessToken,
  getRefreshToken,
  getSessionVersion,
  login as loginRequest,
  register as registerRequest,
  logout as logoutRequest,
  authFetch,
  onSessionExpired,
} from "./auth";

type User = {
  id: number | string;
  email: string;
  created_at: string;
};

type AuthContextType = {
  user: User | null;
  loading: boolean;
  sessionError: boolean;
  retrySession: () => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(
  undefined
);

export function AuthProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [sessionError, setSessionError] = useState(false);

  useEffect(() => onSessionExpired(() => setUser(null)), []);

  const refreshUser = useCallback(async () => {
    const version = getSessionVersion();
    const token = await getAccessToken();

    if (!token && !await getRefreshToken()) {
      setUser(null);
      return;
    }

    try {
      const response = await authFetch("/auth/me");

      if (response.status === 401 || response.status === 403) {
        if (version === getSessionVersion()) setUser(null);
        return;
      }
      if (!response.ok) {
        throw new Error("Could not restore your session. Please try signing in again.");
      }

      const data = await response.json();
      if (version === getSessionVersion()) setUser(data);
    } catch (error) {
      if (version === getSessionVersion()) setUser(null);
      throw error;
    }
  }, []);

  const retrySession = useCallback(async () => {
        setLoading(true);
        setSessionError(false);
      try {
        await refreshUser();
      } catch {
        setSessionError(true);
      } finally {
        setLoading(false);
      }
  }, [refreshUser]);

  // Initial hydration uses the same guarded path as an explicit reconnect.
  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => { void retrySession(); }, [retrySession]);

  const login = async (email: string, password: string) => {
    await loginRequest(email, password);
    await refreshUser();
  };

  const register = async (email: string, password: string) => {
    await registerRequest(email, password);
  };

  const logout = async () => {
    await logoutRequest();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        sessionError,
        retrySession,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider"
    );
  }

  return context;
}