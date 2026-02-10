#!/usr/bin/env python3
import json
import subprocess as py_subprocess
import sys
import types
from copy import deepcopy
from importlib.machinery import SourceFileLoader


BASE_SERVER = {
    "Motherboard": {
        "Manufacturer": "Supermicro",
        "Product Name": "X11DPL-i",
        "Serial Number": "PARITY-TEST",
    },
    "HBA": [],
    "Hybrid": False,
    "Serial": "PARITY-TEST",
    "Model": "Parity-Model",
    "Alias Style": "STORINATOR",
    "Chassis Size": "S45",
    "VM": False,
    "Edit Mode": False,
    "OS NAME": "Rocky Linux",
    "OS VERSION_ID": "9",
}


def hba(model: str, bus: str):
    return {"Model": model, "Bus Address": bus}


CASES = {
    "h16_av15": {
        "server": {"Alias Style": "H16", "Chassis Size": "AV15", "HBA": [hba("SAS9305-24i", "0000:01:00.0")]},
    },
    "h16_q30": {
        "server": {"Alias Style": "H16", "Chassis Size": "Q30", "HBA": [hba("SAS9305-16i", "0000:01:00.0"), hba("SAS9305-24i", "0000:02:00.0")]},
    },
    "h16_s45": {
        "server": {
            "Alias Style": "H16",
            "Chassis Size": "S45",
            "HBA": [hba("SAS9305-16i", "0000:01:00.0"), hba("SAS9305-16i", "0000:02:00.0"), hba("SAS9305-24i", "0000:03:00.0")],
        },
    },
    "h16_xl60": {
        "server": {
            "Alias Style": "H16",
            "Chassis Size": "XL60",
            "HBA": [
                hba("SAS9305-16i", "0000:01:00.0"),
                hba("SAS9305-16i", "0000:02:00.0"),
                hba("SAS9305-16i", "0000:03:00.0"),
                hba("SAS9305-24i", "0000:04:00.0"),
            ],
        },
    },
    "h32_q30": {
        "server": {"Alias Style": "H32", "Chassis Size": "Q30", "HBA": [hba("SAS9305-24i", "0000:07:00.0"), hba("SAS9305-24i", "0000:08:00.0")]},
    },
    "h32_s45": {
        "server": {
            "Alias Style": "H32",
            "Chassis Size": "S45",
            "HBA": [hba("SAS9305-16i", "0000:07:00.0"), hba("SAS9305-24i", "0000:08:00.0"), hba("SAS9305-24i", "0000:09:00.0")],
        },
    },
    "h32_xl60": {
        "server": {
            "Alias Style": "H32",
            "Chassis Size": "XL60",
            "HBA": [
                hba("SAS9305-16i", "0000:07:00.0"),
                hba("SAS9305-16i", "0000:08:00.0"),
                hba("SAS9305-24i", "0000:09:00.0"),
                hba("SAS9305-24i", "0000:0a:00.0"),
            ],
        },
    },
    "storinator_av15": {
        "server": {"Alias Style": "STORINATOR", "Chassis Size": "AV15", "HBA": [hba("SAS9305-16i", "0000:01:00.0")]},
    },
    "storinator_av15_9600": {
        "server": {"Alias Style": "STORINATOR", "Chassis Size": "AV15", "HBA": [hba("9600-24i", "0000:21:00.0")]},
    },
    "storinator_q30": {
        "server": {"Alias Style": "STORINATOR", "Chassis Size": "Q30", "HBA": [hba("SAS9305-16i", "0000:01:00.0"), hba("SAS9305-16i", "0000:02:00.0")]},
    },
    "storinator_s45": {
        "server": {
            "Alias Style": "STORINATOR",
            "Chassis Size": "S45",
            "HBA": [hba("SAS9305-16i", "0000:01:00.0"), hba("SAS9305-16i", "0000:02:00.0"), hba("SAS9305-16i", "0000:03:00.0")],
        },
    },
    "storinator_xl60": {
        "server": {
            "Alias Style": "STORINATOR",
            "Chassis Size": "XL60",
            "HBA": [
                hba("SAS9305-16i", "0000:01:00.0"),
                hba("SAS9305-16i", "0000:02:00.0"),
                hba("SAS9305-16i", "0000:03:00.0"),
                hba("SAS9305-16i", "0000:04:00.0"),
            ],
        },
    },
    "storinator_f32": {
        "server": {"Alias Style": "STORINATOR", "Chassis Size": "F32", "HBA": [hba("SAS9305-16i", "0000:01:00.0"), hba("SAS9305-16i", "0000:02:00.0")]},
    },
    "c8": {
        "server": {"Alias Style": "STORINATOR", "Chassis Size": "C8", "HBA": [hba("SAS9305-16i", "0000:06:00.0")]},
    },
    "storinator_mi4_hba": {
        "server": {"Alias Style": "STORINATOR", "Chassis Size": "MI4", "HBA": [hba("SAS9305-16i", "0000:0b:00.0")]},
    },
    "storinator_mi4_nohba": {
        "server": {"Alias Style": "STORINATOR", "Chassis Size": "MI4", "HBA": [], "Motherboard": {"Manufacturer": "Supermicro", "Product Name": "H11SSL-i", "Serial Number": "PARITY-TEST"}},
        "mocks": {
            "lspci_lines": [
                "00:17.0 Intel Corporation SATA Controller",
            ]
        },
    },
    "storinator_mi4_fallback_centos7": {
        "server": {
            "Alias Style": "STORINATOR",
            "Chassis Size": "MI4",
            "HBA": [],
            "OS NAME": "CentOS Linux",
            "OS VERSION_ID": "7",
            "Motherboard": {"Manufacturer": "Supermicro", "Product Name": "X11DPL-i", "Serial Number": "PARITY-TEST"},
        },
        "mocks": {
            "lspci_lines": [
                "00:17.0 Intel Corporation SATA Controller",
            ]
        },
    },
    "storinatorubm_mi4_ubm_hba": {
        "server": {"Alias Style": "STORINATORUBM", "Chassis Size": "MI4_UBM", "HBA": [hba("SAS9305-16i", "0000:0c:00.0")]},
    },
    "storinatorubm_c8_ubm_hba": {
        "server": {"Alias Style": "STORINATORUBM", "Chassis Size": "C8_UBM", "HBA": [hba("SAS9305-16i", "0000:0d:00.0")]},
    },
    "storinatorubm_mi4_ubm_nohba": {
        "server": {"Alias Style": "STORINATORUBM", "Chassis Size": "MI4_UBM", "HBA": [], "Motherboard": {"Manufacturer": "Supermicro", "Product Name": "MS03-6L0-000", "Serial Number": "PARITY-TEST"}},
    },
    "homelab_hl15": {
        "server": {"Alias Style": "HOMELAB", "Chassis Size": "HL15", "HBA": [hba("SAS9305-16i", "0000:0e:00.0")]},
    },
    "homelab_hl15_beast": {
        "server": {
            "Alias Style": "HOMELAB",
            "Chassis Size": "HL15_BEAST",
            "HBA": [hba("SAS9305-24i", "0000:0f:00.0")],
            "Motherboard": {"Manufacturer": "ASUS", "Product Name": "ProArt X870E-CREATOR WIFI", "Serial Number": "PARITY-TEST"},
        },
    },
    "homelab_hl15_beast_romed8": {
        "server": {
            "Alias Style": "HOMELAB",
            "Chassis Size": "HL15_BEAST",
            "HBA": [hba("HBA 9400-16i", "0000:20:00.0")],
            "Motherboard": {"Manufacturer": "ASRockRack", "Product Name": "ROMED8-2T", "Serial Number": "PARITY-TEST"},
        },
        "mocks": {
            "sata_addresses": ["0000:48:00.0", "0000:49:00.0"],
            "sata_port_paths": {
                "0000:48:00.0": [
                    "/dev/disk/by-path/pci-0000:48:00.0-ata-5",
                    "/dev/disk/by-path/pci-0000:48:00.0-ata-6",
                ],
                "0000:49:00.0": [
                    "/dev/disk/by-path/pci-0000:49:00.0-ata-7",
                    "/dev/disk/by-path/pci-0000:49:00.0-ata-8",
                ],
            },
        },
    },
    "homelab_hl4": {
        "server": {"Alias Style": "HOMELAB", "Chassis Size": "HL4", "HBA": []},
        "mocks": {"sata_addresses": ["0000:10:00.0"]},
    },
    "homelab_hl8": {
        "server": {"Alias Style": "HOMELAB", "Chassis Size": "HL8", "HBA": []},
        "mocks": {"sata_addresses": ["0000:10:00.0", "0000:11:00.0"]},
    },
    "professional_pro15": {
        "server": {"Alias Style": "PROFESSIONAL", "Chassis Size": "PRO15", "HBA": [hba("SAS9305-16i", "0000:12:00.0")]},
    },
    "professional_pro4": {
        "server": {"Alias Style": "PROFESSIONAL", "Chassis Size": "PRO4", "HBA": []},
    },
    "professional_pro8": {
        "server": {"Alias Style": "PROFESSIONAL", "Chassis Size": "PRO8", "HBA": []},
    },
    "studio8": {
        "server": {"Alias Style": "STUDIO", "Chassis Size": "STUDIO8", "HBA": []},
    },
    "stornado_av15": {
        "server": {"Alias Style": "STORNADO", "Chassis Size": "AV15", "HBA": [hba("SAS9305-16i", "0000:13:00.0"), hba("SAS9305-16i", "0000:14:00.0")]},
    },
    "stornado_f32": {
        "server": {"Alias Style": "STORNADO", "Chassis Size": "F32", "HBA": [hba("SAS9305-16i", "0000:13:00.0"), hba("SAS9305-16i", "0000:14:00.0")]},
    },
    "2ustornado_2u": {
        "server": {"Alias Style": "2USTORNADO", "Chassis Size": "2U", "HBA": [hba("SAS9305-16i", "0000:15:00.0"), hba("SAS9305-16i", "0000:16:00.0")]},
    },
    "f2_f2": {
        "server": {
            "Alias Style": "F2STORNADO",
            "Chassis Size": "F2",
            "HBA": [hba("SAS9305-16i", "0000:17:00.0"), hba("SAS9305-16i", "0000:18:00.0"), hba("SAS9305-16i", "0000:19:00.0"), hba("SAS9305-16i", "0000:1a:00.0")],
        },
    },
    "f2_vm8": {
        "server": {"Alias Style": "F2STORNADO", "Chassis Size": "VM8", "HBA": [hba("SAS9305-16i", "0000:17:00.0")]},
    },
    "f2_vm16": {
        "server": {"Alias Style": "F2STORNADO", "Chassis Size": "VM16", "HBA": [hba("SAS9305-16i", "0000:17:00.0"), hba("SAS9305-16i", "0000:18:00.0")]},
    },
    "f2_vm32": {
        "server": {"Alias Style": "F2STORNADO", "Chassis Size": "VM32", "HBA": [hba("SAS9305-16i", "0000:17:00.0"), hba("SAS9305-16i", "0000:18:00.0"), hba("SAS9305-16i", "0000:19:00.0")]},
    },
    "av15_base": {
        "server": {"Alias Style": "AV15-BASE", "Chassis Size": "AV15", "HBA": []},
        "mocks": {
            "lspci_lines": [
                "00:17.0 Intel Corporation SATA Controller",
                "05:00.0 Broadcom / LSI SAS3008 PCI-Express Fusion-MPT SAS-3",
            ]
        },
    },
    "av15_base_centos7": {
        "server": {
            "Alias Style": "AV15-BASE",
            "Chassis Size": "AV15",
            "HBA": [],
            "OS NAME": "CentOS Linux",
            "OS VERSION_ID": "7",
        },
        "mocks": {
            "lspci_lines": [
                "00:17.0 Intel Corporation SATA Controller",
                "05:00.0 Broadcom / LSI SAS3008 PCI-Express Fusion-MPT SAS-3",
            ]
        },
    },
    "destroyinator_av15": {
        "server": {
            "Alias Style": "DESTROYINATOR",
            "Chassis Size": "AV15",
            "HBA": [hba("SAS9305-16i", "0000:1b:00.0")],
            "Motherboard": {"Manufacturer": "Giga Computing", "Product Name": "MS73-HB0", "Serial Number": "PARITY-TEST"},
        },
    },
    "destroyinator_q30": {
        "server": {
            "Alias Style": "DESTROYINATOR",
            "Chassis Size": "Q30",
            "HBA": [hba("SAS9305-16i", "0000:1b:00.0"), hba("SAS9305-16i", "0000:1c:00.0")],
            "Motherboard": {"Manufacturer": "Giga Computing", "Product Name": "MS73-HB0", "Serial Number": "PARITY-TEST"},
        },
    },
    "destroyinator_s45": {
        "server": {
            "Alias Style": "DESTROYINATOR",
            "Chassis Size": "S45",
            "HBA": [hba("SAS9305-16i", "0000:1b:00.0"), hba("SAS9305-16i", "0000:1c:00.0"), hba("SAS9305-16i", "0000:1d:00.0")],
            "Motherboard": {"Manufacturer": "Giga Computing", "Product Name": "MS73-HB0", "Serial Number": "PARITY-TEST"},
        },
    },
    "destroyinator_xl60": {
        "server": {
            "Alias Style": "DESTROYINATOR",
            "Chassis Size": "XL60",
            "HBA": [hba("SAS9305-16i", "0000:1b:00.0"), hba("SAS9305-16i", "0000:1c:00.0"), hba("SAS9305-16i", "0000:1d:00.0"), hba("SAS9305-16i", "0000:1e:00.0")],
            "Motherboard": {"Manufacturer": "Giga Computing", "Product Name": "MS73-HB0", "Serial Number": "PARITY-TEST"},
        },
    },
    "f8_x1": {
        "server": {"Alias Style": "F8", "Chassis Size": "F8X1", "HBA": [hba("SAS9305-24i", "0000:05:00.0")]},
    },
    "f8_x2": {
        "server": {"Alias Style": "F8", "Chassis Size": "F8X2", "HBA": [hba("SAS9305-24i", "0000:05:00.0"), hba("SAS9305-24i", "0000:06:00.0")]},
    },
    "f8_x3": {
        "server": {
            "Alias Style": "F8",
            "Chassis Size": "F8X3",
            "HBA": [hba("SAS9305-24i", "0000:05:00.0"), hba("SAS9305-24i", "0000:06:00.0"), hba("SAS9305-24i", "0000:07:00.0")],
        },
    },
    "storinator_av15_9361": {
        "server": {"Alias Style": "STORINATOR", "Chassis Size": "AV15", "HBA": [hba("9361-16i", "0000:31:00.0")]},
        "mocks": {
            "hwraid_map": {
                "0000:31:00.0": [str(200 + i) for i in range(24)],
            }
        },
    },
    "h32_q30_9361_hybrid": {
        "server": {
            "Alias Style": "H32",
            "Chassis Size": "Q30",
            "HBA": [hba("9361-24i", "0000:32:00.0"), hba("SAS9305-24i", "0000:33:00.0")],
        },
        "mocks": {
            "hwraid_map": {
                "0000:32:00.0": [str(300 + i) for i in range(24)],
            }
        },
    },
    "c8_9361": {
        "server": {"Alias Style": "STORINATOR", "Chassis Size": "C8", "HBA": [hba("9361-16i", "0000:34:00.0")]},
        "mocks": {
            "hwraid_map": {
                "0000:34:00.0": [str(400 + i) for i in range(24)],
            }
        },
    },
    "f8_x1_9361": {
        "server": {"Alias Style": "F8", "Chassis Size": "F8X1", "HBA": [hba("9361-24i", "0000:35:00.0")]},
        "mocks": {
            "hwraid_map": {
                "0000:35:00.0": [str(500 + i) for i in range(24)],
            }
        },
    },
    "bypath_vm2": {
        "server": {
            "Alias Style": "BYPATH",
            "Chassis Size": "VM2",
            "HBA": [],
            "Motherboard": {"Manufacturer": "Supermicro", "Product Name": "ME03-CE0-000", "Serial Number": "PARITY-TEST"},
        },
    },
    "unknown_qmark": {
        "server": {"Alias Style": "?", "Chassis Size": "?", "HBA": []},
    },
}


