#!/usr/bin/env python3
"""Build-time generator for the news-image-20261117 entry.
Draws three variant front-page images (1024x1024) with PIL, all artwork
drawn programmatically here - no copied photos. Deterministic: no
randomness, fixed coordinates. Only the chosen variant's PNG is shipped;
main.py in the repo simply copies it to /output/entry.png.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
FD = "/usr/share/fonts/truetype/dejavu/"
SERIF = FD + "DejaVuSerif-Bold.ttf"
SERIF_R = FD + "DejaVuSerif.ttf"
SANS = FD + "DejaVuSans-Bold.ttf"
SANS_R = FD + "DejaVuSans.ttf"

PAPER = (247, 243, 234)
INK = (17, 24, 39)
NAVY = (30, 58, 95)
RED = (185, 28, 28)
SEA = (38, 84, 110)
SEA_D = (22, 55, 78)
SKY = (232, 222, 200)
ORANGE = (234, 120, 40)
GOLD = (212, 160, 40)
GREY = (90, 96, 104)
WHITE = (255, 255, 255)
CREAM = (255, 251, 240)


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, f, max_w):
    """Greedy word wrap returning list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(d, x, y, max_w, text, f, fill=INK, leading=None, align="left"):
    lines = wrap(d, text, f, max_w)
    lh = leading or int(f.size * 1.15)
    for ln in lines:
        if align == "center":
            d.text((x + (max_w - d.textlength(ln, font=f)) / 2, y), ln, font=f, fill=fill)
        else:
            d.text((x, y), ln, font=f, fill=fill)
        y += lh
    return y


def rule(d, x, y, w, color=INK, width=3):
    d.line([(x, y), (x + w, y)], fill=color, width=width)


def tag(d, x, y, label, f, bg=RED, fg=WHITE):
    tw = d.textlength(label, font=f)
    pad = 10
    d.rounded_rectangle([x, y, x + tw + pad * 2, y + f.size + 14], radius=4, fill=bg)
    d.text((x + pad, y + 7), label, font=f, fill=fg)
    return x + tw + pad * 2


# ---------------------------------------------------------------- scenes
def bridge_scene(d, x, y, w, h):
    """Kerch Bridge: dusk sky, sea, long bridge with a collapsed span."""
    d.rectangle([x, y, x + w, y + h], fill=(226, 205, 170))
    # low warm horizon band
    d.rectangle([x, y + h * 0.30, x + w, y + h * 0.52], fill=(233, 214, 180))
    # distant shore
    d.rectangle([x, y + h * 0.52, x + w, y + h * 0.58], fill=(120, 118, 96))
    # sea
    d.rectangle([x, y + h * 0.58, x + w, y + h], fill=SEA)
    for i in range(7):
        yy = y + h * (0.62 + i * 0.05)
        d.arc([x - 20 + i * 30, yy, x + w * 0.55 + i * 30, yy + 26],
              200, 340, fill=(140, 180, 200), width=3)
        d.arc([x + w * 0.5 + i * 25, yy + 8, x + w + i * 25, yy + 34],
              200, 340, fill=(140, 180, 200), width=3)
    # bridge deck left part
    deck_y = y + h * 0.42
    d.rectangle([x, deck_y, x + w * 0.40, deck_y + 16], fill=(52, 58, 66))
    d.rectangle([x, deck_y, x + w * 0.40, deck_y + 6], fill=(88, 94, 104))
    # bridge deck right part
    d.rectangle([x + w * 0.62, deck_y, x + w, deck_y + 16], fill=(52, 58, 66))
    d.rectangle([x + w * 0.62, deck_y, x + w, deck_y + 6], fill=(88, 94, 104))
    # one arch across the whole bridge, broken at the centre gap
    d.arc([x + w * 0.02, deck_y - h * 0.30, x + w * 0.98, deck_y + 10],
          180, 360, fill=(52, 58, 66), width=12)
    # erase the middle of the arch (the collapsed section)
    d.rectangle([x + w * 0.43, deck_y - h * 0.30, x + w * 0.59, deck_y],
                fill=(233, 214, 180))
    # support pillars
    for px in (0.10, 0.30, 0.70, 0.90):
        d.rectangle([x + w * px, deck_y + 16, x + w * px + 10, y + h * 0.58],
                    fill=(70, 76, 84))
    # collapsed span: tilted slab falling into the sea
    d.polygon([(x + w * 0.40, deck_y + 6), (x + w * 0.52, deck_y + 40),
               (x + w * 0.50, deck_y + 62), (x + w * 0.38, deck_y + 28)],
              fill=(52, 58, 66))
    d.polygon([(x + w * 0.44, deck_y + 46), (x + w * 0.56, deck_y + 78),
               (x + w * 0.54, deck_y + 96), (x + w * 0.42, deck_y + 64)],
              fill=(70, 76, 84))
    # splash
    for cx, cy, r in [(0.50, 0.72, 26), (0.54, 0.76, 18), (0.46, 0.78, 14)]:
        d.ellipse([x + w * cx - r, y + h * cy - r * 0.6,
                   x + w * cx + r, y + h * cy + r * 0.6],
                  outline=(200, 225, 235), width=4)
    # explosion glow + smoke at the gap (small, at deck level)
    d.ellipse([x + w * 0.45, deck_y - 26, x + w * 0.55, deck_y + 14],
              fill=(240, 150, 50))
    d.ellipse([x + w * 0.475, deck_y - 14, x + w * 0.525, deck_y + 4],
              fill=(250, 210, 90))
    for cx, cy, r, col in [(0.47, 0.22, 22, (120, 118, 114)),
                           (0.52, 0.16, 28, (140, 138, 134)),
                           (0.56, 0.23, 18, (105, 103, 100))]:
        d.ellipse([x + w * cx - r, y + h * cy - r * 0.7,
                   x + w * cx + r, y + h * cy + r * 0.7], fill=col)


