### AnyKernel3 untuk kernel-garnet
## Hanya mengganti kernel di partisi boot; ramdisk, vendor_boot, dan dtbo tidak disentuh.

properties() { '
kernel.string=kernel-garnet: ACK android12-5.10 + SukiSU Ultra + SUSFS
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

. tools/ak3-core.sh;

# split_boot/flash_boot: ganti kernel tanpa membongkar ramdisk.
split_boot;
flash_boot;