def usage() -> int:
    print(
        f"Usage: {sys.argv[0]} <vendor_dmap_path> <case_name> [--text|--full|--server|--local-env]\n"
        f"   or: {sys.argv[0]} --list",
        file=sys.stderr,
    )
    return 2


def case_names():
    return sorted(CASES.keys())


def case_spec(case_name: str):
    spec = CASES.get(case_name)
    if spec is None:
        return None
    return deepcopy(spec)


def build_server(case_name: str):
    spec = case_spec(case_name)
    if spec is None:
        return None
    server = deepcopy(BASE_SERVER)
    server.update(spec.get("server", {}))
    return server


def local_env(case_name: str):
    spec = case_spec(case_name)
    if spec is None:
        return None
    mocks = spec.get("mocks", {})
    env = {}
    sata_addrs = mocks.get("sata_addresses")
    if isinstance(sata_addrs, list) and sata_addrs:
        env["DRIVEMAP_DMAP_SATA_ADDRS"] = ",".join(str(x) for x in sata_addrs)
    lspci_lines = mocks.get("lspci_lines")
    if isinstance(lspci_lines, list) and lspci_lines:
        env["DRIVEMAP_DMAP_LSPCI_JSON"] = json.dumps([str(x) for x in lspci_lines])
    sata_paths = mocks.get("sata_port_paths")
    if isinstance(sata_paths, dict) and sata_paths:
        env["DRIVEMAP_DMAP_SATA_PATHS_JSON"] = json.dumps(sata_paths)
    hwraid_map = mocks.get("hwraid_map")
    if isinstance(hwraid_map, dict) and hwraid_map:
        env["DRIVEMAP_DMAP_HWRAID_JSON"] = json.dumps(hwraid_map)
    return env


