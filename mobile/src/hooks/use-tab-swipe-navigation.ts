
import { router } from "expo-router";
import { Dimensions, PanResponder } from "react-native";
import {
  runOnJS,
  useSharedValue,
  withTiming,
} from "react-native-reanimated";
import { TabRouteName } from "../components/bottom-navigation";

const routes: TabRouteName[] = [
  "chat",
  "mirai",
  "learn",
  "profile",
];

const SWIPE_DISTANCE = 72;
const SWIPE_VELOCITY = 0.45;

const screenWidth = Dimensions.get("window").width;

export function useTabSwipeNavigation(
  activeRoute: TabRouteName,
) {
  const translateX = useSharedValue(0);

  const navigateToRoute = (
    targetRoute: TabRouteName,
  ) => {
    if (targetRoute === activeRoute) {
      translateX.value = 0;
      return;
    }

    router.push(`/(tabs)/${targetRoute}`);
  };

  const panResponder = PanResponder.create({
    onMoveShouldSetPanResponder: (_, gesture) => {
      const horizontalDistance = Math.abs(gesture.dx);
      const verticalDistance = Math.abs(gesture.dy);

      return (
        horizontalDistance > 10 &&
        horizontalDistance > verticalDistance * 1.2
      );
    },

    onPanResponderGrant: () => {
      translateX.value = 0;
    },

    onPanResponderMove: (_, gesture) => {
      translateX.value = Math.max(
        -screenWidth,
        Math.min(screenWidth, gesture.dx),
      );
    },

    onPanResponderRelease: (_, gesture) => {
      const currentIndex = routes.indexOf(activeRoute);

      if (currentIndex === -1) {
        translateX.value = withTiming(0, {
          duration: 180,
        });

        return;
      }

      const shouldNavigate =
        Math.abs(gesture.dx) >= SWIPE_DISTANCE ||
        Math.abs(gesture.vx) >= SWIPE_VELOCITY;

      if (!shouldNavigate) {
        translateX.value = withTiming(0, {
          duration: 180,
        });

        return;
      }

      const isSwipeLeft = gesture.dx < 0;

      const nextIndex = isSwipeLeft
        ? (currentIndex + 1) % routes.length
        : (currentIndex - 1 + routes.length) % routes.length;

      const nextRoute = routes[nextIndex];

      translateX.value = withTiming(
        isSwipeLeft ? -screenWidth : screenWidth,
        {
          duration: 180,
        },
        (finished) => {
          if (finished) {
            runOnJS(navigateToRoute)(nextRoute);
          }
        },
      );
    },

    onPanResponderTerminate: () => {
      translateX.value = withTiming(0, {
        duration: 180,
      });
    },

    onPanResponderTerminationRequest: () => {
      return false;
    },
  });

  return {
    panHandlers: panResponder.panHandlers,
    translateX,
  };
}
