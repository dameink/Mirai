/* global __dirname */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const vm = require('node:vm');
const ts = require('typescript');
const api = {};
vm.runInNewContext(ts.transpileModule(readFileSync(join(__dirname, '../src/auth/errors.ts'), 'utf8'), { compilerOptions: { module: ts.ModuleKind.CommonJS } }).outputText, { exports: api, Error });

test('provider quotas and expired sessions are not labelled as an internet outage', async () => {
  for (const [status, body, expected] of [[503, { code: 'model_rate_limited' }, /request limit/], [401, {}, /sign in again/], [503, {}, /service is temporarily unavailable/]]) {
    try { await api.throwResponseError(new Response(JSON.stringify(body), { status })); }
    catch (error) { assert.match(api.requestErrorMessage(error), expected); }
  }
});

test('HTML gateway responses do not hide the service error', async () => {
  await assert.rejects(api.throwResponseError(new Response('<html>Bad gateway</html>', { status: 502 })), error => /service is temporarily unavailable/.test(api.requestErrorMessage(error)));
});
