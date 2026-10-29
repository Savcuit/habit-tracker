"""Generate the app icon (assets/icon.ico) without any image library."""
import math, struct, zlib, os

S = 256
BG1 = (10, 17, 32)
BG2 = (16, 26, 46)
CYAN = (34, 211, 238)
DARK = (6, 19, 31)

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def pixel(x, y):
    cx = cy = S / 2
    dx, dy = x - cx, y - cy
    r = math.hypot(dx, dy)

    # rounded-square background with a soft vertical gradient
    base = lerp(BG1, BG2, y / S)
    if r > 104:
        return (0, 0, 0, 0)

    # outer ring
    if 84 <= r <= 100:
        return CYAN + (255,)
    # inner subtle ring
    if 78 <= r < 82:
        return (24, 60, 82, 255)

    # check mark: two thick strokes inside the circle
    def seg_dist(px, py, ax, ay, bx, by):
        vx, vy = bx - ax, by - ay
        wx, wy = px - ax, py - ay
        t = max(0.0, min(1.0, (wx * vx + wy * vy) / (vx * vx + vy * vy)))
        return math.hypot(px - (ax + t * vx), py - (ay + t * vy))

    d1 = seg_dist(x, y, 88, 128, 118, 158)
    d2 = seg_dist(x, y, 118, 158, 172, 96)
    if d1 <= 9 or d2 <= 9:
        return CYAN + (255,)

    return base + (255,)


def build_png():
    rows = []
    for y in range(S):
        row = bytearray(b"\x00")
        for x in range(S):
            row += bytes(pixel(x, y))
        rows.append(bytes(row))
    raw = b"".join(rows)

    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", S, S, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def main():
    png = build_png()
    os.makedirs("assets", exist_ok=True)
    with open("assets/icon.png", "wb") as fh:
        fh.write(png)

    # ICO container holding a single 256x256 PNG image
    header = struct.pack("<HHH", 0, 1, 1)
    entry = struct.pack("<BBBBHHII", 0, 0, 0, 0, 1, 32, len(png), 22)
    with open("assets/icon.ico", "wb") as fh:
        fh.write(header + entry + png)
    print("wrote assets/icon.png and assets/icon.ico",
          os.path.getsize("assets/icon.ico"), "bytes")


if __name__ == "__main__":
    main()
