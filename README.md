# Equinox Kernel

A GKI kernel for the **Redmi Note 13 Pro 5G / POCO X6 5G** (`garnet`, Snapdragon 7s Gen 2), built straight from Google's Android Common Kernel with root and root hiding included.

Balanced by design: it stays close to the stock kernel and changes only what is needed.

## What's inside

| Area | What you get |
|---|---|
| Base | Android Common Kernel `android12-5.10`, rebuilt whenever Google updates it |
| Root | [SukiSU Ultra](https://github.com/SukiSU-Ultra/SukiSU-Ultra), built in, with KPM |
| Root hiding | [SUSFS](https://gitlab.com/simonpunk/susfs4ksu) |
| Network | TCP BBR as the default congestion control |
| Display | HyperOS flicker fix |
| Storage | ADIOS I/O scheduler, optional (see below) |
| Toolchain | Official AOSP clang `r416183b`, with CFI, SCS and ThinLTO enabled |

Only the kernel image inside `boot` is replaced. Vendor modules, `vendor_boot` and `dtbo` stay stock.

## Compatibility

- **Device:** `garnet` only. The installer refuses other devices.
- **Tested ROM:** HyperOS 3.0.315.0 CN (Android 16).
- **Other HyperOS versions on garnet** (1.x, 2.x, Global or CN, ports) use the same kernel interface (`android12-5.10`, KMI generation 9), so Equinox should boot there too. This is untested. If you try it, please open an issue with your ROM version and whether it booted.
- **Bootloader:** must be unlocked.

## Install

1. Back up your current `boot` partition.
2. Download the latest release that is **not** marked `[UNTESTED]` or `[DO NOT FLASH]`.
3. Flash `Equinox-garnet-<version>-AnyKernel3.zip` from a custom recovery, then reboot.
4. Install the SukiSU Ultra manager.
5. Optional: flash `ksu_module_susfs.zip` from the manager to configure SUSFS.

The first boot on HyperOS can take a couple of minutes.

### Going back

Flash your `boot` backup from fastboot:

```
fastboot flash boot_a boot_a.img
```

Use `boot_b` if your active slot is `b`.

## Release labels

| Label | Meaning |
|---|---|
| *(none)* | Booted and checked on a real device |
| `[UNTESTED]` | Compiled, not yet booted on a device |
| `[DO NOT FLASH]` | Known to fail on a device. Kept for reference only |

## ADIOS I/O scheduler

Equinox ships ADIOS v3.3.0 with a fix for kernel 5.10. The upstream code reads `data->hctx` in `limit_depth`, which 5.10 has not set yet at that point, so the kernel crashes on the first write. In our tests on garnet the fixed version wrote about 15-40% faster than `bfq`; read speed was about the same.

HyperOS selects `bfq` at boot, so ADIOS stays unused until you switch to it. From a root shell:

```
for q in /sys/block/sd*/queue; do echo adios > $q/scheduler; done
```

This lasts until reboot. To keep it, run the same line from a boot script such as `/data/adb/service.d/adios.sh` once `sys.boot_completed` is `1`.

## Kernel name and root detection

The kernel reports itself as `5.10.x-android12-9-Equinox-r<build>`. Some apps look at this string. If you need it hidden, SUSFS can spoof it with its `set_uname` feature.

## Build it yourself

Everything is built by one GitHub Actions workflow, `.github/workflows/build.yml`:

1. Fork this repository.
2. Open the **Actions** tab and run **Build Equinox Kernel**.
3. The build is published as a release in your fork, labelled `[UNTESTED]`.

The workflow also runs weekly and builds only when the kernel, SukiSU Ultra or SUSFS has new commits.

Patches live in `patches/`. `patches/SOURCE.txt` records where each one comes from and which changes were tried and removed.

## Disclaimer

You flash this at your own risk. A bad kernel can leave the phone unable to boot until you restore `boot` from fastboot. Keep a backup and a PC with fastboot at hand.

## Credits

- Google, for the Android Common Kernel
- The SukiSU Ultra and KernelSU developers
- simonpunk, for SUSFS
- osm0sis, for AnyKernel3
- Pzqqt and ramabondanp, for the HyperOS display fix

## License

The kernel and the patches in this repository are licensed under GPL-2.0. Each release lists the exact source commits it was built from.
