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

- Release process details: `RELEASING.md`
- Changelog management: `CHANGELOG.md` + `knope.toml`
- Test suite:
  - `php tests/run.php`
  - `php tests/remote_smoke.php` (non-45d / no-python smoke)
- Remote dev harness (SSH + rsync/scp):
  - `dev/remote-test-harness.sh --host root@<unraid-ip>`
  - details in `dev/README.md`
