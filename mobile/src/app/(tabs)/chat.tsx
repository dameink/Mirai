import {
  View,
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
} from "react-native";

import {
  useEffect,
  useRef,
  useState,
} from "react";

import { BottomNavigation } from "../../components/bottom-navigation";
import { authFetch } from "../../auth/auth";
import { useSettings } from "../../../context/settings-context";

type Message = {
  id: number;
  text: string;
  sender: "mirai" | "user";
  timestamp?: string;
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
  const scale = useRef(
    new Animated.Value(1)
  ).current;

  const pressIn = () => {
    if (disabled) {
      return;
    }

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
          transform: [
            {
              scale,
            },
          ],
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
  const dot1 = useRef(
    new Animated.Value(0.3)
  ).current;

  const dot2 = useRef(
    new Animated.Value(0.3)
  ).current;

  const dot3 = useRef(
    new Animated.Value(0.3)
  ).current;

  const translate1 = useRef(
    new Animated.Value(0)
  ).current;

  const translate2 = useRef(
    new Animated.Value(0)
  ).current;

  const translate3 = useRef(
    new Animated.Value(0)
  ).current;

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

    const animation1 = animateDot(
      dot1,
      translate1,
      0
    );

    const animation2 = animateDot(
      dot2,
      translate2,
      150
    );

    const animation3 = animateDot(
      dot3,
      translate3,
      300
    );

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
              transform: [
                {
                  translateY: translate1,
                },
              ],
            },
          ]}
        />

        <Animated.View
          style={[
            styles.typingDot,
            {
              opacity: dot2,
              transform: [
                {
                  translateY: translate2,
                },
              ],
            },
          ]}
        />

        <Animated.View
          style={[
            styles.typingDot,
            {
              opacity: dot3,
              transform: [
                {
                  translateY: translate3,
                },
              ],
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
  message,
}: {
  message: Message;
}) {
  const opacity = useRef(
    new Animated.Value(0)
  ).current;

  const translateY = useRef(
    new Animated.Value(8)
  ).current;

  const scale = useRef(
    new Animated.Value(0.98)
  ).current;

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
  }, []);

  return (
    <Animated.View
      style={{
        opacity,
        transform: [
          {
            translateY,
          },
          {
            scale,
          },
        ],
      }}
    >
      <View
        style={[
          styles.messageRow,
          message.sender === "user" &&
            styles.userRow,
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

          {message.timestamp && (
            <Text style={styles.timestamp}>
              {new Date(
                message.timestamp
              ).toLocaleTimeString([], {
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
  const [message, setMessage] =
    useState("");

  const [messages, setMessages] =
    useState<Message[]>([]);

  const [isSending, setIsSending] =
    useState(false);

  const [menuVisible, setMenuVisible] =
    useState(false);

  const scrollViewRef =
    useRef<ScrollView>(null);

  const menuOpacity = useRef(
    new Animated.Value(0)
  ).current;

  const menuScale = useRef(
    new Animated.Value(0.94)
  ).current;

  const backdropOpacity = useRef(
    new Animated.Value(0)
  ).current;

  const thinkingOpacity = useRef(
    new Animated.Value(0.55)
  ).current;

  const sendScale = useRef(
    new Animated.Value(1)
  ).current;

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

    const animation =
      Animated.loop(
        Animated.sequence([
          Animated.timing(
            thinkingOpacity,
            {
              toValue: 1,
              duration: 700,
              easing: Easing.inOut(
                Easing.ease
              ),
              useNativeDriver: true,
            }
          ),

          Animated.timing(
            thinkingOpacity,
            {
              toValue: 0.55,
              duration: 700,
              easing: Easing.inOut(
                Easing.ease
              ),
              useNativeDriver: true,
            }
          ),
        ])
      );

    animation.start();

    return () => {
      animation.stop();
    };
  }, [
    isSending,
    thinkingOpacity,
  ]);

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

        Animated.timing(
          backdropOpacity,
          {
            toValue: 0,
            duration: 150,
            useNativeDriver: true,
          }
        ),

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
        easing: Easing.out(
          Easing.ease
        ),
        useNativeDriver: true,
      }),

      Animated.timing(
        backdropOpacity,
        {
          toValue: 1,
          duration: 180,
          easing: Easing.out(
            Easing.ease
          ),
          useNativeDriver: true,
        }
      ),

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
    const loadConversation =
      async () => {
        try {
          const response =
            await authFetch(
              "/conversation"
            );

          if (!response.ok) {
            throw new Error(
              "Failed to load conversation"
            );
          }

          const data: {
            role:
              | "user"
              | "assistant";

            content: string;

            timestamp?: string;
          }[] =
            await response.json();

          const loadedMessages:
            Message[] =
            data.map(
              (
                item,
                index
              ) => ({
                id: index + 1,

                text:
                  item.content,

                sender:
                  item.role ===
                  "user"
                    ? "user"
                    : "mirai",

                timestamp:
                  item.timestamp,
              })
            );

          setMessages(
            loadedMessages
          );

          setTimeout(() => {
            scrollViewRef.current?.scrollToEnd(
              {
                animated: false,
              }
            );
          }, 100);
        } catch (error) {
          console.error(
            "Failed to load conversation:",
            error
          );
        }
      };

    loadConversation();
  }, []);

  /* =======================================================
     AUTO SCROLL
     ======================================================= */

  useEffect(() => {
    if (messages.length === 0) {
      return;
    }

    setTimeout(() => {
      scrollViewRef.current?.scrollToEnd({
        animated: true,
      });
    }, 80);
  }, [messages]);

  /* =======================================================
     SEND MESSAGE
     ======================================================= */

  const sendMessage =
    async () => {
      const trimmedMessage =
        message.trim();

      if (
        !trimmedMessage ||
        isSending
      ) {
        return;
      }

      Animated.sequence([
        Animated.spring(sendScale, {
          toValue: 0.88,
          useNativeDriver: true,
          speed: 35,
          bounciness: 2,
        }),

        Animated.spring(sendScale, {
          toValue: 1,
          useNativeDriver: true,
          speed: 25,
          bounciness: 5,
        }),
      ]).start();

      const newMessage:
        Message = {
        id: Date.now(),

        text:
          trimmedMessage,

        sender: "user",

        timestamp:
          new Date().toISOString(),
      };

      setMessages(
        (currentMessages) => [
          ...currentMessages,
          newMessage,
        ]
      );

      setMessage("");

      setIsSending(true);

      try {
        const response =
          await authFetch(
            "/chat",
            {
              method: "POST",

              headers: {
                "Content-Type":
                  "application/json",
              },

              body:
                JSON.stringify({
                  message:
                    trimmedMessage,

                  language:
                    language,

                  mode:
                    mode,
                }),
            }
          );

        if (!response.ok) {
          throw new Error(
            `Mirai server returned ${response.status}`
          );
        }

        const data:
          ChatResponse =
          await response.json();

        if (!data.response) {
          throw new Error(
            "Mirai returned an empty response"
          );
        }

        const miraiMessage:
          Message = {
          id: Date.now() + 1,

          text:
            data.response,

          sender: "mirai",

          timestamp:
            new Date().toISOString(),
        };

        setMessages(
          (currentMessages) => [
            ...currentMessages,
            miraiMessage,
          ]
        );
      } catch (error) {
        console.error(
          "Failed to send message:",
          error
        );

        setMessages(
          (currentMessages) => [
            ...currentMessages,

            {
              id:
                Date.now() + 1,

              text:
                "I can’t connect right now. Please try again.",

              sender:
                "mirai",
            },
          ]
        );
      } finally {
        setIsSending(false);

        setTimeout(() => {
          scrollViewRef.current?.scrollToEnd(
            {
              animated: true,
            }
          );
        }, 100);
      }
    };

  /* =======================================================
     NEW CONVERSATION
     ======================================================= */

  const newConversation =
    async () => {
      if (isSending) {
        return;
      }

      try {
        const response =
          await authFetch(
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

        setMessages([]);

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

  const clearConversation =
    async () => {
      if (isSending) {
        return;
      }

      try {
        const response =
          await authFetch(
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

        setMessages([]);

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

  const resetMirai =
    async () => {
      if (isSending) {
        return;
      }

      try {
        const response =
          await authFetch(
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

        setMessages([]);

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

  const sendQuickReply =
    (text: string) => {
      if (isSending) {
        return;
      }

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
      behavior={
        Platform.OS === "ios"
          ? "height"
          : undefined
      }
      keyboardVerticalOffset={0}
    >
      {/* =================================================
          HEADER
          ================================================= */}

      <View style={styles.header}>
        <View style={styles.miraiInfo}>
          <Animated.View
            style={styles.avatar}
          >
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
                    opacity:
                      isSending
                        ? thinkingOpacity
                        : 1,
                  },
                ]}
              />

              <Animated.Text
                style={[
                  styles.status,
                  {
                    opacity:
                      isSending
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

      {/* =================================================
          MENU
          ================================================= */}

      {menuVisible && (
        <View style={styles.menuOverlay}>
          <Animated.View
            pointerEvents="auto"
            style={[
              styles.menuBackdrop,
              {
                opacity:
                  backdropOpacity,
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
                opacity:
                  menuOpacity,

                transform: [
                  {
                    scale:
                      menuScale,
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
              <View
                style={styles.menuAction}
              >
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
              onPress={
                clearConversation
              }
              disabled={isSending}
            >
              <View
                style={styles.menuAction}
              >
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
              <View
                style={styles.menuAction}
              >
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
              <View
                style={styles.cancelButton}
              >
                <Text
                  style={styles.cancelText}
                >
                  Cancel
                </Text>
              </View>
            </AnimatedPressable>
          </Animated.View>
        </View>
      )}

      {/* =================================================
          CHAT
          ================================================= */}

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
          showsVerticalScrollIndicator={
            false
          }
          keyboardShouldPersistTaps="handled"
        >
          {/* =================================================
              EMPTY STATE
              ================================================= */}

          {messages.length === 0 && (
            <>
              <Animated.View
                style={
                  styles.messageRow
                }
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
                    Hey! I'm Mirai 🌸
                    {"\n\n"}
                    I'm really happy you're here.
                    {"\n\n"}
                    Want to practice English
                    together?
                  </Text>
                </View>
              </Animated.View>

              <View
                style={
                  styles.quickReplies
                }
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

          {/* =================================================
              MESSAGES
              ================================================= */}

          {messages.map(
            (item) => (
              <AnimatedMessage
                key={item.id}
                message={item}
              />
            )
          )}

          {/* =================================================
              TYPING
              ================================================= */}

          {isSending && (
            <View
              style={styles.messageRow}
            >
              <TypingIndicator />
            </View>
          )}
        </ScrollView>
      </ImageBackground>

      {/* =================================================
          INPUT
          ================================================= */}

      <View style={styles.inputArea}>
        <View
          style={
            styles.inputContainer
          }
        >
          <TextInput
            value={message}
            onChangeText={
              setMessage
            }
            placeholder="Message..."
            placeholderTextColor="#999"
            style={styles.input}
            returnKeyType="send"
            onSubmitEditing={
              sendMessage
            }
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
              onPress={
                sendMessage
              }
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

      {/* =================================================
          BOTTOM NAVIGATION
          ================================================= */}

      <BottomNavigation
        activeRoute="chat"
      />
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

  /* =======================================================
     HEADER
     ======================================================= */

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

  /* =======================================================
     CHAT
     ======================================================= */

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

  /* =======================================================
     TYPING
     ======================================================= */

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

  /* =======================================================
     QUICK REPLIES
     ======================================================= */

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

  /* =======================================================
     INPUT
     ======================================================= */

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

  /* =======================================================
     MENU
     ======================================================= */

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