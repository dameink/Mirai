import { useRef, useState } from 'react';
import { Alert, Modal, Pressable, ScrollView, Text, View } from 'react-native';
import { authFetch, getSessionVersion } from '../auth/auth';
import { requestErrorMessage, throwResponseError } from '../auth/errors';

const reasons = [
  ['harmful', 'Harmful or unsafe'], ['sexual', 'Sexual content'],
  ['hate', 'Hate or harassment'], ['incorrect', 'Incorrect or misleading'], ['other', 'Other'],
] as const;

export function ReportReply({ messageId }: { messageId?: string }) {
  const [open, setOpen] = useState(false);
  const [reason, setReason] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const busy = useRef(false);
  const submit = async () => {
    if (!messageId || !reason || busy.current) return;
    busy.current = true;
    setSending(true);
    const version = getSessionVersion();
    try {
      const response = await authFetch('/content-reports', {
        method: 'POST', body: JSON.stringify({ message_id: messageId, reason }),
      });
      if (!response.ok) await throwResponseError(response);
      const result = await response.json();
      if (result.status !== 'received') throw new Error('Report was not confirmed. Please try again.');
      if (version !== getSessionVersion()) return;
      setOpen(false);
      Alert.alert('Report received', 'Thank you. Your report has been saved for review.');
    } catch (error) {
      if (version === getSessionVersion()) Alert.alert('Report not sent', requestErrorMessage(error));
    } finally { busy.current = false; setSending(false); }
  };
  return <>
    <Pressable accessibilityRole="button" accessibilityLabel="Report this AI reply" onPress={() => {
      if (!messageId) { Alert.alert('Reply not ready', 'Reload the conversation before reporting this reply.'); return; }
      setReason(null); setOpen(true);
    }} style={{ minHeight: 44, justifyContent: 'center' }}>
      <Text style={{ color: '#79334A', fontSize: 12 }}>Report reply</Text>
    </Pressable>
    <Modal visible={open} transparent animationType="fade" onRequestClose={() => { if (!sending) setOpen(false); }}>
      <View style={{ flex: 1, backgroundColor: '#0008', justifyContent: 'center', padding: 24 }}>
        <ScrollView style={{ maxHeight: '85%', backgroundColor: '#FFFDFE', borderRadius: 20 }} contentContainerStyle={{ padding: 24, gap: 12 }}>
          <Text style={{ fontSize: 22, fontWeight: '700' }}>Report AI reply</Text>
          <Text>The selected reply and your reason will be sent to Mirai’s developer for review. A copy stays with the report if you clear the chat; deleting your account removes it.</Text>
          {reasons.map(([value, label]) => <Pressable key={value} accessibilityRole="radio" accessibilityState={{ checked: reason === value, disabled: sending }} disabled={sending} onPress={() => setReason(value)} style={{ padding: 14, borderWidth: 1, borderColor: reason === value ? '#79334A' : '#DDD', borderRadius: 10 }}>
            <Text>{reason === value ? '● ' : '○ '}{label}</Text>
          </Pressable>)}
          <Pressable accessibilityRole="button" disabled={!reason || sending} onPress={() => { void submit(); }} style={{ padding: 14, opacity: !reason || sending ? 0.45 : 1, backgroundColor: '#79334A', borderRadius: 10 }}>
            <Text style={{ color: 'white', textAlign: 'center' }}>{sending ? 'Sending…' : 'Send report'}</Text>
          </Pressable>
          <Pressable accessibilityRole="button" disabled={sending} onPress={() => setOpen(false)} style={{ padding: 14 }}><Text style={{ textAlign: 'center' }}>Cancel</Text></Pressable>
        </ScrollView>
      </View>
    </Modal>
  </>;
}
