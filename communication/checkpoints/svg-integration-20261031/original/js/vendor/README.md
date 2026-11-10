# Vendored small libraries

Committed so the app works without third-party CDNs for security- and
compatibility-critical dependencies. The reviewed Namelecule JSmol entry bundle
is versioned locally as the explicit exception described below. The large
`j2s/` runtime still uses the existing CDN/local-path configuration and remains
outside Git. This is not a fully offline runtime.

## Namelecule JSmol lifecycle bundle — 2026-10-31 r1

`jsmol/namelecule-20261031-r1/JSmol.min.js` is the exact independently reviewed
candidate from the isolated lifecycle prototype. It owns/cancels applet repaint
and resize work and rejects repaint after applet destruction. v52 exploration
and lessons share this relative, versioned URL with SHA-384 integrity. Neither
`libs=cdn` nor `libs=local` replaces it with an unpatched entry bundle; those
options still select the existing j2s/server paths. Local j2s is not supplied.

- SHA-256: `d99b1168acbbd55d59073943e6fde174513e8b815ddb88ae8f1bfa927961b323`.
- Provenance, upstream notices and license texts: adjacent `PROVENANCE.json`,
  `NOTICE.txt`, `LICENSE-Jmol.txt` and `LICENSE-jQuery.txt`.
- Read-only reconstruction/check: `python3 -B tools/build-jsmol-lifecycle.py --check`.
- Intentional reconstruction: the same command with `--write`. A different
  implementation must use a new reviewed version/path rather than replacing
  the bytes at this URL.
- Archived source/helper/diff and review:
  `docs/checks/jsmol-lifecycle-prototype-20261031/`.

No unpatched CDN fallback is used for the entry bundle. The 3D engine j2s still
comes from the configured external service by default; a complete pinned/offline
distribution and conference rehearsal remain separate work.

## Contents

| Path | Version | License |
|---|---|---|
| `jquery/jquery-4.0.0.min.js` | 4.0.0 | MIT (`jquery/LICENSE.txt`) |
| `dompurify/dompurify-3.4.17.min.js` | 3.4.17 | MPL-2.0 OR Apache-2.0 (`dompurify/LICENSE.txt`) |

## Update procedure

1. Download the minified build from the official source.
2. Update the versioned filename and license file.
3. Compute SHA-512 (base64) and record it below.
4. Update the `<script>` tag in the current `mulermoc-nom-*.html`.
5. Run `node --check` on app JS and smoke-test the app.

```sh
openssl dgst -sha512 -binary FILE | openssl base64 -A
```

## SHA-512 (base64) of committed files

- `jquery/jquery-4.0.0.min.js`:
  `8LENNbXmzI/Gbj+OwXmqR6V4QaUAw0/porPzy1+dQoJqC0JPHedWoe0DDOTL2uHA5XXJyIsPtiMHH86pVlay6A==`
- `dompurify/dompurify-3.4.17.min.js`:
  `2wT0W6vojz3cJuLoa/DxrPVQRinkfRjFWMWIDK4NghTqObEhpem1nEkeK0d9ZE+/hyvfMNuJZlfxM4LsRgeoSA==`

These are the hashes of the local files. CDN SRI values can differ if the CDN
re-encodes the response; verify the exact artifact before using SRI.

## jQuery 4 note

jQuery 4.0.0 is the current major. If a regression appears, vendor 3.7.1 as a
temporary fallback and keep the same path/update procedure.
