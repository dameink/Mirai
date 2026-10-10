import * as SecureStore from "expo-secure-store";
export type PendingChat = { request_id: string; message: string; language: string; mode: string };
const key = (uid: string) => `mirai_outbox_${uid}`;
// Keep each SecureStore entry below platform size limits, including Unicode.
async function savePendingRecord(uid: string, request: PendingChat) {
  const characters = Array.from(JSON.stringify(request));
  const chunks = Math.ceil(characters.length / 300);
  await SecureStore.setItemAsync(key(uid), JSON.stringify({ id: request.request_id, chunks, preparing: true }));
  for (let i = 0; i < chunks; i++) {
    await SecureStore.setItemAsync(`${key(uid)}_${request.request_id}_${i}`, characters.slice(i * 300, (i + 1) * 300).join(""));
  }
  await SecureStore.setItemAsync(key(uid), JSON.stringify({ id: request.request_id, chunks }));
}

async function readPendingRecord(uid: string): Promise<PendingChat | null> {
  const head = await SecureStore.getItemAsync(key(uid));
  if (!head) return null;
  const { id, chunks, preparing, deleting } = JSON.parse(head);
  if (preparing || deleting) { await clearPendingRecord(uid); return null; }
  if (typeof id !== "string" || !Number.isInteger(chunks) || chunks < 1 || chunks > 100) throw new Error("Invalid saved message");
  let encoded = "";
  for (let i = 0; i < chunks; i++) {
    const part = await SecureStore.getItemAsync(`${key(uid)}_${id}_${i}`);
    if (part === null) throw new Error("Saved message incomplete");
    encoded += part;
  }
  const result = JSON.parse(encoded);
  if (result.request_id !== id || typeof result.message !== "string") throw new Error("Invalid saved message");
  return result;
}
async function clearPendingRecord(uid: string) {
  const head = await SecureStore.getItemAsync(key(uid));
  if (!head) return;
  const { id, chunks } = JSON.parse(head);
  // A durable tombstone lets the next launch finish interrupted cleanup.
  await SecureStore.setItemAsync(key(uid), JSON.stringify({ id, chunks, deleting: true }));
  for (let i = 0; i < Math.min(chunks, 100); i++) await SecureStore.deleteItemAsync(`${key(uid)}_${id}_${i}`);
  await SecureStore.deleteItemAsync(key(uid));
}

// Storage operations for one account must not interleave (save vs. clear/reset).
const operations = new Map<string, Promise<unknown>>();
function serial<T>(uid: string, action: () => Promise<T>): Promise<T> {
  const result = (operations.get(uid) ?? Promise.resolve()).catch(() => {}).then(action);
  const tail = result.then(() => {}, () => {});
  operations.set(uid, tail);
  void tail.then(() => { if (operations.get(uid) === tail) operations.delete(uid); });
  return result;
}
export function savePending(uid: string, request: PendingChat) {
  return serial(uid, () => savePendingRecord(uid, request));
}
export function readPending(uid: string) {
  return serial(uid, () => readPendingRecord(uid));
}
export function clearPending(uid: string) {
  return serial(uid, () => clearPendingRecord(uid));
}
