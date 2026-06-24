This directory contains vendored 45drives-disks frontend assets.

These assets are produced and maintained by 45Drives. We vendor their prebuilt
output and ship it as-is; we do not build or maintain it in this repo. To update
the disk-map UI, take a newer release snapshot from 45Drives rather than
rebuilding here. (Building from the upstream source under
`vendor/45drives/cockpit-hardware/` is not supported — it requires 45Drives'
private package registry and will fail with `401 Unauthorized`.)

- `45drives-disks/` holds a prebuilt Cockpit module release snapshot (v2.5.4-2).
- `45drives-disks/index.html` is patched to shim Cockpit APIs and route process
  calls to `/plugins/45d-drivemap/php/api.php` on Unraid.
- `drivemap.js` and `drivemap.css` remain as a lightweight fallback renderer.
