import { createMaterialTopTabNavigator } from "expo-router/js-top-tabs";
import { withLayoutContext } from "expo-router";

const { Navigator } = createMaterialTopTabNavigator();

const MaterialTopTabs = withLayoutContext(Navigator);

export default function TabsLayout() {
  return (
    <MaterialTopTabs
      initialRouteName="chat"
      tabBar={() => null}
      screenOptions={{
        swipeEnabled: true,
        animationEnabled: true,
        lazy: false,
        tabBarStyle: {
          display: "none",
        },
      }}
    >
      <MaterialTopTabs.Screen
        name="chat"
        options={{
          title: "Chat",
        }}
      />

      <MaterialTopTabs.Screen
        name="mirai"
        options={{
          title: "Mirai",
        }}
      />

      <MaterialTopTabs.Screen
        name="learn"
        options={{
          title: "Learn",
        }}
      />

      <MaterialTopTabs.Screen
        name="profile"
        options={{
          title: "Me",
        }}
      />
    </MaterialTopTabs>
  );
}