def load_vendor_dmap(path: str):
    loader = SourceFileLoader("vendor_dmap_reference", path)
    module = types.ModuleType(loader.name)
    loader.exec_module(module)
    module.g_quiet = True
    return module


def apply_vendor_mocks(module, case_name: str):
    spec = case_spec(case_name)
    if spec is None:
        return
    mocks = spec.get("mocks", {})

    sata_addrs = mocks.get("sata_addresses")
    if isinstance(sata_addrs, list):
        module.get_sata_pci_addresses = lambda: list(sata_addrs)

    sata_paths = mocks.get("sata_port_paths")
    if isinstance(sata_paths, dict):
        def fake_list_ata_paths(addr):
            value = sata_paths.get(addr, [])
            if isinstance(value, list):
                return [str(x) for x in value]
            return []
        module.list_ata_port_paths = fake_list_ata_paths

    lspci_lines = mocks.get("lspci_lines")
    if isinstance(lspci_lines, list):
        real_popen = module.subprocess.Popen

        class FakeProcess:
            def __init__(self, lines):
                self.stdout = iter(lines)

        def patched_popen(args, *popen_args, **popen_kwargs):
            argv = args if isinstance(args, list) else [str(args)]
            if argv and argv[0] == "lspci":
                return FakeProcess(list(lspci_lines))
            return real_popen(args, *popen_args, **popen_kwargs)

        module.subprocess.Popen = patched_popen

    hwraid = mocks.get("hwraid_map")
    if isinstance(hwraid, dict):
        def fake_hwraid_map(hba_obj, _server):
            if not isinstance(hba_obj, dict):
                return [99] * 24
            bus = str(hba_obj.get("Bus Address", ""))
            model = str(hba_obj.get("Model", ""))
            raw = hwraid.get(bus)
            if isinstance(raw, list):
                return [str(x) for x in raw]
            if model in ("9361-16i", "9361-24i"):
                return [99] * 24
            return [99] * 24
        module.hwraid_map = fake_hwraid_map


