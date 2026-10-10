/* global __dirname, process */
const { spawnSync } = require('node:child_process');
const { resolve } = require('node:path');
const root = resolve(__dirname, '..');
const profile = require('../eas.json').build.preview;
const endpoint = new URL(profile.env.EXPO_PUBLIC_API_URL);
if (endpoint.protocol !== 'https:' || endpoint.username || endpoint.password) {
  throw new Error('APK preview requires an HTTPS API URL without credentials');
}
if (profile.android.buildType !== 'apk' || profile.distribution !== 'internal') {
  throw new Error('Preview must produce an internal APK');
}
const env = { ...process.env, EXPO_PUBLIC_API_URL: endpoint.href.replace(/\/$/, ''), EXPO_NO_DOTENV: '1', EAS_NO_VCS: '1', EAS_PROJECT_ROOT: root };
function run(command, args) {
  const result = spawnSync(command, args, { cwd: root, env, stdio: 'inherit' });
  if (result.error) throw result.error;
  if (result.status !== 0) process.exit(result.status || 1);
}
run('npm', ['run', 'check']);
run('npx', ['expo', 'export', '--platform', 'android', '--output-dir', 'dist/apk-check']);
if (process.argv.includes('--build')) {
  run('eas', ['build', '--platform', 'android', '--profile', 'preview']);
} else {
  console.log('Android bundle checks passed. This is not a signed APK or a server/device test.');
}
