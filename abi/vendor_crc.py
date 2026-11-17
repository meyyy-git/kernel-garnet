"""Ambil daftar (simbol, CRC) yang diminta modul vendor dari vendor_boot.img.
Keluaran: baris "0xCRC simbol" terurut, untuk dibandingkan dengan vmlinux.symvers hasil build."""
import gzip
import struct
import sys

import lz4.block


def ramdisk(img):
    assert img[:8] == b"VNDRBOOT", "bukan vendor_boot"
    ver, page = struct.unpack_from("<II", img, 8)
    rd_size = struct.unpack_from("<I", img, 24)[0]
    hdr_size = struct.unpack_from("<I", img, 28 + 2048 + 4 + 16)[0]
    off = -(-hdr_size // page) * page
    return img[off:off + rd_size]


def decompress(d):
    if d[:2] == b"\x1f\x8b":
        return gzip.decompress(d)
    assert d[:4] == b"\x02\x21\x4c\x18", f"kompresi tak dikenal {d[:4].hex()}"
    out, p = [], 4
    while p + 4 <= len(d):
        n = struct.unpack_from("<I", d, p)[0]
        if n == 0x184C2102:  # magic berulang = frame berikutnya
            p += 4
            continue
        if n == 0 or p + 4 + n > len(d):
            break
        out.append(lz4.block.decompress(d[p + 4:p + 4 + n], uncompressed_size=8 << 20))
        p += 4 + n
    return b"".join(out)


def cpio_files(d):
    p = 0
    while p + 110 <= len(d):
        if d[p:p + 6] != b"070701":
            # beberapa ramdisk digabung berurutan, dipisah nol
            nxt = d.find(b"070701", p)
            if nxt < 0:
                return
            p = nxt
            continue
        f = [int(d[p + 6 + i * 8:p + 14 + i * 8], 16) for i in range(13)]
        size, nlen = f[6], f[11]
        name = d[p + 110:p + 110 + nlen - 1].decode(errors="replace")
        s = (p + 110 + nlen + 3) & ~3
        yield name, d[s:s + size]
        p = (s + size + 3) & ~3


def exports(ko):
    """Nama simbol yang diekspor modul ini sendiri (bukan dari vmlinux)."""
    if ko[:4] != b"\x7fELF":
        return set()
    shoff = struct.unpack_from("<Q", ko, 0x28)[0]
    shentsize, shnum, shstrndx = struct.unpack_from("<HHH", ko, 0x3A)
    sh = [struct.unpack_from("<IIQQQQIIQQ", ko, shoff + i * shentsize) for i in range(shnum)]
    stro = sh[shstrndx][4]
    for s in sh:
        if ko[stro + s[0]:ko.index(b"\0", stro + s[0])] == b"__ksymtab_strings":
            return {x.decode() for x in ko[s[4]:s[4] + s[5]].split(b"\0") if x}
    return set()


def versions(ko):
    if ko[:4] != b"\x7fELF":
        return []
    shoff = struct.unpack_from("<Q", ko, 0x28)[0]
    shentsize, shnum, shstrndx = struct.unpack_from("<HHH", ko, 0x3A)
    sh = [struct.unpack_from("<IIQQQQIIQQ", ko, shoff + i * shentsize) for i in range(shnum)]
    stro = sh[shstrndx][4]
    for s in sh:
        name = ko[stro + s[0]:ko.index(b"\0", stro + s[0])]
        if name == b"__versions":
            d = ko[s[4]:s[4] + s[5]]
            return [(struct.unpack_from("<Q", d, i)[0], d[i + 8:i + 64].split(b"\0")[0].decode())
                    for i in range(0, len(d), 64)]
    return []


img = open(sys.argv[1], "rb").read()
need, nmod, own = {}, 0, set()
for name, data in cpio_files(decompress(ramdisk(img))):
    if not name.endswith(".ko"):
        continue
    nmod += 1
    own |= exports(data)
    for crc, sym in versions(data):
        need.setdefault(sym, set()).add(crc)
total = len(need)
need = {s: c for s, c in need.items() if s not in own}
print(f"simbol antar-modul vendor (dibuang): {total - len(need)}", file=sys.stderr)
bad = {s for s, c in need.items() if len(c) > 1}
print(f"modul: {nmod}, simbol: {len(need)}, simbol dgn CRC ganda: {len(bad)}", file=sys.stderr)
for sym in sorted(need):
    for crc in sorted(need[sym]):
        print(f"0x{crc:08x} {sym}")
