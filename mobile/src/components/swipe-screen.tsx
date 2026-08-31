import { ReactNode } from "react";
import { StyleSheet, View } from "react-native";
import Animated, {
  SharedValue,
  useAnimatedStyle,
} from "react-native-reanimated";

type SwipeScreenProps = {
  children: ReactNode;
  translateX: SharedValue<number>;
};

export function SwipeScreen({
  children,
  translateX,
}: SwipeScreenProps) {
  const animatedStyle = useAnimatedStyle(() => {
    return {
      transform: [
        {
          translateX: translateX.value,
        },
      ],
    };
  });

  return (
    <View style={styles.container}>
      <Animated.View style={[styles.screen, animatedStyle]}>
        {children}
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    overflow: "hidden",
    backgroundColor: "#FFFDFE",
  },

  screen: {
    flex: 1,
    width: "100%",
  },
});