def tanker_scene(d, x, y, w, h):
    """Oil tanker on fire in the Strait of Hormuz."""
    d.rectangle([x, y, x + w, y + h], fill=(214, 196, 160))
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=SEA_D)
    for i in range(4):
        yy = y + h * (0.68 + i * 0.09)
        d.arc([x - 10 + i * 40, yy, x + w * 0.6 + i * 40, yy + 18],
              200, 340, fill=(140, 180, 200), width=3)
    # tanker hull
    hy = y + h * 0.52
    d.polygon([(x + w * 0.06, hy), (x + w * 0.94, hy), (x + w * 0.88, hy + h * 0.16),
               (x + w * 0.12, hy + h * 0.16)], fill=(60, 30, 28))
    d.rectangle([x + w * 0.06, hy - 6, x + w * 0.94, hy], fill=(90, 44, 40))
    # deck + superstructure
    d.rectangle([x + w * 0.68, hy - h * 0.22, x + w * 0.86, hy - 6], fill=(230, 225, 210))
    d.rectangle([x + w * 0.70, hy - h * 0.30, x + w * 0.84, hy - h * 0.22], fill=(200, 60, 40))
    # fire mid-ship
    for fx, fy, fr, col in [(0.34, 0.42, 34, (240, 150, 50)),
                            (0.40, 0.36, 26, (250, 200, 80)),
                            (0.30, 0.46, 22, (250, 210, 90)),
                            (0.44, 0.44, 18, (240, 150, 50))]:
        d.ellipse([x + w * fx - fr, y + h * fy - fr, x + w * fx + fr, y + h * fy + fr],
                  fill=col)
    # black smoke
    for cx, cy, r in [(0.36, 0.18, 30), (0.42, 0.10, 38), (0.48, 0.16, 26)]:
        d.ellipse([x + w * cx - r, y + h * cy - r * 0.7,
                   x + w * cx + r, y + h * cy + r * 0.7], fill=(45, 45, 48))
    # second distant tanker
    d.rectangle([x + w * 0.06, y + h * 0.46, x + w * 0.24, y + h * 0.52], fill=(90, 90, 92))


