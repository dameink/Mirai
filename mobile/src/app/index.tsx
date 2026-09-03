
import {
  Animated,
  Easing,
  Pressable,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { router } from "expo-router";
import { useEffect, useRef } from "react";
import { useAuth } from "../auth/AuthContext";

export default function Index() {
  const { user, loading } = useAuth();

  const sakuraScale = useRef(new Animated.Value(1)).current;
  const sakuraOpacity = useRef(new Animated.Value(0.9)).current;
  const contentOpacity = useRef(new Animated.Value(0)).current;
  const contentTranslateY = useRef(new Animated.Value(18)).current;
  const buttonScale = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [loading, user]);

  useEffect(() => {
    if (loading || !user) {
      return;
    }

    Animated.parallel([
      Animated.timing(contentOpacity, {
        toValue: 1,
        duration: 650,
        easing: Easing.out(Easing.ease),
        useNativeDriver: true,
      }),

      Animated.timing(contentTranslateY, {
        toValue: 0,
        duration: 700,
        easing: Easing.out(Easing.ease),
        useNativeDriver: true,
      }),
    ]).start();

    const sakuraAnimation = Animated.loop(
      Animated.sequence([
        Animated.parallel([
          Animated.timing(sakuraScale, {
            toValue: 1.06,
            duration: 1800,
            easing: Easing.inOut(Easing.ease),
            useNativeDriver: true,
          }),

          Animated.timing(sakuraOpacity, {
            toValue: 1,
            duration: 1800,
            easing: Easing.inOut(Easing.ease),
            useNativeDriver: true,
          }),
        ]),

        Animated.parallel([
          Animated.timing(sakuraScale, {
            toValue: 1,
            duration: 1800,
            easing: Easing.inOut(Easing.ease),
            useNativeDriver: true,
          }),

          Animated.timing(sakuraOpacity, {
            toValue: 0.9,
            duration: 1800,
            easing: Easing.inOut(Easing.ease),
            useNativeDriver: true,
          }),
        ]),
      ])
    );

    sakuraAnimation.start();

    return () => {
      sakuraAnimation.stop();
    };
  }, [
    loading,
    user,
    sakuraScale,
    sakuraOpacity,
    contentOpacity,
    contentTranslateY,
  ]);

  if (loading || !user) {
    return null;
  }

  const pressIn = () => {
    Animated.spring(buttonScale, {
      toValue: 0.96,
      useNativeDriver: true,
      speed: 30,
      bounciness: 3,
    }).start();
  };

  const pressOut = () => {
    Animated.spring(buttonScale, {
      toValue: 1,
      useNativeDriver: true,
      speed: 24,
      bounciness: 6,
    }).start();
  };

  return (
    <View style={styles.container}>
      <View style={styles.backgroundGlow} />

      <Animated.View
        style={[
          styles.content,
          {
            opacity: contentOpacity,
            transform: [
              {
                translateY: contentTranslateY,
              },
            ],
          },
        ]}
      >
        <Animated.View
          style={[
            styles.sakuraContainer,
            {
              opacity: sakuraOpacity,
              transform: [
                {
                  scale: sakuraScale,
                },
              ],
            },
          ]}
        >
          <Text style={styles.sakura}>🌸</Text>
        </Animated.View>

        <Text style={styles.title}>Mirai</Text>

        <View style={styles.titleUnderline} />

        <Text style={styles.subtitle}>
          Your companion for learning and growing
        </Text>

        <Text style={styles.welcome}>
          Welcome back
        </Text>

        <Animated.View
          style={{
            transform: [
              {
                scale: buttonScale,
              },
            ],
          }}
        >
          <Pressable
            style={({ pressed }) => [
              styles.button,
              pressed && styles.buttonPressed,
            ]}
            onPress={() => router.replace("/chat")}
            onPressIn={pressIn}
            onPressOut={pressOut}
          >
            <Text style={styles.buttonText}>Start</Text>
            <Text style={styles.buttonArrow}>→</Text>
          </Pressable>
        </Animated.View>

        <Text style={styles.footer}>
          Learn · Talk · Grow
        </Text>
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F7F0E6",
    justifyContent: "center",
    alignItems: "center",
    overflow: "hidden",
  },

  backgroundGlow: {
    position: "absolute",
    width: 320,
    height: 320,
    borderRadius: 160,
    backgroundColor: "#FFE6EF",
    opacity: 0.35,
    top: "24%",
  },

  content: {
    alignItems: "center",
    width: "100%",
    paddingHorizontal: 32,
  },

  sakuraContainer: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: "rgba(255,255,255,0.48)",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 14,
    shadowColor: "#D9A6A6",
    shadowOffset: {
      width: 0,
      height: 8,
    },
    shadowOpacity: 0.12,
    shadowRadius: 18,
    elevation: 4,
  },

  sakura: {
    fontSize: 58,
  },

  title: {
    fontSize: 52,
    fontWeight: "600",
    color: "#D9A6A6",
    letterSpacing: 1.5,
  },

  titleUnderline: {
    width: 42,
    height: 3,
    borderRadius: 2,
    backgroundColor: "#E7B9B9",
    marginTop: 8,
  },

  subtitle: {
    marginTop: 14,
    fontSize: 16,
    color: "#8E7C72",
    textAlign: "center",
    lineHeight: 23,
  },

  welcome: {
    marginTop: 30,
    fontSize: 13,
    color: "#A99A91",
    letterSpacing: 0.5,
  },

  button: {
    marginTop: 18,
    width: 220,
    height: 58,
    borderRadius: 29,
    backgroundColor: "#D9A6A6",
    justifyContent: "center",
    alignItems: "center",
    flexDirection: "row",
    shadowColor: "#C68F8F",
    shadowOffset: {
      width: 0,
      height: 8,
    },
    shadowOpacity: 0.2,
    shadowRadius: 14,
    elevation: 5,
  },

  buttonPressed: {
    opacity: 0.85,
  },

  buttonText: {
    color: "#FFFFFF",
    fontSize: 18,
    fontWeight: "600",
    letterSpacing: 0.3,
  },

  buttonArrow: {
    color: "#FFFFFF",
    fontSize: 20,
    marginLeft: 10,
    marginTop: -1,
  },

  footer: {
    marginTop: 34,
    fontSize: 12,
    color: "#B2A49D",
    letterSpacing: 1,
  },
});