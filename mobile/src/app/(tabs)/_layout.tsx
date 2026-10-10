import { createMaterialTopTabNavigator } from "expo-router/js-top-tabs";
import { Redirect, withLayoutContext } from "expo-router";
import { useAuth } from "../../auth/AuthContext";

const { Navigator } = createMaterialTopTabNavigator();

const MaterialTopTabs = withLayoutContext(Navigator);

export default function TabsLayout() {
  const { user, loading } = useAuth();
  if (loading) return null;
  if (!user) return <Redirect href="/login" />;
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