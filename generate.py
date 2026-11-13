#!/usr/bin/env python3
"""Draw "Orange cat kneading a sunbeam on a windowsill" (ai-happy-01 v2).

Build-time generator: renders entry.png at 2048x2048 with Pillow, then
downsamples to 1024x1024 (LANCZOS). The grading runtime is stdlib-only,
so the entry program (main.py) just copies the finished PNG.
Everything here is drawn procedurally from scratch: no photos, no stock.
"""
import math
from PIL import Image, ImageDraw, ImageFilter

S = 2048  # working supersample size
OUT = 1024

# --- palette ---
CREAM_TOP = (255, 246, 222)
CREAM_BOT = (255, 224, 174)
SKY_TOP = (255, 237, 176)
SKY_BOT = (255, 176, 78)
SUN_CORE = (255, 205, 80)
SUN_GLOW = (255, 186, 90)
FRAME = (255, 253, 246)
FRAME_SHADOW = (232, 201, 160)
WOOD_TOP = (223, 169, 100)
WOOD_BOT = (181, 126, 62)
WOOD_EDGE = (138, 90, 38)
FLOOR_TOP = (201, 143, 82)
FLOOR_BOT = (169, 111, 53)
CAT = (242, 165, 74)
CAT_DARK = (217, 130, 43)
CAT_LIGHT = (255, 232, 194)
CAT_BELLY = (255, 223, 168)
OUTLINE = (107, 66, 38)
PINK = (232, 122, 122)
PINK_SOFT = (245, 163, 163)
GREEN = (78, 138, 90)
GREEN_LT = (107, 175, 116)
POT = (201, 111, 74)
BEAM = (255, 196, 96)