def summit_scene(d, x, y, w, h):
    """Three flags: US, China, Russia — the Shenzhen trilateral."""
    d.rectangle([x, y, x + w, y + h], fill=(228, 226, 218))
    # table line
    d.rectangle([x, y + h * 0.78, x + w, y + h], fill=(120, 96, 70))
    flags = [
        ("us", (255, 255, 255)),
        ("cn", (222, 41, 16)),
        ("ru", (255, 255, 255)),
    ]
    fw, fh = w * 0.24, h * 0.26
    for i, (code, _) in enumerate(flags):
        fx = x + w * (0.08 + i * 0.32)
        fy = y + h * 0.34
        # pole
        d.line([(fx + fw / 2, fy), (fx + fw / 2, y + h * 0.78)], fill=(90, 80, 60), width=5)
        d.ellipse([fx + fw / 2 - 5, fy - 5, fx + fw / 2 + 5, fy + 5], fill=(212, 160, 40))
        if code == "us":
            d.rectangle([fx, fy, fx + fw, fy + fh], fill=(255, 255, 255))
            for s in range(7):
                d.rectangle([fx, fy + s * fh / 13, fx + fw, fy + (s * 2 + 1) * fh / 13],
                            fill=(178, 34, 52))
            d.rectangle([fx, fy, fx + fw * 0.4, fy + fh * 0.54], fill=(30, 58, 95))
            for sx in range(3):
                for sy in range(3):
                    d.ellipse([fx + 6 + sx * 12, fy + 5 + sy * 11,
                               fx + 11 + sx * 12, fy + 10 + sy * 11], fill=(255, 255, 255))
        elif code == "cn":
            d.rectangle([fx, fy, fx + fw, fy + fh], fill=(222, 41, 16))
            d.polygon([(fx + 8, fy + 6), (fx + 14, fy + 18), (fx + 26, fy + 18),
                       (fx + 16, fy + 26), (fx + 20, fy + 38), (fx + 8, fy + 30),
                       (fx - 4, fy + 38), (fx + 0, fy + 26), (fx - 10, fy + 18),
                       (fx + 2, fy + 18)], fill=(255, 222, 0))
        else:
            d.rectangle([fx, fy, fx + fw, fy + fh / 3], fill=(255, 255, 255))
            d.rectangle([fx, fy + fh / 3, fx + fw, fy + 2 * fh / 3], fill=(0, 57, 166))
            d.rectangle([fx, fy + 2 * fh / 3, fx + fw, fy + fh], fill=(213, 0, 50))
    # three silhouetted figures at the table
    for i in range(3):
        cx = x + w * (0.20 + i * 0.30)
        cy = y + h * 0.60
        d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(40, 44, 52))
        d.pieslice([cx - 26, cy + 12, cx + 26, cy + 66], 180, 360, fill=(40, 44, 52))


