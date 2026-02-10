# Releasing

This repo ships a thin `45d-drivemap.plg` that downloads a versioned plugin
tarball from GitHub Releases and extracts it on Unraid.

`scripts/render-plg` now renders `<CHANGES>` from the matching version section
in `CHANGELOG.md` and fails if that section is missing.

## Changelog flow (KNope)

1. Create a change file:
   - `knope document-change`
2. Prepare a release locally:
   - `knope release --dry-run`
3. Run the real release workflow locally (commits changelog + tags + pushes):
   - `knope release`

KNope configuration lives in `knope.toml` and writes release notes to
`CHANGELOG.md`.

## Automatic release assets

1. Push a tag in the format `vX.Y.Z`.
2. GitHub Actions workflow `.github/workflows/release.yml` will:
   - build `packages/45d-drivemap-X.Y.Z.txz`
   - render `45d-drivemap.plg` with matching checksum and release URLs
   - publish both assets to that release

Because `plugin_url` points to:

`https://github.com/<owner>/<repo>/releases/latest/download/45d-drivemap.plg`

the install URL remains stable while payloads stay versioned.

## Local build helpers

- Build full plugin package:

`scripts/build-plugin-txz 0.1.3`

- Render release plg from template:

`scripts/render-plg 0.1.3 <sha256> <owner/repo>`
