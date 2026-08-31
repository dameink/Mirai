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
} from "react-native";
import { useEffect, useRef, useState } from "react";
import { BottomNavigation } from "../../components/bottom-navigation";
import { API_URL } from "../../constants/api";

type Message = {
  id: number;
  text: string;
  sender: "mirai" | "user";
  timestamp?: string;
};

function TypingIndicator() {
  const dot1 = useRef(new Animated.Value(0.3)).current;
  const dot2 = useRef(new Animated.Value(0.3)).current;
  const dot3 = useRef(new Animated.Value(0.3)).current;

  useEffect(() => {
    const animateDot = (
      dot: Animated.Value,
      delay: number,
    ) => {
      return Animated.loop(
        Animated.sequence([
          Animated.delay(delay),
          Animated.timing(dot, {
            toValue: 1,
            duration: 350,
            useNativeDriver: true,
          }),
          Animated.timing(dot, {
            toValue: 0.3,
            duration: 350,
            useNativeDriver: true,
          }),
        ]),
      );
    };

    const animation1 = animateDot(dot1, 0);
    const animation2 = animateDot(dot2, 150);
    const animation3 = animateDot(dot3, 300);

    animation1.start();
    animation2.start();
    animation3.start();

    return () => {
      animation1.stop();
      animation2.stop();
      animation3.stop();
    };
  }, [dot1, dot2, dot3]);

  return (
    <View style={styles.typingBubble}>
      <View style={styles.typingDots}>
        <Animated.View
          style={[styles.typingDot, { opacity: dot1 }]}
        />
        <Animated.View
          style={[styles.typingDot, { opacity: dot2 }]}
        />
        <Animated.View
          style={[styles.typingDot, { opacity: dot3 }]}
        />
      </View>
    </View>
  );
}

