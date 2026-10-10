/* global __dirname */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');

function harness(fetchImpl, initial = {}) {
  const store = new Map(Object.entries(initial));
  const source = readFileSync(join(__dirname, '../src/auth/auth.ts'), 'utf8');
  const js = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } }).outputText;
  const exports = {};
  vm.runInNewContext(js, {
    exports, Headers, AbortController, setTimeout, clearTimeout,
    fetch: fetchImpl,
    require(name) {
      if (name === '../constants/api') return { API_URL: 'https://offline.test' };
      if (name === 'expo-secure-store') return {
        getItemAsync: async key => store.get(key) || null,
        setItemAsync: async (key, value) => { assert.equal(typeof value, 'string'); store.set(key, value); },
        deleteItemAsync: async key => { store.delete(key); },
      };
      throw new Error(`Unexpected import ${name}`);
    },
  });
  return { api: exports, store };
}
const initial = { mirai_access_token: 'old-access', mirai_refresh_token: 'old-refresh' };
const response = (status, body = {}) => new Response(JSON.stringify(body), { status });
const tokens = { access_token: 'new-access', refresh_token: 'new-refresh' };

test('registration returns verification message without saving undefined tokens', async () => {
  const { api, store } = harness(async () => response(201, { message: 'Verify email' }));
  assert.equal((await api.register('a@example.com', 'password')).message, 'Verify email');
  assert.equal(store.size, 0);
});

test('parallel 401 responses share one refresh and retry with rotated token', async () => {
  let refreshes = 0;
  const { api, store } = harness(async (url, options) => {
    if (url.endsWith('/auth/refresh')) {
      refreshes++;
      await new Promise(resolve => setTimeout(resolve, 10));
      return response(200, tokens);
    }
    return response(options.headers.get('Authorization') === 'Bearer new-access' ? 200 : 401);
  }, initial);
  const results = await Promise.all([api.authFetch('/state'), api.authFetch('/conversation'), api.authFetch('/gamification')]);
  assert.ok(results.every(r => r.status === 200));
  assert.equal(refreshes, 1);
  assert.equal(await api.getRefreshToken(), 'new-refresh');
});

test('invalid refresh clears credentials and notifies auth context', async () => {
  let expired = 0;
  const { api, store } = harness(async () => response(401), initial);
  api.onSessionExpired(() => expired++);
  assert.equal((await api.authFetch('/state')).status, 401);
  assert.equal(store.size, 0);
  assert.equal(expired, 1);
});

test('temporary refresh outage preserves credentials', async () => {
  const { api, store } = harness(async url => response(url.endsWith('/auth/refresh') ? 503 : 401), initial);
  await assert.rejects(api.authFetch('/state'), /temporarily unavailable/);
  assert.equal(store.get('mirai_refresh_token'), 'old-refresh');
});

test('logout clears local session even without network', async () => {
  const { api, store } = harness(async () => { throw new Error('offline'); }, initial);
  await api.logout();
  assert.equal(store.size, 0);
});

test('late refresh response cannot resurrect a logged-out session', async () => {
  let release;
  let started;
  const refreshing = new Promise(resolve => { started = resolve; });
  const { api, store } = harness(async url => {
    if (url.endsWith('/auth/refresh')) {
      started();
      await new Promise(resolve => { release = resolve; });
      return response(200, tokens);
    }
    return response(url.endsWith('/auth/logout') ? 200 : 401);
  }, initial);
  const request = api.authFetch('/state');
  await refreshing;
  await api.logout();
  release();
  assert.equal((await request).status, 401);
  assert.equal(store.size, 0);
});

test('failed credentials are surfaced as validation text', async () => {
  const { api } = harness(async () => response(422, { detail: [{ msg: 'invalid email' }] }));
  await assert.rejects(api.login('invalid', ''), /check your email and password/);
});

test('unverified login preserves HTTP status for the verification screen', async () => {
  const { api, store } = harness(async () => response(403, { detail: 'Please verify your email' }));
  await assert.rejects(api.login('a@example.com', 'password'), error => error.status === 403);
  assert.equal(store.size, 0);
});

test('session version changes on logout so stale profile loads can be ignored', async () => {
  const { api } = harness(async () => response(200), initial);
  const version = api.getSessionVersion();
  await api.logout();
  assert.notEqual(api.getSessionVersion(), version);
});

test('late login cannot restore credentials after logout', async () => {
  let release;
  const { api, store } = harness(async url => {
    if (url.endsWith('/auth/login')) return new Promise(resolve => { release = () => resolve(response(200, tokens)); });
    return response(200);
  });
  const signingIn = api.login('a@example.com', 'password');
  await api.logout();
  release();
  await assert.rejects(signingIn, /cancelled/);
  assert.equal(store.size, 0);
});
test('newer login wins when two login responses arrive out of order', async () => {
  let release;
  let count = 0;
  const { api, store } = harness(async () => {
    if (++count === 1) return new Promise(resolve => { release = () => resolve(response(200, { access_token: 'stale', refresh_token: 'stale' })); });
    return response(200, tokens);
  });
  const stale = api.login('a@example.com', 'password');
  await api.login('b@example.com', 'password');
  release();
  await assert.rejects(stale, /cancelled/);
  assert.equal(await api.getAccessToken(), 'new-access');
});
test('HTML gateway failure produces a useful authentication error', async () => {
  const { api } = harness(async () => new Response('<html>Unavailable</html>', { status: 503 }));
  await assert.rejects(api.login('a@example.com', 'password'), error => error.status === 503 && /temporarily unavailable/.test(error.message));
});

test('rotated credentials survive a new application process', async () => {
  const first = harness(async (url, options) => url.endsWith('/auth/refresh') ? response(200, tokens) : response(options.headers.get('Authorization') === 'Bearer new-access' ? 200 : 401), initial);
  assert.equal((await first.api.authFetch('/auth/me')).status, 200);
  assert.ok(first.store.has('mirai_session_v2'));
  assert.ok(!first.store.has('mirai_access_token'));
  const restarted = harness(async (_url, options) => response(options.headers.get('Authorization') === 'Bearer new-access' ? 200 : 401), Object.fromEntries(first.store));
  assert.equal((await restarted.api.authFetch('/auth/me')).status, 200);
});

test('a retained refresh token recovers a missing legacy access token', async () => {
  const { api } = harness(async (url, options) => url.endsWith('/auth/refresh') ? response(200, tokens) : response(options.headers.get('Authorization') === 'Bearer new-access' ? 200 : 401), { mirai_refresh_token: 'old-refresh' });
  assert.equal((await api.authFetch('/auth/me')).status, 200);
});

test('a rejected replacement token ends the session instead of looping on 401', async () => {
  let expired = 0;
  const { api, store } = harness(async url => url.endsWith('/auth/refresh') ? response(200, tokens) : response(401), initial);
  api.onSessionExpired(() => expired++);
  assert.equal((await api.authFetch('/auth/me')).status, 401);
  assert.equal(expired, 1);
  assert.equal(store.size, 0);
});

test('logout removes a migrated atomic session', async () => {
  const { api, store } = harness(async () => response(200), { mirai_session_v2: JSON.stringify({ accessToken: 'a', refreshToken: 'r' }) });
  await api.logout();
  assert.equal(store.size, 0);
});
