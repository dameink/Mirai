# Dependency security — 2026-10-09

Scope: mobile npm dependencies, including the Expo build toolchain. This is not a security audit of the Python server or the complete application.

## Remediations

- `uuid` overridden to 11.1.1. Its CommonJS v4 API is exercised through the actual xcode project-ID generator. Addresses GHSA-w5hq-g745-h8pq.
- `decode-uri-component` overridden to 0.5.0. `query-string` 7.1.3 has a minimal default-export compatibility patch. Tests cover Unicode, repeated query parameters, malformed escapes and large malformed input with a child-process deadline. Addresses GHSA-vcc3-ghjq-m6fr.
- `braces` 3.0.3 has a local depth guard in the parser and recursive compile/expand/stringify walkers. Rejects excessive nesting at 128 instead of exhausting the stack. Direct AST inputs are also covered. Local mitigation for GHSA-vfj7-8cjw-p6xm; not a vendor release.
- `node-forge` 1.4.0 has a local strict check of the nested DigestAlgorithm sequence: one OID and at most one empty primitive NULL parameter. Regression creates a correctly padded RSA signature containing extra nested elements; verification must reject it. Normal SHA-256 signatures still verify. Local mitigation for GHSA-86w9-cpqp-85rv; not an upstream-reviewed cryptographic release.

The two locally patched advisories have no published fixed npm versions as of this check:
https://github.com/advisories/GHSA-vfj7-8cjw-p6xm
https://github.com/advisories/GHSA-86w9-cpqp-85rv

## Reproducibility

`patches/` is included in the EAS source archive. `postinstall` runs `patch-package --error-on-fail`. Do not install with `--ignore-scripts` for builds. Build environments must install devDependencies (patch-package is a build tool).

Verified fresh `npm ci --ignore-scripts`, then negative-control tests: 4 of 5 security checks fail without patches. Applying `npm run postinstall` restores all checks. Full `npm run apk:check` passes: TypeScript, ESLint, 21 tests and Android/Hermes export.

Raw npm audit still reports the original versions: 21 high entries in the full tree, representing two underlying advisories propagated through parent dependencies. This is not a zero-finding audit and alerts have not been suppressed. The patch tool itself adds parent-chain findings through braces, not a third distinct advisory. Review new advisories normally.

Replace local patches with vendor fixes when available, rerun the regression tests, and remove an override/patch only after verifying the replacement. Local patches require maintenance and independent review before a public release. No signed APK or physical-device validation was performed in this task.