export default function ChatScreen() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [menuVisible, setMenuVisible] = useState(false);

  const scrollViewRef = useRef<ScrollView>(null);

  useEffect(() => {
    const loadConversation = async () => {
      try {
        const response = await fetch(
          `${API_URL}/conversation`,
        );

        if (!response.ok) {
          throw new Error("Failed to load conversation");
        }

        const data: {
          role: "user" | "assistant";
          content: string;
          timestamp?: string;
        }[] = await response.json();

        const loadedMessages: Message[] = data.map(
          (item, index) => ({
            id: index + 1,
            text: item.content,
            sender:
              item.role === "user"
                ? "user"
                : "mirai",
            timestamp: item.timestamp,
          }),
        );

        setMessages(loadedMessages);

        setTimeout(() => {
          scrollViewRef.current?.scrollToEnd({
            animated: false,
          });
        }, 100);
      } catch (error) {
        console.error(
          "Failed to load conversation:",
          error,
        );
      }
    };

    loadConversation();
  }, []);

  useEffect(() => {
    if (messages.length === 0) {
      return;
    }

    setTimeout(() => {
      scrollViewRef.current?.scrollToEnd({
        animated: true,
      });
    }, 100);
  }, [messages]);

  const sendMessage = async () => {
    const trimmedMessage = message.trim();

    if (!trimmedMessage || isSending) {
      return;
    }

    const newMessage: Message = {
      id: Date.now(),
      text: trimmedMessage,
      sender: "user",
      timestamp: new Date().toISOString(),
    };

    setMessages((currentMessages) => [
      ...currentMessages,
      newMessage,
    ]);

    setMessage("");
    setIsSending(true);

    try {
      const response = await fetch(
        `${API_URL}/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: trimmedMessage,
          }),
        },
      );

      if (!response.ok) {
        throw new Error(
          "Mirai server is unavailable",
        );
      }

      const data: { mirai?: string } =
        await response.json();

      const miraiMessage = data.mirai;

      if (!miraiMessage) {
        throw new Error(
          "Mirai returned an empty response",
        );
      }

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          id: Date.now() + 1,
          text: miraiMessage,
          sender: "mirai",
          timestamp: new Date().toISOString(),
        },
      ]);
    } catch {
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          id: Date.now() + 1,
          text:
            "I can’t connect right now. Please make sure Mirai’s server is running.",
          sender: "mirai",
        },
      ]);
    } finally {
      setIsSending(false);

      setTimeout(() => {
        scrollViewRef.current?.scrollToEnd({
          animated: true,
        });
      }, 100);
    }
  };

  const clearConversation = async () => {
    try {
      const response = await fetch(
        `${API_URL}/conversation`,
        {
          method: "DELETE",
        },
      );

      if (!response.ok) {
        throw new Error(
          "Failed to clear conversation",
        );
      }

      setMessages([]);
      setMenuVisible(false);
    } catch (error) {
      console.error(
        "Failed to clear conversation:",
        error,
      );
    }
  };

  const resetMirai = async () => {
    try {
      const response = await fetch(
        `${API_URL}/reset`,
        {
          method: "DELETE",
        },
      );

      if (!response.ok) {
        throw new Error("Failed to reset Mirai");
      }

      setMessages([]);
      setMenuVisible(false);
    } catch (error) {
      console.error(
        "Failed to reset Mirai:",
        error,
      );
    }
  };

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
      {/* Header */}

      <View style={styles.header}>
        <View style={styles.miraiInfo}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>
              🌸
            </Text>
          </View>

          <View>
            <Text style={styles.name}>
              Mirai
            </Text>

            <View style={styles.statusRow}>
              <View
                style={[
                  styles.statusDot,
                  isSending &&
                    styles.statusDotThinking,
                ]}
              />

              <Text style={styles.status}>
                {isSending
                  ? "thinking..."
                  : "online"}
              </Text>
            </View>
          </View>
        </View>

        <Pressable
          onPress={() => setMenuVisible(true)}
        >
          <Text style={styles.menu}>
            •••
          </Text>
        </Pressable>
      </View>

      {/* Menu */}

      {menuVisible && (
        <View style={styles.menuOverlay}>
          <Pressable
            style={styles.menuBackdrop}
            onPress={() => setMenuVisible(false)}
          />

          <View style={styles.menuModal}>
            <Text style={styles.menuTitle}>
              Mirai 🌸
            </Text>

            <Text style={styles.menuSubtitle}>
              Chat options
            </Text>

            <Pressable
              style={styles.menuAction}
              onPress={() => {
                setMessages([]);
                setMenuVisible(false);
              }}
            >
              <Text style={styles.menuActionIcon}>
                ＋
              </Text>

              <Text style={styles.menuActionText}>
                New conversation
              </Text>
            </Pressable>

            <Pressable
              style={styles.menuAction}
              onPress={clearConversation}
            >
              <Text
                style={[
                  styles.menuActionText,
                  styles.dangerText,
                ]}
              >
                Clear history
              </Text>
            </Pressable>

            <Pressable
              style={styles.menuAction}
              onPress={resetMirai}
            >
              <Text
                style={[
                  styles.menuActionText,
                  styles.dangerText,
                ]}
              >
                Reset Mirai
              </Text>
            </Pressable>

            <Pressable
              style={styles.cancelButton}
              onPress={() => setMenuVisible(false)}
            >
              <Text style={styles.cancelText}>
                Cancel
              </Text>
            </Pressable>
          </View>
        </View>
      )}

      {/* Chat */}

      <ImageBackground
        source={require("../../../assets/Wallpaper.png")}
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
        >
          {messages.length === 0 && (
            <View style={styles.messageRow}>
              <View style={styles.miraiBubble}>
                <Text style={styles.miraiText}>
                  Hey! I'm Mirai 🌸{"\n\n"}
                  I'm really happy you're here.
                  {"\n\n"}
                  Want to practice English
                  together?
                </Text>
              </View>
            </View>
          )}

          {messages.map((item) => (
            <View
              key={item.id}
              style={[
                styles.messageRow,
                item.sender === "user" &&
                  styles.userRow,
              ]}
            >
              <View
                style={
                  item.sender === "user"
                    ? styles.userBubble
                    : styles.miraiBubble
                }
              >
                <Text
                  style={
                    item.sender === "user"
                      ? styles.userText
                      : styles.miraiText
                  }
                >
                  {item.text}
                </Text>

                {item.timestamp && (
                  <Text style={styles.timestamp}>
                    {new Date(
                      item.timestamp,
                    ).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </Text>
                )}
              </View>
            </View>
          ))}

          {isSending && (
            <View style={styles.messageRow}>
              <TypingIndicator />
            </View>
          )}
        </ScrollView>
      </ImageBackground>

      {/* Input */}

      <View style={styles.inputArea}>
        <View style={styles.inputContainer}>
          <TextInput
            value={message}
            onChangeText={setMessage}
            placeholder="Message..."
            placeholderTextColor="#999"
            style={styles.input}
            returnKeyType="send"
            onSubmitEditing={sendMessage}
          />

          <Pressable
            style={[
              styles.sendButton,
              !message.trim() &&
                styles.sendButtonDisabled,
            ]}
            onPress={sendMessage}
          >
            <Text style={styles.sendText}>
              ➤
            </Text>
          </Pressable>
        </View>
      </View>

      <BottomNavigation activeRoute="chat" />
    </KeyboardAvoidingView>
  );
}

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

  status: {
    fontSize: 12,
    color: "#8E8E8E",
    marginTop: 2,
  },

  statusRow: {
    flexDirection: "row",
    alignItems: "center",
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

  menuAction: {
    height: 56,
    borderRadius: 16,
    backgroundColor: "#FFF5F8",
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 16,
    marginBottom: 10,
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

  cancelButton: {
    height: 50,
    justifyContent: "center",
    alignItems: "center",
    marginTop: 2,
  },

  cancelText: {
    fontSize: 15,
    fontWeight: "600",
    color: "#8E858A",
  },
});