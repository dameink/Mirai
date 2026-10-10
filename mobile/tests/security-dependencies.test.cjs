const { test } = require('node:test');
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');

test('query-string preserves Unicode, arrays and malformed URLs with the fixed decoder', () => {
  const query = require('query-string');
  assert.equal(query.parse('q=%E3%81%82+hello').q, 'あ hello');
  assert.deepEqual(query.parse('a=1&a=2').a, ['1', '2']);
  assert.equal(query.parse('q=%ZZ').q, '%ZZ');
  assert.equal(query.parse(query.stringify({ q: '🌸 & hello' })).q, '🌸 & hello');
  // Run hostile input in a child with a hard deadline: a regression cannot hang tests.
  const result = spawnSync(process.execPath, ['-e', "require('query-string').parse('q=' + '%FF'.repeat(20000))"], { timeout: 5000 });
  assert.equal(result.status, 0, String(result.error || result.stderr));
});

test('Xcode project IDs still use the supported UUID v4 API', () => {
  const project = require('xcode').project('unused.pbxproj');
  project.hash = { project: { objects: {} } };
  const first = project.generateUuid();
  assert.match(first, /^[A-F0-9]{24}$/);
  assert.notEqual(project.generateUuid(), first);
});

test('brace patterns reject excessive nesting before recursive traversal', () => {
  const braces = require('braces');
  assert.deepEqual(braces.expand('src/{app,auth}/*.ts'), ['src/app/*.ts', 'src/auth/*.ts']);
  for (const method of ['parse', 'compile', 'expand', 'stringify']) {
    assert.throws(() => braces[method]('{'.repeat(4000) + 'a,b' + '}'.repeat(4000)), /nesting exceeds safe limit/);
  }
});

test('RSA verification rejects extra nested DigestAlgorithm elements but accepts valid signatures', () => {
  const forge = require('node-forge');
  const { publicKey, privateKey } = forge.pki.rsa.generateKeyPair({ bits: 1024 });
  const md = forge.md.sha256.create().update('Mirai security regression');
  const digest = md.digest().getBytes();
  assert.equal(publicKey.verify(digest, privateKey.sign(md)), true);
  const a = forge.asn1;
  const oid = () => a.create(a.Class.UNIVERSAL, a.Type.OID, false, a.oidToDer(forge.oids.sha256).getBytes());
  const nil = () => a.create(a.Class.UNIVERSAL, a.Type.NULL, false, '');
  for (const algorithm of [[oid(), nil(), nil()], [oid(), nil(), a.create(a.Class.UNIVERSAL, a.Type.SEQUENCE, true, [])]]) {
    const info = a.create(a.Class.UNIVERSAL, a.Type.SEQUENCE, true, [
      a.create(a.Class.UNIVERSAL, a.Type.SEQUENCE, true, algorithm),
      a.create(a.Class.UNIVERSAL, a.Type.OCTETSTRING, false, digest),
    ]);
    const malformed = privateKey.sign(a.toDer(info).getBytes(), 'NONE');
    assert.throws(() => publicKey.verify(digest, malformed), /DigestInfo/);
  }
});

test('brace AST walkers also reject excessive nesting supplied directly', () => {
  const braces = require('braces');
  for (const method of ['compile', 'expand', 'stringify']) {
    let ast = { type: 'text', value: 'safe' };
    for (let i = 0; i < 500; i++) ast = { type: 'root', nodes: [ast] };
    assert.throws(() => braces[method](ast), /nesting exceeds safe limit/);
  }
});