def bank_scene(d, x, y, w, h):
    """Phone with a banking outage: error screen, red alert."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 228, 220))
    px, py = x + w * 0.34, y + h * 0.06
    pw, ph = w * 0.32, h * 0.88
    d.rounded_rectangle([px, py, px + pw, py + ph], radius=14, fill=(30, 34, 42))
    d.rounded_rectangle([px + 5, py + 5, px + pw - 5, py + ph - 5], radius=10,
                        fill=(250, 250, 248))
    # app bar
    d.rectangle([px + 5, py + 5, px + pw - 5, py + ph * 0.22], fill=NAVY)
    d.text((px + 10, py + 8), "BANK", font=font(SANS, 15), fill=WHITE)
    # red alert mark top-right of the bar
    d.ellipse([px + pw - 26, py + 9, px + pw - 10, py + 25], fill=RED)
    d.text((px + pw - 21, py + 8), "!", font=font(SANS, 14), fill=WHITE)
    # big error mark + word, sized to fit the phone
    d.text((px + pw / 2 - 16, py + ph * 0.28), "!", font=font(SANS, 52), fill=RED)
    f = font(SANS, 15)
    lbl = "ERROR"
    d.text((px + (pw - d.textlength(lbl, font=f)) / 2, py + ph * 0.68), lbl,
           font=f, fill=INK)


def rocket_scene(d, x, y, w, h):
    """Vulcan rocket breaking up: tilted rocket, flame, debris, dark sky."""
    d.rectangle([x, y, x + w, y + h], fill=(24, 32, 54))
    for sx, sy in [(0.12, 0.14), (0.30, 0.08), (0.55, 0.18), (0.78, 0.10),
                   (0.88, 0.30), (0.08, 0.38), (0.66, 0.06)]:
        d.ellipse([x + w * sx - 2, y + h * sy - 2, x + w * sx + 2, y + h * sy + 2],
                  fill=(220, 220, 220))
    # smoke trail
    for i in range(6):
        r = 14 + i * 5
        d.ellipse([x + w * (0.62 - i * 0.055) - r, y + h * (0.42 + i * 0.075) - r * 0.6,
                   x + w * (0.62 - i * 0.055) + r, y + h * (0.42 + i * 0.075) + r * 0.6],
                  fill=(150, 150, 158))
    # rocket body (tilted)
    d.polygon([(x + w * 0.60, y + h * 0.16), (x + w * 0.70, y + h * 0.30),
               (x + w * 0.66, y + h * 0.52), (x + w * 0.56, y + h * 0.38)],
              fill=(235, 235, 230))
    d.polygon([(x + w * 0.60, y + h * 0.16), (x + w * 0.65, y + h * 0.06),
               (x + w * 0.70, y + h * 0.30)], fill=(200, 60, 40))
    # flame + explosion at break point
    d.ellipse([x + w * 0.56, y + h * 0.46, x + w * 0.68, y + h * 0.62], fill=(240, 150, 50))
    d.ellipse([x + w * 0.59, y + h * 0.50, x + w * 0.65, y + h * 0.58], fill=(250, 210, 90))
    # debris dots
    for dx, dy in [(0.74, 0.55), (0.80, 0.62), (0.70, 0.68), (0.84, 0.48), (0.52, 0.66)]:
        d.ellipse([x + w * dx - 4, y + h * dy - 4, x + w * dx + 4, y + h * dy + 4],
                  fill=(220, 200, 160))
    # ground
    d.rectangle([x, y + h * 0.88, x + w, y + h], fill=(16, 22, 38))


# ---------------------------------------------------------------- variants
def masthead(d, date_size=56):
    """Top navy band naming the day — shared by all variants."""
    d.rectangle([0, 0, W, 128], fill=NAVY)
    d.text((32, 18), "THE WORLD IN ONE PICTURE", font=font(SANS, 24),
           fill=(180, 200, 225))
    d.text((32, 48), "TUESDAY 17 NOVEMBER 2026", font=font(SERIF, date_size),
           fill=WHITE)
    d.rectangle([0, 128, W, 134], fill=RED)


def variant_a():
    """Front page: hero bridge + right column of three stories + rocket strip."""
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    masthead(d)
    # --- hero bridge ---
    hx, hy, hw, hh = 24, 150, 616, 400
    bridge_scene(d, hx, hy, hw, hh)
    d.rectangle([hx, hy, hx + hw, hy + hh], outline=INK, width=3)
    tag(d, hx + 10, hy + 10, "UKRAINE  •  TOP STORY", font(SANS, 20))
    y = hy + hh + 16
    y = text_block(d, hx, y, hw, "UKRAINE STRIKES THE KERCH BRIDGE AGAIN",
                   font(SERIF, 44), leading=50)
    y = text_block(d, hx, y + 6, hw,
                   "Road span collapses into the strait in a second attack in 24 hours",
                   font(SERIF_R, 26), leading=32)
    y += 14
    rule(d, hx, y, hw, width=2)
    y = text_block(d, hx, y + 10, hw,
                   "Russia hits Kyiv's river crossings in reply; Kyiv says the bridge is a military target.",
                   font(SANS_R, 21), leading=27)
    # --- right column ---
    rx, rw = 664, 336
    stories = [
        ("HORMUZ", "TANKERS HIT BY MINES", tanker_scene,
         "Two tankers catch fire near the strait; a third US carrier arrives."),
        ("SHENZHEN  •  THURSDAY", "TRUMP, XI & PUTIN TO MEET", summit_scene,
         "China confirms the first three-way summit, at APEC in Shenzhen."),
        ("MONEY", "JPMORGAN BLAMES SOFTWARE BUG", bank_scene,
         "Outage hits online accounts and Zelle; 'no sign of a cyberattack'."),
    ]
    sy = 150
    ph = 237
    for label, head, scene, sub in stories:
        scene(d, rx, sy, rw, 120)
        d.rectangle([rx, sy, rx + rw, sy + 120], outline=INK, width=2)
        tag(d, rx + 8, sy + 8, label, font(SANS, 16))
        ty = sy + 128
        ty = text_block(d, rx, ty, rw, head, font(SANS, 24), leading=28)
        text_block(d, rx, ty + 4, rw, sub, font(SANS_R, 17), leading=22)
        sy += ph
    # --- bottom rocket strip ---
    by = 862
    d.rectangle([24, by, 1000, 1000], fill=(24, 32, 54))
    rocket_scene(d, 40, by + 8, 220, 122)
    d.rectangle([40, by + 8, 260, by + 130], outline=WHITE, width=2)
    ty = text_block(d, 284, by + 14, 700,
                    "VULCAN ROCKET FAILS IN FLIGHT",
                    font(SANS, 30), fill=WHITE, leading=35)
    ty = text_block(d, 284, ty + 2, 700,
                    "40 Amazon satellites lost",
                    font(SANS, 24), fill=(220, 200, 140), leading=29)
    text_block(d, 284, ty + 6, 700,
               "ULA rocket breaks up minutes after launch from Cape Canaveral.  •  Nvidia reports first earnings since Jensen Huang's exit.",
               font(SANS_R, 19), fill=(200, 210, 225), leading=25)
    return im


def variant_b():
    """Five frames: date banner, big bridge with headline overlay, 2x2 grid."""
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    masthead(d)
    # hero
    hx, hy, hw, hh = 24, 150, 976, 380
    bridge_scene(d, hx, hy, hw, hh)
    d.rectangle([hx, hy, hx + hw, hy + hh], outline=INK, width=3)
    # headline band over bottom of hero
    d.rectangle([hx, hy + hh - 96, hx + hw, hy + hh], fill=(17, 24, 39))
    d.text((hx + 18, hy + hh - 88), "UKRAINE STRIKES THE KERCH BRIDGE AGAIN",
           font=font(SERIF, 40), fill=WHITE)
    d.text((hx + 18, hy + hh - 40),
           "Road span collapses into the strait — second attack in 24 hours",
           font=font(SERIF_R, 24), fill=(220, 220, 210))
    tag(d, hx + 12, hy + 12, "TOP STORY", font(SANS, 20))
    # 2x2 grid
    cells = [
        ("TANKERS HIT BY MINES OFF HORMUZ", tanker_scene,
         "Two tankers catch fire near the strait"),
        ("TRUMP, XI & PUTIN TO MEET THURSDAY", summit_scene,
         "First three-way summit, in Shenzhen"),
        ("JPMORGAN BLAMES SOFTWARE BUG", bank_scene,
         "Outage hits accounts and Zelle"),
        ("VULCAN ROCKET FAILS", rocket_scene,
         "40 Amazon satellites lost"),
    ]
    cw, chh = 482, 196
    for i, (head, scene, sub) in enumerate(cells):
        cx = 24 + (i % 2) * (cw + 12)
        cy = 546 + (i // 2) * (chh + 12)
        scene(d, cx, cy, cw, 118)
        d.rectangle([cx, cy, cx + cw, cy + 118], outline=INK, width=2)
        d.rectangle([cx, cy + 118, cx + cw, cy + chh], fill=CREAM)
        d.rectangle([cx, cy + 118, cx + cw, cy + chh], outline=INK, width=2)
        text_block(d, cx + 12, cy + 126, cw - 24, head, font(SANS, 22), leading=26)
        text_block(d, cx + 12, cy + 156, cw - 24, sub, font(SANS_R, 18), leading=22)
    return im


def variant_c():
    """Hero full-bleed bridge, headline band, four-column story strip."""
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    # date strip on top of the scene
    d.rectangle([0, 0, W, 96], fill=NAVY)
    d.text((32, 14), "TUESDAY 17 NOVEMBER 2026", font=font(SERIF, 52), fill=WHITE)
    d.text((760, 34), "THE WORLD IN ONE PICTURE", font=font(SANS, 20),
           fill=(180, 200, 225))
    d.rectangle([0, 96, W, 102], fill=RED)
    bridge_scene(d, 0, 102, W, 560)
    # headline band
    d.rectangle([0, 600, W, 700], fill=(17, 24, 39))
    d.text((32, 612), "UKRAINE STRIKES THE KERCH BRIDGE AGAIN",
           font=font(SERIF, 42), fill=WHITE)
    d.text((32, 660), "Road span collapses into the strait — second attack in 24 hours",
           font=font(SERIF_R, 24), fill=(220, 220, 210))
    # four columns
    cols = [
        ("HORMUZ", "Tankers hit by mines; two catch fire near the strait", (240, 150, 50)),
        ("SHENZHEN", "Trump, Xi & Putin to meet Thursday at APEC", (30, 58, 95)),
        ("MONEY", "JPMorgan blames a software bug for bank outage", (185, 28, 28)),
        ("SPACE", "Vulcan rocket fails; 40 Amazon satellites lost", (24, 32, 54)),
    ]
    cw = 244
    for i, (kicker, txt, col) in enumerate(cols):
        cx = 16 + i * (cw + 8)
        d.rectangle([cx, 716, cx + cw, 1000], outline=INK, width=2)
        d.rectangle([cx, 716, cx + cw, 752], fill=col)
        d.text((cx + 12, 722), kicker, font=font(SANS, 22), fill=WHITE)
        text_block(d, cx + 12, 768, cw - 24, txt, font(SANS, 24), leading=30)
    d.text((16, 1004 - 8), "", font=font(SANS, 10))
    return im


if __name__ == "__main__":
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "variants")
    os.makedirs(outdir, exist_ok=True)
    for name, fn in [("a_frontpage", variant_a), ("b_fiveframes", variant_b),
                     ("c_hero", variant_c)]:
        im = fn()
        p = os.path.join(outdir, name + ".png")
        im.save(p, optimize=True)
        print(name, os.path.getsize(p), "bytes", im.size)
