import { Linking, Pressable, ScrollView, StyleSheet, Text } from "react-native";
export default function AboutScreen() {
  return <ScrollView contentContainerStyle={styles.container}>
    <Text style={styles.title}>Mirai</Text>
    <Text>AI conversation and English practice. AI feedback may be inaccurate.</Text>
    <Text style={styles.heading}>Your data</Text>
    <Text>Mirai stores your account email, conversation history, learning progress and preferences. Conversation context is sent through OpenRouter to the configured AI provider to generate replies. Resend delivers account emails; Expo delivers notifications if you allow them. Hosting is provided by Render.</Text>
    <Text>Credentials and unconfirmed messages are kept in your device’s secure storage. Do not send passwords, payment details or sensitive personal information in chats.</Text>
    <Text style={styles.heading}>Control and deletion</Text>
    <Text>You can disable notifications, clear conversations or delete your account in Settings. Account deletion requires your password. Separate backups and provider records may remain under their retention policies. Contact support for help with data requests.</Text>
    <Text style={styles.heading}>Learning limits</Text>
    <Text>Structured practice currently focuses on English. Japanese and Spanish conversation options do not yet provide equivalent courses. Mirai is not a medical, legal or emergency service.</Text>
    <Text style={styles.heading}>Support</Text>
    <Text>Damir Jaldybayev</Text>
    <Pressable accessibilityRole="link" onPress={() => { void Linking.openURL("mailto:damikstrong@gmail.com"); }}><Text style={styles.link}>damikstrong@gmail.com</Text></Pressable>
  </ScrollView>;
}
const styles = StyleSheet.create({ container: { padding: 24, paddingTop: 40, paddingBottom: 60, gap: 16, backgroundColor: "#FFFDFE" }, title: { fontSize: 26, fontWeight: "700" }, heading: { fontSize: 18, fontWeight: "600", marginTop: 8 }, link: { color: "#A72C48", textDecorationLine: "underline" } });
