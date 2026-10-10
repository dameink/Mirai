
import {
  View,
  Alert,
  Text,
  StyleSheet,
  TextInput,
  Pressable,
  ScrollView,
  ImageBackground,
  KeyboardAvoidingView,
  Platform,
  Animated,
  Easing,
  DeviceEventEmitter,
  Keyboard,
} from "react-native";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import { router, useFocusEffect, useLocalSearchParams } from "expo-router";
import { BottomNavigation } from "../../components/bottom-navigation";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { requestErrorMessage, throwResponseError } from "../../auth/errors";
import { authFetch } from "../../auth/auth";
import { useAuth } from "../../auth/AuthContext";
import { savePending, readPending, clearPending } from "../../storage/outbox";
import { useSettings } from "../../../context/settings-context";

// Called only when the user sends a new message; retries reuse the same identifier.
function createRequestId() {
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}-${Math.random().toString(36).slice(2)}`;
}

type ChatPayload = { request_id: string; message: string; language: string; mode: string };

type Message = {
  id: number | string;
  text: string;
  sender: "mirai" | "user";
  timestamp?: string;
  request?: ChatPayload;
  failed?: boolean;
  error?: string;
};

type ChatResponse = {
  response?: string;
  state?: unknown;
};

/* =========================================================
   ANIMATED PRESSABLE
   ========================================================= */

function AnimatedPressable({
  children,
  onPress,
  style,
  disabled = false,
}: {
  children: React.ReactNode;
  onPress: () => void;
  style?: any;
  disabled?: boolean;
}) {
  const [scale] = useState(() => new Animated.Value(1));

  const pressIn = () => {
    if (disabled) return;

    Animated.spring(scale, {
      toValue: 0.96,
      useNativeDriver: true,
      speed: 30,
      bounciness: 4,
    }).start();
  };

  const pressOut = () => {
    Animated.spring(scale, {
      toValue: 1,
      useNativeDriver: true,
      speed: 24,
      bounciness: 6,
    }).start();
  };

  return (
    <Animated.View
      style={[
        style,
        {
          transform: [{ scale }],
        },
      ]}
    >
      <Pressable
        onPress={onPress}
        onPressIn={pressIn}
        onPressOut={pressOut}
        disabled={disabled}
      >
        {children}
      </Pressable>
    </Animated.View>
  );
}

/* =========================================================
   TYPING INDICATOR
   ========================================================= */

function TypingIndicator() {
  const [dot1] = useState(() => new Animated.Value(0.3));
  const [dot2] = useState(() => new Animated.Value(0.3));
  const [dot3] = useState(() => new Animated.Value(0.3));

  const [translate1] = useState(() => new Animated.Value(0));
  const [translate2] = useState(() => new Animated.Value(0));
  const [translate3] = useState(() => new Animated.Value(0));

  useEffect(() => {
    const animateDot = (
      opacity: Animated.Value,
      translate: Animated.Value,
      delay: number
    ) => {
      return Animated.loop(
        Animated.sequence([
          Animated.delay(delay),

          Animated.parallel([
            Animated.timing(opacity, {
              toValue: 1,
              duration: 300,
              easing: Easing.inOut(Easing.ease),
              useNativeDriver: true,
            }),

            Animated.timing(translate, {
              toValue: -3,
              duration: 300,
              easing: Easing.inOut(Easing.ease),
              useNativeDriver: true,
            }),
          ]),

          Animated.parallel([
            Animated.timing(opacity, {
              toValue: 0.3,
              duration: 300,
              easing: Easing.inOut(Easing.ease),
              useNativeDriver: true,
            }),

            Animated.timing(translate, {
              toValue: 0,
              duration: 300,
              easing: Easing.inOut(Easing.ease),
              useNativeDriver: true,
            }),
          ]),
        ])
      );
    };

    const animation1 = animateDot(dot1, translate1, 0);
    const animation2 = animateDot(dot2, translate2, 150);
    const animation3 = animateDot(dot3, translate3, 300);

    animation1.start();
    animation2.start();
    animation3.start();

    return () => {
      animation1.stop();
      animation2.stop();
      animation3.stop();
    };
  }, [
    dot1,
    dot2,
    dot3,
    translate1,
    translate2,
    translate3,
  ]);

  return (
    <View style={styles.typingBubble}>
      <View style={styles.typingDots}>
        <Animated.View
          style={[
            styles.typingDot,
            {
              opacity: dot1,
              transform: [{ translateY: translate1 }],
            },
          ]}
        />

        <Animated.View
          style={[
            styles.typingDot,
            {
              opacity: dot2,
              transform: [{ translateY: translate2 }],
            },
          ]}
        />

        <Animated.View
          style={[
            styles.typingDot,
            {
              opacity: dot3,
              transform: [{ translateY: translate3 }],
            },
          ]}
        />
      </View>
    </View>
  );
}

/* =========================================================
   MESSAGE
   ========================================================= */

function AnimatedMessage({
  message, onRetry, sending,
}: {
  message: Message;
  onRetry: () => void;
  sending: boolean;
}) {
  const [opacity] = useState(() => new Animated.Value(0));
  const [translateY] = useState(() => new Animated.Value(8));
  const [scale] = useState(() => new Animated.Value(0.98));

  useEffect(() => {
    Animated.parallel([
      Animated.timing(opacity, {
        toValue: 1,
        duration: 220,
        easing: Easing.out(Easing.ease),
        useNativeDriver: true,
      }),

      Animated.timing(translateY, {
        toValue: 0,
        duration: 240,
        easing: Easing.out(Easing.ease),
        useNativeDriver: true,
      }),

      Animated.spring(scale, {
        toValue: 1,
        useNativeDriver: true,
        speed: 24,
        bounciness: 3,
      }),
    ]).start();
  }, [opacity, scale, translateY]);

  return (
    <Animated.View
      style={{
        opacity,
        transform: [
          { translateY },
          { scale },
        ],
      }}
    >
      <View
        style={[
          styles.messageRow,
          message.sender === "user" && styles.userRow,
        ]}
      >
        <View
          style={
            message.sender === "user"
              ? styles.userBubble
              : styles.miraiBubble
          }
        >
          <Text
            style={
              message.sender === "user"
                ? styles.userText
                : styles.miraiText
            }
          >
            {message.text}
          </Text>

          {message.failed && (
            <Pressable onPress={onRetry} disabled={sending}>
              <Text style={styles.timestamp}>{message.error || "Delivery unconfirmed."} Tap to retry.</Text>
            </Pressable>
          )}

          {message.timestamp && (
            <Text style={styles.timestamp}>
              {new Date(message.timestamp).toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </Text>
          )}
        </View>
      </View>
    </Animated.View>
  );
}

/* =========================================================
   MAIN SCREEN
   ========================================================= */

export default function ChatScreen() {
  const { user } = useAuth();
  const insets = useSafeAreaInsets();
  const [keyboardVisible, setKeyboardVisible] = useState(false);
  const [historyAttempt, setHistoryAttempt] = useState(0);
  const uid = user ? String(user.id) : null;
  const pendingRef = useRef(false);
  const conversationVersion = useRef(0);
  const [historyReady, setHistoryReady] = useState(false);
  const { practice } = useLocalSearchParams<{ practice?: string }>();
  const [message, setMessage] = useState("");
  useFocusEffect(useCallback(() => {
    if (practice) {
      setMessage(practice);
      router.setParams({ practice: undefined });
    }
  }, [practice]));
  const [messages, setMessages] = useState<Message[]>([]);
  const [isSending, setIsSending] = useState(false);
  const sendingRef = useRef(false);
  const [hasOlder, setHasOlder] = useState(false);
  useEffect(() => {
    const listener = DeviceEventEmitter.addListener("conversationCleared", () => {
      conversationVersion.current += 1;
      pendingRef.current = false;
      setMessages([]);
      setHasOlder(false);
      setHistoryReady(true);
      setMessage("");
    });
    return () => listener.remove();
  }, []);
  const [menuVisible, setMenuVisible] = useState(false);
  const [loadingOlder, setLoadingOlder] = useState(false);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const prepending = useRef(false);

  const scrollViewRef = useRef<ScrollView>(null);

  const [menuOpacity] = useState(() => new Animated.Value(0));
  const [menuScale] = useState(() => new Animated.Value(0.94));
  const [backdropOpacity] = useState(() => new Animated.Value(0));
  const [thinkingOpacity] = useState(() => new Animated.Value(0.55));
  const [sendScale] = useState(() => new Animated.Value(1));

  const {
    language,
    mode,
  } = useSettings();

  /* =======================================================
     THINKING ANIMATION
     ======================================================= */

  useEffect(() => {
    if (!isSending) {
      thinkingOpacity.stopAnimation();

      Animated.timing(thinkingOpacity, {
        toValue: 0.55,
        duration: 150,
        useNativeDriver: true,
      }).start();

      return;
    }

    const animation = Animated.loop(
      Animated.sequence([
        Animated.timing(thinkingOpacity, {
          toValue: 1,
          duration: 700,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),

        Animated.timing(thinkingOpacity, {
          toValue: 0.55,
          duration: 700,
          easing: Easing.inOut(Easing.ease),
          useNativeDriver: true,
        }),
      ])
    );

    animation.start();

    return () => {
      animation.stop();
    };
  }, [isSending, thinkingOpacity]);

  /* =======================================================
     MENU ANIMATION
     ======================================================= */

  useEffect(() => {
    if (!menuVisible) {
      Animated.parallel([
        Animated.timing(menuOpacity, {
          toValue: 0,
          duration: 150,
          useNativeDriver: true,
        }),

        Animated.timing(backdropOpacity, {
          toValue: 0,
          duration: 150,
          useNativeDriver: true,
        }),

        Animated.timing(menuScale, {
          toValue: 0.94,
          duration: 150,
          useNativeDriver: true,
        }),
      ]).start();

      return;
    }

    Animated.parallel([
      Animated.timing(menuOpacity, {
        toValue: 1,
        duration: 180,
        easing: Easing.out(Easing.ease),
        useNativeDriver: true,
      }),

      Animated.timing(backdropOpacity, {
        toValue: 1,
        duration: 180,
        easing: Easing.out(Easing.ease),
        useNativeDriver: true,
      }),

      Animated.spring(menuScale, {
        toValue: 1,
        useNativeDriver: true,
        speed: 20,
        bounciness: 5,
      }),
    ]).start();
  }, [
    menuVisible,
    menuOpacity,
    menuScale,
    backdropOpacity,
  ]);

  /* =======================================================
     LOAD CONVERSATION
     ======================================================= */

  useEffect(() => {
    const version = ++conversationVersion.current;
    // Reset account-scoped UI before restoring this account’s asynchronous history.
    setMessages([]);
    setHistoryReady(false);
    setHistoryError(null);
    setHasOlder(false);
    pendingRef.current = false;
    if (!uid) return;
    let active = true;
    const isCurrent = () => active && version === conversationVersion.current;
    const loadConversation = async () => {
      let storageReady = false;
      try {
        const pending = await readPending(uid);
        if (!isCurrent()) return;
        storageReady = true;
        if (pending && isCurrent()) {
          pendingRef.current = true;
          setMessages([{ id: pending.request_id, text: pending.message, sender: "user", request: pending, failed: true }]);
        }
        let unresolved = pending;
        if (pending) {
          const status = await authFetch(`/chat/requests/${encodeURIComponent(pending.request_id)}`);
          if (!status.ok) await throwResponseError(status);
          const result = await status.json();
          if (!isCurrent()) return;
          if (result.status === "completed" || result.status === "cleared") {
            await clearPending(uid);
            unresolved = null;
            if (isCurrent()) {
              pendingRef.current = false;
              setMessages([]);
            }
          }
        }
        const response = await authFetch("/conversation");
        if (!response.ok) await throwResponseError(response);
        const data: { id: string; role: string; content: string; timestamp?: string }[] = await response.json();
        const loaded: Message[] = data.map(item => ({ id: item.id, text: item.content, sender: item.role === "user" ? "user" : "mirai", timestamp: item.timestamp }));
        if (unresolved) loaded.push({ id: unresolved.request_id, text: unresolved.message, sender: "user", request: unresolved, failed: true });
        if (isCurrent()) {
          pendingRef.current = Boolean(unresolved);
          setMessages(loaded);
          setHasOlder(data.length === 100);
        }
      } catch (error) {
        if (isCurrent()) setHistoryError(requestErrorMessage(error));
      } finally {
        if (isCurrent()) setHistoryReady(storageReady);
      }
    };
    void loadConversation();
    return () => {
      active = false;
      if (conversationVersion.current === version) conversationVersion.current += 1;
    };
  }, [uid, historyAttempt]);

  /* =======================================================
     AUTO SCROLL
     ======================================================= */

  useEffect(() => {
    if (messages.length === 0) return;
    if (prepending.current) { prepending.current = false; return; }

    setTimeout(() => {
      scrollViewRef.current?.scrollToEnd({
        animated: true,
      });
    }, 80);
  }, [messages]);

  /* =======================================================
     KEYBOARD AUTO SCROLL
     ======================================================= */

  useEffect(() => {
    const eventName =
      Platform.OS === "ios"
        ? "keyboardWillShow"
        : "keyboardDidShow";

    const keyboardListener = Keyboard.addListener(
      eventName,
      () => {
        setKeyboardVisible(true);
        setTimeout(() => {
          scrollViewRef.current?.scrollToEnd({
            animated: true,
          });
        }, 100);
      }
    );

    const hideListener = Keyboard.addListener(Platform.OS === "ios" ? "keyboardWillHide" : "keyboardDidHide", () => setKeyboardVisible(false));
    return () => {
      hideListener.remove();
      keyboardListener.remove();
    };
  }, []);

  /* =======================================================
     SEND MESSAGE
     ======================================================= */

  const loadOlder = async () => {
    if (loadingOlder || !messages.length) return;
    const version = conversationVersion.current;
    setLoadingOlder(true);
    setHistoryError(null);
    try {
      const response = await authFetch(`/conversation?before_id=${encodeURIComponent(messages[0].id)}&limit=100`);
      if (!response.ok) throw new Error("Could not load older messages. Please retry.");
      const data: { id: string; content: string; role: string; timestamp: string }[] = await response.json();
      const older: Message[] = data.map((item) => ({ id: item.id, text: item.content, sender: item.role === "user" ? "user" : "mirai", timestamp: item.timestamp }));
      if (version !== conversationVersion.current) return;
      prepending.current = true;
      setMessages((current) => [...older, ...current]);
      setHasOlder(data.length === 100);
    } catch (error) {
      if (version === conversationVersion.current) setHistoryError(error instanceof Error ? error.message : "Could not load history");
    } finally {
      setLoadingOlder(false);
    }
  };

  const sendRequest = async (outgoing: Message) => {
    if (sendingRef.current || !outgoing.request || !uid || !historyReady) return;
    const version = conversationVersion.current;
    sendingRef.current = true;
    setIsSending(true);
    setMessages((current) => current.map((item) => item.id === outgoing.id ? { ...item, failed: false } : item));
    try {
      const response = await authFetch("/chat", {
        method: "POST",
        body: JSON.stringify(outgoing.request),
      });
      if (!response.ok) await throwResponseError(response);
      const data: ChatResponse = await response.json();
      if (!data.response) throw new Error("Mirai returned an empty response");
      if (version !== conversationVersion.current) return;
      await clearPending(uid);
      if (version !== conversationVersion.current) return;
      pendingRef.current = false;
      DeviceEventEmitter.emit("learningUpdated");
      DeviceEventEmitter.emit("miraiUpdated");
      setMessages((current) => [...current, {
        id: `${outgoing.id}:response`, text: data.response!, sender: "mirai",
        timestamp: new Date().toISOString(),
      }]);
    } catch (error) {
      if (version !== conversationVersion.current) return;
      setMessages((current) => current.map((item) => item.id === outgoing.id ? { ...item, failed: true, error: requestErrorMessage(error) } : item));
    } finally {
      sendingRef.current = false;
      setIsSending(false);
    }
  };

  const sendMessage = async () => {
    const trimmedMessage = message.trim();
    if (!trimmedMessage || sendingRef.current || !uid || !historyReady) return;
    if (pendingRef.current) {
      Alert.alert("Message awaiting delivery", "Retry the pending message, or clear the conversation before sending another.");
      return;
    }
    if (trimmedMessage.length > 4000) { Alert.alert("Message too long", "Please use at most 4000 characters."); return; }
    // This is a deduplication identifier, not an authentication secret.
    const requestId = createRequestId();
    const outgoing: Message = {
      id: requestId, text: trimmedMessage, sender: "user", timestamp: new Date().toISOString(),
      request: { request_id: requestId, message: trimmedMessage, language, mode },
    };
    const version = conversationVersion.current;
    sendingRef.current = true;
    try {
      await savePending(uid, outgoing.request!);
      if (version !== conversationVersion.current) return;
      pendingRef.current = true;
    } catch {
      Alert.alert("Message not saved", "Could not securely save the message. Please try again.");
      return;
    } finally { sendingRef.current = false; }
    setMessages((current) => [...current, outgoing]);
    setMessage("");
    await sendRequest(outgoing);
  };

  /* =======================================================
     NEW CONVERSATION
     ======================================================= */

  const newConversation = async () => {
    if (sendingRef.current) return;

    try {
      const response = await authFetch(
        "/conversation",
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        throw new Error(
          `Failed to start new conversation: ${response.status}`
        );
      }

      conversationVersion.current += 1;
      if (uid) await clearPending(uid);
      pendingRef.current = false;
      setMessages([]);
      setHasOlder(false);
      setMessage("");
      setMenuVisible(false);
    } catch (error) {
      console.error(
        "Failed to start new conversation:",
        error
      );
    }
  };

  /* =======================================================
     CLEAR CONVERSATION
     ======================================================= */

  const clearConversation = async () => {
    if (sendingRef.current) return;

    try {
      const response = await authFetch(
        "/conversation",
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        throw new Error(
          `Failed to clear conversation: ${response.status}`
        );
      }

      conversationVersion.current += 1;
      if (uid) await clearPending(uid);
      pendingRef.current = false;
      setMessages([]);
      setHasOlder(false);
      setMessage("");
      setMenuVisible(false);
    } catch (error) {
      console.error(
        "Failed to clear conversation:",
        error
      );
    }
  };

  /* =======================================================
     RESET MIRAI
     ======================================================= */

  const resetMirai = async () => {
    if (sendingRef.current) return;

    try {
      const response = await authFetch(
        "/reset",
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        throw new Error(
          `Failed to reset Mirai: ${response.status}`
        );
      }

      conversationVersion.current += 1;
      if (uid) await clearPending(uid);
      pendingRef.current = false;
      setMessages([]);
      setHasOlder(false);
      setMessage("");
      setMenuVisible(false);
    } catch (error) {
      console.error(
        "Failed to reset Mirai:",
        error
      );
    }
  };

  /* =======================================================
     QUICK REPLY
     ======================================================= */

  const sendQuickReply = (text: string) => {
    if (sendingRef.current) return;

    setMessage(text);
  };

  /* =======================================================
     CLOSE MENU
     ======================================================= */

  const closeMenu = () => {
    setMenuVisible(false);
  };

  /* =======================================================
     UI
     ======================================================= */

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      keyboardVerticalOffset={0}
    >
      {/* HEADER */}

      <View style={[styles.header, { height: 56 + insets.top, paddingTop: insets.top }]}>
        <View style={styles.miraiInfo}>
          <Animated.View style={styles.avatar}>
            <Text style={styles.avatarText}>
              🌸
            </Text>
          </Animated.View>

          <View>
            <Text style={styles.name}>
              Mirai
            </Text>

            <View style={styles.statusRow}>
              <Animated.View
                style={[
                  styles.statusDot,
                  isSending &&
                    styles.statusDotThinking,
                  {
                    opacity: isSending
                      ? thinkingOpacity
                      : 1,
                  },
                ]}
              />

              <Animated.Text
                style={[
                  styles.status,
                  {
                    opacity: isSending
                      ? thinkingOpacity
                      : 1,
                  },
                ]}
              >
                {isSending
                  ? "thinking..."
                  : "online"}
              </Animated.Text>
            </View>
          </View>
        </View>

        <AnimatedPressable
          onPress={() =>
            setMenuVisible(true)
          }
        >
          <Text style={styles.menu}>
            •••
          </Text>
        </AnimatedPressable>
      </View>

      {/* MENU */}

      {menuVisible && (
        <View style={styles.menuOverlay}>
          <Animated.View
            pointerEvents="auto"
            style={[
              styles.menuBackdrop,
              {
                opacity: backdropOpacity,
              },
            ]}
          >
            <Pressable
              style={styles.fullScreenPressable}
              onPress={closeMenu}
            />
          </Animated.View>

          <Animated.View
            style={[
              styles.menuModal,
              {
                opacity: menuOpacity,
                transform: [
                  {
                    scale: menuScale,
                  },
                ],
              },
            ]}
          >
            <Text style={styles.menuTitle}>
              Mirai 🌸
            </Text>

            <Text style={styles.menuSubtitle}>
              Chat options
            </Text>

            <AnimatedPressable
              style={[
                styles.menuActionWrapper,
                isSending &&
                  styles.menuActionDisabled,
              ]}
              onPress={newConversation}
              disabled={isSending}
            >
              <View style={styles.menuAction}>
                <Text
                  style={
                    styles.menuActionIcon
                  }
                >
                  ＋
                </Text>

                <Text
                  style={
                    styles.menuActionText
                  }
                >
                  New conversation
                </Text>
              </View>
            </AnimatedPressable>

            <AnimatedPressable
              style={[
                styles.menuActionWrapper,
                isSending &&
                  styles.menuActionDisabled,
              ]}
              onPress={clearConversation}
              disabled={isSending}
            >
              <View style={styles.menuAction}>
                <Text
                  style={[
                    styles.menuActionText,
                    styles.dangerText,
                  ]}
                >
                  Clear history
                </Text>
              </View>
            </AnimatedPressable>

            <AnimatedPressable
              style={[
                styles.menuActionWrapper,
                isSending &&
                  styles.menuActionDisabled,
              ]}
              onPress={resetMirai}
              disabled={isSending}
            >
              <View style={styles.menuAction}>
                <Text
                  style={[
                    styles.menuActionText,
                    styles.dangerText,
                  ]}
                >
                  Reset Mirai
                </Text>
              </View>
            </AnimatedPressable>

            <AnimatedPressable
              style={styles.cancelButtonWrapper}
              onPress={closeMenu}
            >
              <View style={styles.cancelButton}>
                <Text style={styles.cancelText}>
                  Cancel
                </Text>
              </View>
            </AnimatedPressable>
          </Animated.View>
        </View>
      )}

      {/* CHAT */}

      <ImageBackground
        source={require(
          "../../../assets/Wallpaper.png"
        )}
        style={styles.chat}
        imageStyle={styles.wallpaper}
      >
        <ScrollView
          ref={scrollViewRef}
          contentContainerStyle={
            styles.chatContent
          }
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
          keyboardDismissMode={
            Platform.OS === "android"
              ? "on-drag"
              : "interactive"
          }
        >
          {hasOlder && (
            <Pressable onPress={loadOlder} disabled={loadingOlder}>
              <Text style={styles.miraiText}>{loadingOlder ? "Loading…" : "Load older messages"}</Text>
            </Pressable>
          )}
          {historyError && <Pressable onPress={() => setHistoryAttempt(value => value + 1)}><Text style={styles.miraiText}>{historyError} Tap to reload history.</Text></Pressable>}
          {/* EMPTY STATE */}

          {messages.length === 0 && (
            <>
              <Animated.View
                style={styles.messageRow}
              >
                <View
                  style={
                    styles.miraiBubble
                  }
                >
                  <Text
                    style={
                      styles.miraiText
                    }
                  >
                    Hey! I&apos;m Mirai 🌸
                    {"\n\n"}
                    I&apos;m really happy you&apos;re here.
                    {"\n\n"}
                    Want to practice English
                    together?
                  </Text>
                </View>
              </Animated.View>

              <View
                style={styles.quickReplies}
              >
                <AnimatedPressable
                  onPress={() =>
                    sendQuickReply(
                      "Let's practice English!"
                    )
                  }
                >
                  <View
                    style={
                      styles.quickReply
                    }
                  >
                    <Text
                      style={
                        styles.quickReplyText
                      }
                    >
                      Practice English
                    </Text>
                  </View>
                </AnimatedPressable>

                <AnimatedPressable
                  onPress={() =>
                    sendQuickReply(
                      "Let's just talk for a while."
                    )
                  }
                >
                  <View
                    style={
                      styles.quickReply
                    }
                  >
                    <Text
                      style={
                        styles.quickReplyText
                      }
                    >
                      Just talk
                    </Text>
                  </View>
                </AnimatedPressable>

                <AnimatedPressable
                  onPress={() =>
                    sendQuickReply(
                      "Can you help me study?"
                    )
                  }
                >
                  <View
                    style={
                      styles.quickReply
                    }
                  >
                    <Text
                      style={
                        styles.quickReplyText
                      }
                    >
                      Help me study
                    </Text>
                  </View>
                </AnimatedPressable>
              </View>
            </>
          )}

          {/* MESSAGES */}

          {messages.map((item) => (
            <AnimatedMessage
              key={item.id}
              message={item}
              onRetry={() => { void sendRequest(item); }}
              sending={isSending}
            />
          ))}

          {/* TYPING */}

          {isSending && (
            <View
              style={styles.messageRow}
            >
              <TypingIndicator />
            </View>
          )}
        </ScrollView>
      </ImageBackground>

      {/* INPUT */}

      <View style={[styles.inputArea, keyboardVisible && { paddingBottom: 8 }]}>
        <View
          style={
            styles.inputContainer
          }
        >
          <TextInput
            value={message}
            onChangeText={setMessage}
            placeholder="Message..."
            placeholderTextColor="#999"
            style={styles.input}
            returnKeyType="send"
            onSubmitEditing={sendMessage}
            multiline
            maxLength={4000}
            submitBehavior="submit"
            accessibilityLabel="Message Mirai"
            editable={!isSending}
          />

          <Animated.View
            style={{
              transform: [
                {
                  scale: sendScale,
                },
              ],
            }}
          >
            <Pressable
              style={[
                styles.sendButton,
                (
                  !message.trim() ||
                  isSending
                ) &&
                  styles.sendButtonDisabled,
              ]}
              onPress={sendMessage}
              disabled={
                !message.trim() ||
                isSending
              }
              onPressIn={() => {
                if (
                  !message.trim() ||
                  isSending
                ) {
                  return;
                }

                Animated.spring(
                  sendScale,
                  {
                    toValue: 0.9,
                    useNativeDriver: true,
                    speed: 30,
                    bounciness: 3,
                  }
                ).start();
              }}
              onPressOut={() => {
                Animated.spring(
                  sendScale,
                  {
                    toValue: 1,
                    useNativeDriver: true,
                    speed: 25,
                    bounciness: 5,
                  }
                ).start();
              }}
            >
              <Text
                style={
                  styles.sendText
                }
              >
                ➤
              </Text>
            </Pressable>
          </Animated.View>
        </View>
      </View>

      {/* BOTTOM NAVIGATION */}

      {!keyboardVisible && <BottomNavigation activeRoute="chat" />}
    </KeyboardAvoidingView>
  );
}

/* =========================================================
   STYLES
   ========================================================= */

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#FFFDFE",
  },

  header: {
    height: 92,
    paddingHorizontal: 20,
    paddingTop: 42,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    borderBottomWidth: 1,
    borderBottomColor: "#F1ECEF",
    backgroundColor: "#FFFFFF",
  },

  miraiInfo: {
    flexDirection: "row",
    alignItems: "center",
  },

  avatar: {
    width: 42,
    height: 42,
    borderRadius: 21,
    backgroundColor: "#FFF0F6",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 11,
  },

  avatarText: {
    fontSize: 21,
  },

  name: {
    fontSize: 17,
    fontWeight: "700",
    color: "#222222",
  },

  statusRow: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: 2,
  },

  status: {
    fontSize: 12,
    color: "#8E8E8E",
    marginTop: 2,
  },

  statusDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: "#72C98A",
    marginRight: 5,
  },

  statusDotThinking: {
    backgroundColor: "#D9A6B8",
  },

  menu: {
    fontSize: 22,
    color: "#777777",
    letterSpacing: 2,
  },

  chat: {
    flex: 1,
  },

  wallpaper: {
    opacity: 0.25,
  },

  chatContent: {
    paddingHorizontal: 16,
    paddingVertical: 24,
    paddingBottom: 30,
  },

  messageRow: {
    flexDirection: "row",
    marginBottom: 12,
  },

  userRow: {
    justifyContent: "flex-end",
  },

  miraiBubble: {
    maxWidth: "78%",
    paddingHorizontal: 16,
    paddingVertical: 11,
    borderRadius: 18,
    borderBottomLeftRadius: 5,
    backgroundColor: "#F3F1F2",
  },

  userBubble: {
    maxWidth: "78%",
    paddingHorizontal: 16,
    paddingVertical: 11,
    borderRadius: 18,
    borderBottomRightRadius: 5,
    backgroundColor: "#FFE2EF",
  },

  miraiText: {
    fontSize: 16,
    color: "#252525",
    lineHeight: 22,
  },

  userText: {
    fontSize: 16,
    color: "#252525",
    lineHeight: 22,
  },

  timestamp: {
    fontSize: 10,
    color: "#999999",
    alignSelf: "flex-end",
    marginTop: 4,
  },

  typingBubble: {
    paddingHorizontal: 16,
    paddingVertical: 11,
    borderRadius: 18,
    borderBottomLeftRadius: 5,
    backgroundColor: "#F3F1F2",
  },

  typingDots: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
  },

  typingDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: "#746B70",
  },

  quickReplies: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginTop: 0,
    marginBottom: 8,
  },

  quickReply: {
    paddingHorizontal: 14,
    paddingVertical: 9,
    borderRadius: 18,
    backgroundColor: "#FFF5F8",
    borderWidth: 1,
    borderColor: "#F3DCE5",
  },

  quickReplyText: {
    fontSize: 13,
    fontWeight: "600",
    color: "#D96B88",
  },

  inputArea: {
    paddingHorizontal: 14,
    paddingVertical: 9,
    backgroundColor: "#FFFFFF",
    borderTopWidth: 1,
    borderTopColor: "#F1ECEF",
  },

  inputContainer: {
    minHeight: 46,
    borderRadius: 23,
    backgroundColor: "#F5F3F4",
    flexDirection: "row",
    alignItems: "center",
    paddingLeft: 17,
    paddingRight: 5,
  },

  input: {
    minHeight: 44,
    maxHeight: 120,
    paddingVertical: 10,
    textAlignVertical: "center",
    flex: 1,
    fontSize: 16,
    color: "#222222",
  },

  sendButton: {
    width: 37,
    height: 37,
    borderRadius: 19,
    backgroundColor: "#FF8FBA",
    justifyContent: "center",
    alignItems: "center",
  },

  sendButtonDisabled: {
    opacity: 0.45,
  },

  sendText: {
    color: "#FFFFFF",
    fontSize: 18,
    marginLeft: 2,
  },

  menuOverlay: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    zIndex: 100,
    justifyContent: "center",
    alignItems: "center",
  },

  menuBackdrop: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor:
      "rgba(30, 20, 25, 0.28)",
  },

  fullScreenPressable: {
    flex: 1,
  },

  menuModal: {
    width: "82%",
    maxWidth: 340,
    backgroundColor: "#FFFFFF",
    borderRadius: 24,
    paddingHorizontal: 20,
    paddingTop: 24,
    paddingBottom: 14,

    shadowColor: "#000",

    shadowOffset: {
      width: 0,
      height: 8,
    },

    shadowOpacity: 0.18,

    shadowRadius: 20,

    elevation: 12,
  },

  menuTitle: {
    fontSize: 21,
    fontWeight: "700",
    color: "#252225",
    textAlign: "center",
  },

  menuSubtitle: {
    fontSize: 14,
    color: "#8E858A",
    textAlign: "center",
    marginTop: 4,
    marginBottom: 20,
  },

  menuActionWrapper: {
    marginBottom: 10,
  },

  menuAction: {
    height: 56,
    borderRadius: 16,
    backgroundColor: "#FFF5F8",
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 16,
  },

  menuActionDisabled: {
    opacity: 0.45,
  },

  menuActionIcon: {
    width: 32,
    fontSize: 22,
    color: "#FF8FBA",
    textAlign: "center",
    marginRight: 10,
  },

  menuActionText: {
    fontSize: 16,
    fontWeight: "600",
    color: "#302B2E",
  },

  dangerText: {
    color: "#D96B88",
  },

  cancelButtonWrapper: {
    marginTop: 2,
  },

  cancelButton: {
    height: 50,
    justifyContent: "center",
    alignItems: "center",
  },

  cancelText: {
    fontSize: 15,
    fontWeight: "600",
    color: "#8E858A",
  },
});