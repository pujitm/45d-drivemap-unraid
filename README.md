# 45D Drive Map (Unraid Plugin)

Embed the 45Drives disk map UI directly in Unraid's **Main** page and generate
map/server metadata on the Unraid host.

## Stable Plugin Links

- Install / update URL (stable latest):
  - `https://github.com/unraid/45d-drivemap/releases/latest/download/45d-drivemap.plg`
- Release history (version-specific assets):
  - `https://github.com/unraid/45d-drivemap/releases`

## What This Plugin Does

- Adds a **Drive Map** section to the top of Unraid Main (`Main:0`).
- Serves the 45Drives disk-map frontend from plugin assets.
- Generates and caches:
  - `drivemap.json`
  - `server_info.json`
  - runtime logs
  in `/var/local/45d/`.
- Supports SMART-derived fields and ZFS info endpoints used by the UI.

## Getting Started

1. In Unraid, open **Plugins**.
2. Choose **Install Plugin**.
3. Paste the stable URL:
   - `https://github.com/unraid/45d-drivemap/releases/latest/download/45d-drivemap.plg`
4. Install, then open **Main** and scroll to **Drive Map** (top section).
5. Click **Refresh** in the Drive Map toolbar to force regeneration if needed.

## Configuration Overrides

- To override model inference, place a product name override in
  `/boot/config/plugins/45d-drivemap/product_name`.
- To override HBA port/phy order for non-standard motherboard/HBA builds, create
  `/boot/config/plugins/45d-drivemap/hba_phy_order_overrides.json`:

```json
{
  "X11CUSTOM": {
    "HBA 9400-16i": [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
  }
}
```

The top-level key is the motherboard product name from `server_info.json`, and
the nested key is the HBA model. Use `*` as the motherboard key for a global HBA
model override. Remove `/etc/vdev_id.conf` and refresh the map to regenerate
aliases after changing this file.

To collect the current HBA/SATA path/device evidence for building an override, run:

```bash
/usr/local/emhttp/plugins/45d-drivemap/scripts/45d-list-hba-paths
```

It prints `hba_path`, resolved `/dev/sdX`, serial, model, size, PCI bus, and
phy/target/ATA port. Use `--json` when attaching machine-readable output to a
support ticket.

## Uninstall Behavior

Removing the plugin cleans up:

- `/usr/local/emhttp/plugins/45d-drivemap`
- `/var/local/45d`
- cached package files under `/boot/config/plugins/45d-drivemap`

## Development

### Disk-map frontend (45Drives base + Unraid patches)

The **base** disk-map UI is built by **45Drives**; we vendor it and layer
Unraid-specific patches on top. The shipped bundle is therefore *not* a clean
upstream snapshot — see `assets/45d/README.md` for the full provenance and the
list of Unraid patches (Cockpit API shim, drive standby display, storage
context).

- The shipped bundle lives in `assets/45d/45drives-disks/` (45Drives base
  v2.5.4-2 + Unraid patches).
- The matching Vue source is under `vendor/45drives/cockpit-hardware/45drives-disks/`
  (upstream v2.5.8 + Unraid feature source); it builds with
  `npm install && npm run build` (vendored dep shim in `src/lib/`). Do **not**
  run the upstream `make` here — it fans out to sibling plugins
  (`45drives-motherboard`, `45drives-system`) that need 45Drives' private
  package registry and fail with `401 Unauthorized`.
- **Updating is not a drop-in pull.** A newer upstream build lacks the Unraid
  patches and would regress them. `dev/update-45drives-disks.sh` fetches an
  upstream build as a starting point only; the Unraid patches must be re-applied
  and QA'd. Upstream also rewrote its architecture after v2.5.8 (→ the
  `houston-common` monorepo), so a version bump is a re-port, not a merge. See
  `dev/README.md`.

### Plugin

- Release process details: `RELEASING.md`
- Changelog management: `CHANGELOG.md` + `knope.toml`
- Test suite:
  - `php tests/run.php`
  - `php tests/remote_smoke.php` (non-45d / no-python smoke)
- Remote dev harness (SSH + rsync/scp):
  - `dev/remote-test-harness.sh --host root@<unraid-ip>`
  - details in `dev/README.md`