def vgrad(size, top, bottom):
    """Vertical linear gradient."""
    w, h = size
    base = Image.new("RGB", (1, h))
    px = base.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        px[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return base.resize((w, h))


def soft_shape(draw_fn, blur):
    """Draw onto a transparent layer, blur it, return the layer."""
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    draw_fn(d)
    return layer.filter(ImageFilter.GaussianBlur(blur))


def ellipse_arc_points(cx, cy, rx, ry, a0, a1, n=40):
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    return pts


def main():
    img = vgrad((S, S), CREAM_TOP, CREAM_BOT).convert("RGBA")
    d = ImageDraw.Draw(img)

    # ---------- window sky ----------
    win = (170, 130, 1878, 1470)
    # frame shadow: filled rect BEHIND the sky so only its border shows
    d0 = ImageDraw.Draw(img)
    d0.rectangle([win[0] - 26, win[1] - 26, win[2] + 26, win[3] + 26],
                 fill=FRAME_SHADOW + (255,))
    sky = vgrad((win[2] - win[0], win[3] - win[1]), SKY_TOP, SKY_BOT).convert("RGBA")
    img.paste(sky, (win[0], win[1]))

    # ---------- sunbeam (behind the sun, lands on the sill) ----------
    beam = soft_shape(
        lambda g: g.polygon(
            [(330, 150), (980, 150), (1420, 1500), (760, 1500)],
            fill=BEAM + (165,)),
        40)
    img.alpha_composite(beam)
    beam_core = soft_shape(
        lambda g: g.polygon(
            [(520, 150), (830, 150), (1180, 1500), (900, 1500)],
            fill=(255, 226, 150, 130)),
        25)
    img.alpha_composite(beam_core)
    d = ImageDraw.Draw(img)

    # ---------- sun + glow (on top of the beam so it stays bright) ----------
    sun_cx, sun_cy, sun_r = 560, 430, 205
    glow = soft_shape(
        lambda g: g.ellipse(
            [sun_cx - 380, sun_cy - 380, sun_cx + 380, sun_cy + 380],
            fill=SUN_GLOW + (190,)),
        110)
    img.alpha_composite(glow)
    d = ImageDraw.Draw(img)
    d.ellipse([sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r],
              fill=(255, 178, 58, 255))
    d.ellipse([sun_cx - sun_r + 40, sun_cy - sun_r + 40,
               sun_cx + sun_r - 40, sun_cy + sun_r - 40],
              fill=SUN_CORE + (255,))
    d.ellipse([sun_cx - sun_r + 95, sun_cy - sun_r + 95,
               sun_cx + sun_r - 95, sun_cy + sun_r - 95],
              fill=(255, 233, 170, 255))

    # ---------- window frame ----------
    d.rectangle(win, outline=FRAME + (255,), width=52)
    d.rectangle([1000, win[1], 1048, win[3]], fill=FRAME + (255,))
    d.rectangle([win[0], 776, win[2], 824], fill=FRAME + (255,))
    # frame highlight
    d.line([win[0] - 26, win[1] - 26, win[2] + 26, win[1] - 26],
           fill=(255, 255, 255, 255), width=10)

    # ---------- sill + floor ----------
    sill = vgrad((1828, 280), WOOD_TOP, WOOD_BOT).convert("RGBA")
    img.paste(sill, (110, 1470))
    d = ImageDraw.Draw(img)
    d.rectangle([110, 1470, 1938, 1484], fill=(255, 220, 160, 255))
    d.rectangle([110, 1736, 1938, 1750], fill=WOOD_EDGE + (255,))
    floor = vgrad((S, S - 1750), FLOOR_TOP, FLOOR_BOT).convert("RGBA")
    img.paste(floor, (0, 1750))
    d = ImageDraw.Draw(img)
    # soft shadow under the sill
    sh = soft_shape(
        lambda g: g.rectangle([110, 1750, 1938, 1830], fill=(90, 50, 20, 90)),
        30)
    img.alpha_composite(sh)
    d = ImageDraw.Draw(img)

    # ---------- bright sunlit patch on the sill (under the paws) ----------
    patch = soft_shape(
        lambda g: g.ellipse([820, 1420, 1380, 1640], fill=(255, 232, 160, 170)),
        45)
    img.alpha_composite(patch)
    d = ImageDraw.Draw(img)

    # ---------- potted plant, left of the sill ----------
    # pot
    d.polygon([(250, 1420), (470, 1420), (440, 1580), (280, 1580)], fill=POT + (255,))
    d.rectangle([235, 1396, 485, 1430], fill=(176, 92, 58, 255))
    d.ellipse([235, 1380, 485, 1422], fill=(214, 128, 88, 255))
    # leaves: elongated ellipses on their own layers, rotated
    for ang, lx, ly, ln in [(-38, 360, 1330, 330), (-14, 360, 1300, 380),
                            (12, 360, 1300, 380), (36, 360, 1330, 330),
                            (0, 360, 1270, 400)]:
        leaf = Image.new("RGBA", (200, 460), (0, 0, 0, 0))
        ld = ImageDraw.Draw(leaf)
        ld.ellipse([60, 20, 140, 440], fill=GREEN + (255,))
        ld.ellipse([78, 60, 122, 400], fill=GREEN_LT + (255,))
        leaf = leaf.rotate(ang, resample=Image.BICUBIC, expand=True)
        img.alpha_composite(leaf, (lx - leaf.width // 2, ly - leaf.height // 2))
    d = ImageDraw.Draw(img)
    # shadow under the pot
    psh = soft_shape(
        lambda g: g.ellipse([220, 1560, 500, 1620], fill=(90, 50, 20, 70)),
        18)
    img.alpha_composite(psh)
    d = ImageDraw.Draw(img)

    # ---------- cat shadow on the sill ----------
    csh = soft_shape(
        lambda g: g.ellipse([690, 1560, 1360, 1660], fill=(120, 70, 30, 80)),
        25)
    img.alpha_composite(csh)
    d = ImageDraw.Draw(img)

    # ---------- tail: thick curling arc, rings via stamped circles ----------
    tail_pts = ellipse_arc_points(1090, 1560, 330, 210, -70, 95, 26)
    for i, (x, y) in enumerate(tail_pts):
        col = CAT_DARK if (i // 4) % 2 else CAT
        d.ellipse([x - 52, y - 52, x + 52, y + 52], fill=col + (255,))
    # tail tip
    tx, ty = tail_pts[-1]
    d.ellipse([tx - 52, ty - 52, tx + 52, ty + 52], fill=CAT_LIGHT + (255,))

    # ---------- body: sitting pear shape + haunches ----------
    d.ellipse([694, 1000, 1354, 1660], fill=CAT + (255,))          # body
    d.ellipse([700, 1420, 980, 1660], fill=CAT + (255,))           # left haunch
    d.ellipse([1070, 1420, 1350, 1660], fill=CAT + (255,))         # right haunch
    d.ellipse([814, 1080, 1234, 1620], fill=CAT_BELLY + (255,))    # chest/belly
    # side stripes
    for (x0, y0, x1, y1) in [(730, 1180, 830, 1260), (1220, 1180, 1320, 1260),
                             (745, 1320, 845, 1400), (1205, 1320, 1305, 1400)]:
        d.line([x0, y0, x1, y1], fill=CAT_DARK + (255,), width=26)

    # ---------- front legs + kneading paws ----------
    # legs: thick rounded lines
    for lx in (930, 1120):
        d.line([lx, 1380, lx, 1560], fill=CAT + (255,), width=132)
        d.ellipse([lx - 66, 1330, lx + 66, 1462], fill=CAT + (255,))
    # paws on the sunlit patch; right paw slightly lifted (kneading)
    d.ellipse([864, 1548, 996, 1660], fill=CAT_LIGHT + (255,))     # left paw
    d.ellipse([1054, 1510, 1186, 1622], fill=CAT_LIGHT + (255,))   # right paw, lifted
    # toe beans on the lifted paw
    for bx, by in [(1090, 1590), (1120, 1600), (1150, 1590)]:
        d.ellipse([bx - 12, by - 16, bx + 12, by + 16], fill=PINK + (255,))
    # leg stripes
    d.line([884, 1460, 976, 1460], fill=CAT_DARK + (255,), width=18)
    d.line([1074, 1440, 1166, 1440], fill=CAT_DARK + (255,), width=18)

    # ---------- head ----------
    d.ellipse([724, 580, 1324, 1180], fill=CAT + (255,))           # head
    # ears
    d.polygon([(790, 700), (860, 520), (990, 660)], fill=CAT + (255,))
    d.polygon([(1060, 660), (1190, 520), (1260, 700)], fill=CAT + (255,))
    d.polygon([(828, 676), (872, 566), (946, 646)], fill=PINK_SOFT + (255,))
    d.polygon([(1104, 646), (1178, 566), (1222, 676)], fill=PINK_SOFT + (255,))
    # forehead stripes
    for (x0, y0, x1, y1) in [(970, 620, 970, 700), (1024, 610, 1024, 700),
                             (1078, 620, 1078, 700)]:
        d.line([x0, y0, x1, y1], fill=CAT_DARK + (255,), width=24)
    # cheek stripes
    for (x0, y0, x1, y1) in [(760, 980, 850, 1010), (1200, 1010, 1290, 980),
                             (770, 1060, 855, 1080), (1195, 1080, 1280, 1060)]:
        d.line([x0, y0, x1, y1], fill=CAT_DARK + (255,), width=18)
    # blush (soft)
    blush = soft_shape(
        lambda g: (g.ellipse([800, 1000, 920, 1070], fill=PINK_SOFT + (120,)),
                   g.ellipse([1130, 1000, 1250, 1070], fill=PINK_SOFT + (120,))),
        16)
    img.alpha_composite(blush)
    d = ImageDraw.Draw(img)
    # closed happy eyes: gentle ∩ arcs
    d.arc([872, 940, 992, 1060], 180, 360, fill=OUTLINE + (255,), width=22)
    d.arc([1058, 940, 1178, 1060], 180, 360, fill=OUTLINE + (255,), width=22)
    # nose: rounded triangle
    d.polygon([(1002, 1064), (1046, 1064), (1024, 1096)], fill=PINK + (255,))
    d.ellipse([1002, 1058, 1046, 1080], fill=PINK + (255,))
    # mouth: two small ∪ arcs under the nose
    d.arc([984, 1096, 1024, 1136], 0, 180, fill=OUTLINE + (255,), width=14)
    d.arc([1024, 1096, 1064, 1136], 0, 180, fill=OUTLINE + (255,), width=14)
    # whiskers
    for (x0, y0, x1, y1) in [(900, 1060, 730, 1010), (900, 1100, 720, 1100),
                             (900, 1140, 740, 1200), (1148, 1060, 1318, 1010),
                             (1148, 1100, 1328, 1100), (1148, 1140, 1308, 1200)]:
        d.line([x0, y0, x1, y1], fill=OUTLINE + (200,), width=8)

    # ---------- warm light wash over the cat's paws ----------
    wash = soft_shape(
        lambda g: g.ellipse([860, 1440, 1240, 1700], fill=(255, 220, 130, 70)),
        40)
    img.alpha_composite(wash)
    d = ImageDraw.Draw(img)

    # ---------- dust motes in the beam ----------
    import random
    random.seed(11)
    for _ in range(26):
        x = random.randint(480, 1250)
        y = random.randint(300, 1420)
        r = random.randint(4, 13)
        a = random.randint(90, 190)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 240, 200, a))

    # ---------- downsample + save ----------
    out = img.convert("RGB").resize((OUT, OUT), Image.LANCZOS)
    out.save("entry.png", optimize=True)
    print("saved entry.png", out.size)


if __name__ == "__main__":
    main()
