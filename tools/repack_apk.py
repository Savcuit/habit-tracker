"""Repackage the habit tracker APK: swap the web page, keep everything else.

The manifest, resources and compiled Java were produced earlier with aapt2 and
d8; only assets/index.html changes. Android wants resources.arsc stored
uncompressed and aligned to 4 bytes, so the archive is written by hand with the
same rules zipalign applies.
"""

import os
import sys
import zipfile
import zlib

SRC_APK = "/tmp/HabitTracker.apk"
NEW_HTML = "/home/savcuit/repos/habit-tracker/android/assets/index.html"
OUT = "/tmp/HabitTracker-new.apk"

ALIGN_RULES = ((b".so", 4096), (b"resources.arsc", 4))


def align_for(name: str) -> int:
    raw = name.encode()
    for suffix, value in ALIGN_RULES:
        if raw.endswith(suffix):
            return value
    return 0


def extra_field_for(current: int, name_len: int, align: int) -> bytes:
    """Padding so that the entry's data begins on an `align` boundary."""
    base = current + 30 + name_len
    pad = (-base) % align
    if pad == 0:
        return b""
    if pad < 4:
        pad += align
    body = pad - 4
    return b"\x00\x00" + body.to_bytes(2, "little") + b"\x00" * body


def main() -> int:
    if not os.path.exists(SRC_APK):
        print("source apk missing")
        return 1

    with zipfile.ZipFile(SRC_APK) as src:
        entries = [(i.filename, src.read(i.filename)) for i in src.infolist()]

    new_html = open(NEW_HTML, "rb").read()
    replaced = False
    kept = []
    for name, data in entries:
        if name.startswith("META-INF/"):
            continue                     # old signature; apksigner writes new ones
        if name == "assets/index.html":
            data = new_html
            replaced = True
        kept.append((name, data))

    if not replaced:
        print("assets/index.html missing from the source apk")
        return 1

    kept.sort(key=lambda pair: (align_for(pair[0]) == 0, pair[0]))

    with open(OUT, "wb") as fh:
        central = []
        for name, data in kept:
            align = align_for(name)
            name_b = name.encode()
            crc = zlib.crc32(data) & 0xFFFFFFFF

            if align:
                method, payload = zipfile.ZIP_STORED, data
            else:
                method = zipfile.ZIP_DEFLATED
                comp = zlib.compressobj(6, zlib.DEFLATED, -15)
                payload = comp.compress(data) + comp.flush()

            extra = extra_field_for(fh.tell(), len(name_b), align) if align else b""
            offset = fh.tell()

            fh.write(b"PK\x03\x04")
            fh.write((20).to_bytes(2, "little"))
            fh.write((0).to_bytes(2, "little"))
            fh.write(method.to_bytes(2, "little"))
            fh.write((0).to_bytes(2, "little"))
            fh.write((0x21).to_bytes(2, "little"))
            fh.write(crc.to_bytes(4, "little"))
            fh.write(len(payload).to_bytes(4, "little"))
            fh.write(len(data).to_bytes(4, "little"))
            fh.write(len(name_b).to_bytes(2, "little"))
            fh.write(len(extra).to_bytes(2, "little"))
            fh.write(name_b)
            fh.write(extra)
            fh.write(payload)

            central.append((name_b, method, crc, len(payload), len(data), offset))

        cd_start = fh.tell()
        for name_b, method, crc, csize, usize, offset in central:
            fh.write(b"PK\x01\x02")
            fh.write((20).to_bytes(2, "little"))
            fh.write((20).to_bytes(2, "little"))
            fh.write((0).to_bytes(2, "little"))
            fh.write(method.to_bytes(2, "little"))
            fh.write((0).to_bytes(2, "little"))
            fh.write((0x21).to_bytes(2, "little"))
            fh.write(crc.to_bytes(4, "little"))
            fh.write(csize.to_bytes(4, "little"))
            fh.write(usize.to_bytes(4, "little"))
            fh.write(len(name_b).to_bytes(2, "little"))
            fh.write((0).to_bytes(2, "little"))      # no extra in central record
            fh.write((0).to_bytes(2, "little"))
            fh.write((0).to_bytes(2, "little"))
            fh.write((0).to_bytes(2, "little"))
            fh.write((0).to_bytes(4, "little"))
            fh.write(offset.to_bytes(4, "little"))
            fh.write(name_b)

        cd_size = fh.tell() - cd_start
        fh.write(b"PK\x05\x06")
        fh.write((0).to_bytes(2, "little"))
        fh.write((0).to_bytes(2, "little"))
        fh.write(len(central).to_bytes(2, "little"))
        fh.write(len(central).to_bytes(2, "little"))
        fh.write(cd_size.to_bytes(4, "little"))
        fh.write(cd_start.to_bytes(4, "little"))
        fh.write((0).to_bytes(2, "little"))

    print("wrote", OUT, os.path.getsize(OUT), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