def alias_lines(text: str):
    return [line for line in text.splitlines() if line.startswith("alias ")]


def run_case(vendor_dmap_path: str, case_name: str):
    module = load_vendor_dmap(vendor_dmap_path)
    apply_vendor_mocks(module, case_name)
    server = build_server(case_name)
    if server is None:
        raise KeyError(case_name)
    generated = module.create_vdev_id(server)
    if generated is not None and not isinstance(generated, str):
        raise RuntimeError("create_vdev_id returned non-string output")
    return generated


def run_case_aliases(vendor_dmap_path: str, case_name: str):
    generated = run_case(vendor_dmap_path, case_name)
    if generated is None:
        return []
    return alias_lines(generated)


def main() -> int:
    if len(sys.argv) == 2 and sys.argv[1] == "--list":
        print(json.dumps(case_names()))
        return 0

    if len(sys.argv) < 3 or len(sys.argv) > 4:
        return usage()

    vendor_dmap_path = sys.argv[1]
    case_name = sys.argv[2]
    mode = sys.argv[3] if len(sys.argv) == 4 else ""

    if case_name not in CASES:
        print(f"error: unknown case '{case_name}'", file=sys.stderr)
        return 2

    if mode == "--server":
        print(json.dumps(build_server(case_name)))
        return 0
    if mode == "--local-env":
        print(json.dumps(local_env(case_name)))
        return 0

    try:
        generated = run_case(vendor_dmap_path, case_name)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if mode == "--full":
        print(json.dumps(generated))
        return 0

    lines = alias_lines(generated) if isinstance(generated, str) else []
    if mode == "--text":
        sys.stdout.write("\n".join(lines))
        if lines:
            sys.stdout.write("\n")
    else:
        print(json.dumps(lines))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
