Drive Map tests

Run the generator + API parity checks:

```bash
php tests/run.php
```

The test harness uses fixtures under `tests/fixtures` and overrides generator/API
paths through environment variables, so it is safe to run on non-Unraid hosts.

Coverage includes:
- baseline map + API + ZFS fixture behavior
- SMART-derived field population via fixture JSON blobs
- row-order parity checks against vendored upstream `lsdev` templates
- server_info inference from alias layouts (for example `H16/Q30`)
- upstream template extraction helper: `tests/vendor_template.py`

Additional fixture files:
- `tests/fixtures/vdev_id_h16_q30.conf`
- `tests/fixtures/vdev_id_h16_s45.conf`
- `tests/fixtures/vdev_id_s45_full.conf`
