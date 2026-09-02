import React, {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import {
  getAccessToken,
  getRefreshToken,
  login as loginRequest,
  register as registerRequest,
  logout as logoutRequest,
  authFetch,
  saveTokens,
} from "./auth";

type User = {
  id: number | string;
  email: string;
  created_at: string;
};

type AuthContextType = {
  user: User | null;
  loading: boolean;
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

  const refreshUser = async () => {
    const token = await getAccessToken();

    if (!token) {
      setUser(null);
      return;
    }

    try {
      const response = await authFetch("/auth/me");

      if (!response.ok) {
        setUser(null);
        return;
      }

      const data = await response.json();
      setUser(data);
    } catch {
      setUser(null);
    }
  };

  useEffect(() => {
    const initialize = async () => {
      try {
        await refreshUser();
      } finally {
        setLoading(false);
      }
    };

    initialize();
  }, []);

  const login = async (email: string, password: string) => {
    await loginRequest(email, password);
    await refreshUser();
  };

  const register = async (email: string, password: string) => {
    const data = await registerRequest(email, password);

    await saveTokens(
      data.access_token,
      data.refresh_token
    );

    await refreshUser();
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