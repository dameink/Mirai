/* global __dirname, Buffer */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');
function harness(store = new Map(), failAfter = Infinity) {
  let writes = 0;
  const source = readFileSync(join(__dirname, '../src/storage/outbox.ts'), 'utf8');
  const js = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } }).outputText;
  const exports = {};
  vm.runInNewContext(js, { exports, require() { return {
    getItemAsync: async key => store.get(key) ?? null,
    setItemAsync: async (key, value) => { if (++writes > failAfter) throw new Error('storage interrupted'); assert.ok(Buffer.byteLength(value) <= 2048); store.set(key, value); },
    deleteItemAsync: async key => store.delete(key),
  }; } });
  return { api: exports, store };
}
const payload = { request_id: 'request-123', message: '🌸こんにちは'.repeat(600), language: 'Japanese', mode: 'Casual' };
test('pending Unicode message survives restart with the same request ID and owner isolation', async () => {
  const first = harness(); await first.api.savePending('one', payload);
  const restarted = harness(first.store);
  assert.equal(JSON.stringify(await restarted.api.readPending('one')), JSON.stringify(payload));
  assert.equal(await restarted.api.readPending('two'), null);
  await restarted.api.clearPending('one'); assert.equal(first.store.size, 0);
});
test('interrupted save is cleaned up on restart without sending a partial request', async () => {
  const first = harness(new Map(), 2);
  await assert.rejects(first.api.savePending('one', payload), /storage interrupted/);
  const restarted = harness(first.store);
  assert.equal(await restarted.api.readPending('one'), null);
  assert.equal(first.store.size, 0);
});

test('clear during save removes the entire pending record without orphan chunks', async () => {
  const { api, store } = harness();
  await Promise.all([api.savePending('one', payload), api.clearPending('one')]);
  assert.equal(await api.readPending('one'), null);
  assert.equal(store.size, 0);
});
test('read during save waits for the complete durable message', async () => {
  const { api } = harness();
  const saving = api.savePending('one', payload);
  const reading = api.readPending('one');
  await saving;
  assert.equal(JSON.stringify(await reading), JSON.stringify(payload));
});
