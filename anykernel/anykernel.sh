### AnyKernel3 for Equinox Kernel
## Hanya mengganti kernel di partisi boot; ramdisk, vendor_boot, dan dtbo tidak disentuh.
## Banner dan detail build tampil dari file `banner` dan `version` di root zip.

properties() { '
kernel.string=Equinox Kernel for Redmi Note 13 Pro 5G / POCO X6 5G
do.devicecheck=1
do.modules=0
do.systemless=1
do.cleanup=1
do.cleanuponabort=0
device.name1=garnet
supported.versions=
supported.patchlevels=
supported.vendorpatchlevels=
'; }

BLOCK=boot;
IS_SLOT_DEVICE=1;
RAMDISK_COMPRESSION=auto;
PATCH_VBMETA_FLAG=auto;

# AnyKernel3 mencari slot aktif lewat getprop, lalu /proc/cmdline. Di garnet dengan ROM
# Android 16, getprop mati di recovery setelah AK3 memasang /system milik ROM (apex runtime
# gagal di-mount), dan slot hanya tercatat di /proc/bootconfig. Tanpa cadangan ini instalasi
# berhenti dengan "Unable to determine active slot".
getprop() {
  local val="$(command getprop "$@" 2>/dev/null)";
  if [ -z "$val" ] && [ "$1" = ro.boot.slot_suffix ]; then
    val="$(sed -n 's/^androidboot\.slot_suffix *= *"\(.*\)"/\1/p' /proc/bootconfig 2>/dev/null)";
  fi;
  echo "$val";
}

. tools/ak3-core.sh;

ui_print " ";
ui_print "  ----------------------------------------";
ui_print "   Installing Equinox";
ui_print "  ----------------------------------------";
ui_print " ";
ui_print "  [1/2] Reading your current boot image...";
# split_boot/flash_boot: ganti kernel tanpa membongkar ramdisk.
split_boot;

ui_print "  [2/2] Flashing the Equinox kernel...";
flash_boot;

ui_print " ";
ui_print "  ----------------------------------------";
ui_print "   Equinox is installed.";
ui_print "  ----------------------------------------";
ui_print " ";
ui_print "  What's inside:";
ui_print "   - Root    : SukiSU Ultra with KPM";
ui_print "   - Hiding  : SUSFS";
ui_print "   - Network : TCP BBR";
ui_print "   - Storage : ADIOS I/O scheduler";
ui_print "   - Display : HyperOS flicker fix";
ui_print " ";
ui_print "  Next steps:";
ui_print "   1. Reboot your device.";
ui_print "   2. Install the SukiSU Ultra manager.";
ui_print "   3. Flash the SUSFS module from the manager.";
ui_print " ";
ui_print "  Only the kernel was replaced. Your data,";
ui_print "  vendor_boot and dtbo were not touched.";
ui_print " ";
