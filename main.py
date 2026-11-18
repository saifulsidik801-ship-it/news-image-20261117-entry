#!/usr/bin/env python3
"""news-image-20261117: a one-day world-news front page for Tuesday 17 November 2026.

Draws a dense newspaper front page (43 stories, 6 continents) with Pillow only:
no network, no external assets, no downloaded pictures. Writes entry.png
(1024 x 1024, under 1 MiB) next to this file and to /output/entry.png when
that directory exists or can be created.

Layout follows the winning front-page formula: masthead with the date and the
story count, three illustrated hero stories, ten mid stories with small
illustrated banners, a numbered world map, a two-column "also on" digest of
the remaining thirty stories, and a sources footer. Every story happened or
was first reported on Tuesday 17 November 2026.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024
MARGIN = 16

PAPER = (246, 240, 220)
INK = (20, 20, 20)
RULE = (20, 20, 20)
RED = (176, 30, 36)
BLUE = (43, 94, 167)
ORANGE = (217, 122, 31)
PURPLE = (122, 79, 163)
GREEN = (46, 125, 50)
DARKPURPLE = (91, 74, 138)
TEAL = (31, 138, 138)
NAVY = (31, 42, 68)
SEA = (183, 211, 222)
LAND = (231, 220, 185)
LAND_LINE = (185, 168, 111)

REGION_COLORS = {
    "EU": BLUE,
    "ME": ORANGE,
    "AS": PURPLE,
    "AF": GREEN,
    "AM": RED,
    "GL": DARKPURPLE,
    "OC": TEAL,
    "US": RED,
}

SERIF_BOLD_PATHS = [
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
]
SERIF_PATHS = [
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
]
SANS_BOLD_PATHS = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
SANS_PATHS = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
CONDENSED_PATHS = [
    "/usr/share/fonts/truetype/noto/NotoSans-Condensed.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
CONDENSED_BOLD_PATHS = [
    "/usr/share/fonts/truetype/noto/NotoSans-CondensedBold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def load_font(paths, size):
    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def serif_b(size):
    return load_font(SERIF_BOLD_PATHS, size)


def serif(size):
    return load_font(SERIF_PATHS, size)


def sans_b(size):
    return load_font(SANS_BOLD_PATHS, size)


def sans(size):
    return load_font(SANS_PATHS, size)


def cond(size):
    return load_font(CONDENSED_PATHS, size)


def cond_b(size):
    return load_font(CONDENSED_BOLD_PATHS, size)


def text_w(draw, text, font):
    """Pixel width of text with the given font."""
    left, _top, right, _bottom = draw.textbbox((0, 0), text, font=font)
    return right - left


def wrap(draw, text, font, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_w(draw, trial, font) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines(draw, x, y, lines, font, fill, leading):
    """Draw lines top to bottom; returns the y just below the last line."""
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def fit_lines(draw, text, font_paths, size, max_width, max_lines):
    """Wrap text, shrinking the font until it fits in max_lines; returns lines, font."""
    size_now = size
    while size_now >= 8:
        font = load_font(font_paths, size_now)
        lines = wrap(draw, text, font, max_width)
        if len(lines) <= max_lines:
            return lines, font
        size_now -= 1
    font = load_font(font_paths, 8)
    return wrap(draw, text, font, max_width)[:max_lines], font


def num_badge(draw, cx, cy, radius, number, color):
    draw.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        fill=color,
        outline=(255, 255, 255),
        width=1,
    )
    label = str(number)
    font = sans_b(max(9, radius + 1))
    w = text_w(draw, label, font)
    bbox = draw.textbbox((0, 0), label, font=font)
    draw.text((cx - w / 2, cy - (bbox[3] - bbox[1]) / 2 - bbox[1]), label,
              font=font, fill=(255, 255, 255))


def pill(draw, x, y, w, h, color, text, font):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=color)
    tw = text_w(draw, text, font)
    bbox = draw.textbbox((0, 0), text, font=font)
    draw.text((x + (w - tw) / 2, y + (h - (bbox[3] - bbox[1])) / 2 - bbox[1]),
              text, font=font, fill=(255, 255, 255))


def flag_us(draw, x, y, w, h):
    stripe = h / 13.0
    for i in range(13):
        color = (178, 34, 52) if i % 2 == 0 else (255, 255, 255)
        draw.rectangle([x, y + i * stripe, x + w, y + (i + 1) * stripe], fill=color)
    canton_w = w * 0.4
    canton_h = stripe * 7
    draw.rectangle([x, y, x + canton_w, y + canton_h], fill=(60, 59, 110))
    for row in range(5):
        for col in range(6):
            cx = x + 4 + col * (canton_w - 8) / 5.0
            cy = y + 3 + row * (canton_h - 6) / 4.0
            draw.ellipse([cx - 1, cy - 1, cx + 1, cy + 1], fill=(255, 255, 255))


def flag_india(draw, x, y, w, h):
    third = h / 3.0
    draw.rectangle([x, y, x + w, y + third], fill=(255, 153, 51))
    draw.rectangle([x, y + third, x + w, y + 2 * third], fill=(255, 255, 255))
    draw.rectangle([x, y + 2 * third, x + w, y + h], fill=(19, 136, 8))
    cx, cy = x + w / 2, y + h / 2
    r = third * 0.42
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(0, 0, 128), width=1)


def flag_japan(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    cx, cy = x + w / 2, y + h / 2
    r = h * 0.3
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(188, 0, 45))


def flag_australia(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(0, 40, 104))
    draw.rectangle([x, y, x + w * 0.5, y + h * 0.5], fill=(200, 16, 46))
    draw.line([x, y, x + w * 0.5, y + h * 0.5], fill=(255, 255, 255), width=2)
    draw.line([x + w * 0.5, y, x, y + h * 0.5], fill=(255, 255, 255), width=2)
    for cx, cy in [(x + w * 0.72, y + h * 0.3), (x + w * 0.85, y + h * 0.62),
                   (x + w * 0.68, y + h * 0.78)]:
        draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(255, 255, 255))


def flag_tricolor_v(draw, x, y, w, h, colors):
    third = w / 3.0
    for i, color in enumerate(colors):
        draw.rectangle([x + i * third, y, x + (i + 1) * third, y + h], fill=color)


def flag_tricolor_h(draw, x, y, w, h, colors):
    third = h / 3.0
    for i, color in enumerate(colors):
        draw.rectangle([x, y + i * third, x + w, y + (i + 1) * third], fill=color)


# ---------------------------------------------------------------- data ---

HEROES = [
    {
        "num": 1, "region": "EU", "art": "kerch",
        "kicker": "EUROPE · UKRAINE WAR",
        "headline": "Ukraine says a Crimean Bridge road span fell into the sea",
        "deck": "Second strike in two days; Zelensky hails an \u201cunprecedented operation\u201d. The Kremlin vows to rebuild.",
    },
    {
        "num": 2, "region": "ME", "art": "hormuz",
        "kicker": "MIDDLE EAST · IRAN WAR",
        "headline": "Iran sends drones at a US radar in Bahrain; US hits back",
        "deck": "Bahrain and the US say all were downed; US jets then strike Qeshm. Iran says tankers hit mines in Hormuz.",
    },
    {
        "num": 3, "region": "AS", "art": "quad",
        "kicker": "ASIA · DIPLOMACY",
        "headline": "Trump holds his first Quad summit, in Manila",
        "deck": "The four unveil critical-minerals deals; Putin reaches Shenzhen for Thursday\u2019s talks with Trump and Xi.",
    },
]

MIDS = [
    {"num": 4, "region": "AF", "art": "ebola",
     "kicker": "AFRICA · HEALTH",
     "headline": "Ebola cases in DR Congo top 11,000, WHO says",
     "deck": "Cases more than doubled in three months; about 5,400 have died."},
    {"num": 5, "region": "GL", "art": "cop31",
     "kicker": "GLOBAL · CLIMATE",
     "headline": "COP31 divided over a fossil-fuel phase-out",
     "deck": "Nations weigh the first draft; the Antalya talks end Friday."},
    {"num": 6, "region": "AM", "art": "measles",
     "kicker": "AMERICAS · HEALTH",
     "headline": "US, Mexico and Bolivia lose measles-free status",
     "deck": "PAHO cites a year of spread; the US has 5,700+ cases in 2026."},
    {"num": 7, "region": "US", "art": "nvidia",
     "kicker": "US · BUSINESS",
     "headline": "Nvidia\u2019s quarterly sales double to $115.8bn",
     "deck": "Reported after the close. Earlier the Dow fell 849 points (-1.6%)."},
    {"num": 8, "region": "ME", "art": "gaza",
     "kicker": "MIDDLE EAST · GAZA",
     "headline": "Gaza truce at risk of collapse, UN is told",
     "deck": "Board of Peace report; UN agencies say 1.4m face acute hunger."},
    {"num": 9, "region": "AS", "art": "mongolia",
     "kicker": "ASIA · POLITICS",
     "headline": "Mongolia\u2019s president says he will resign",
     "deck": "Khurelsukh denies a $25m bribe claim; parliament must accept."},
    {"num": 10, "region": "EU", "art": "serbia",
     "kicker": "EUROPE · POLITICS",
     "headline": "Serbia\u2019s student-led majority takes its seats",
     "deck": "Student List holds 140 of 250; Vucic\u2019s party goes into opposition."},
    {"num": 11, "region": "AS", "art": "bangladesh",
     "kicker": "ASIA · LABOUR",
     "headline": "Bangladesh police tear-gas garment workers",
     "deck": "They want Tk 30,000 a month, up from 12,500; 37 factories shut."},
    {"num": 12, "region": "EU", "art": "an12",
     "kicker": "RUSSIA · AIR CRASH",
     "headline": "Russian An-12 crash in Siberia kills all 19",
     "deck": "The air force plane came down near Kemerovo; a fault is suspected."},
    {"num": 13, "region": "AF", "art": "maputo",
     "kicker": "AFRICA · JUSTICE",
     "headline": "Mozambique puts opposition leader on trial",
     "deck": "Venancio Mondlane faces 5 charges over deadly 2024 protests."},
]

# (number, region, one-line title, longitude, latitude) for the digest.
ALSO = [
    (14, "EU", "Russia: record 1,441 drones downed overnight", 60, 55),
    (15, "EU", "Kyiv: missiles hit two Dnipro bridges", 30.5, 50.4),
    (16, "GL", "UN: Ukraine civilian deaths top all of 2025", 31, 49),
    (17, "EU", "Prague: two trains collide; 46 injured", 14.4, 50),
    (18, "EU", "France: public-sector strike; 146,000 march", 2.3, 48.8),
    (19, "EU", "Poland: Tusk survives no-confidence vote", 21, 52.2),
    (20, "EU", "Germany: Deutsche Bank shares fall on data leak", 10, 51),
    (21, "EU", "Moldova: airspace shut as drone nears Chisinau", 28.8, 47),
    (22, "ME", "Turkey: police seize broadcaster Sozcu TV", 32.8, 39.9),
    (23, "EU", "Football: Norway win 3-2 in Denmark", 10, 57),
    (24, "EU", "Vatican: Pope Leo XIV back from S. America tour", 12.45, 41.9),
    (25, "EU", "UK: sanctions 8 settlement firms and Tzav 9", -0.1, 51.5),
    (26, "ME", "Israel: Eisenkot ally elected speaker, 66-52", 34.8, 32),
    (27, "ME", "West Bank: settlers kill a woman, 72", 35.2, 31.9),
    (28, "ME", "Oman: Iran's Araghchi holds shipping talks", 58.4, 23.6),
    (29, "AS", "India: Cyclone Akvan strengthens; evacuations", 78, 21),
    (30, "AS", "India: bus falls into gorge, 8 dead", 79, 30),
    (31, "AS", "Japan: protests Russian airspace intrusion", 139.7, 35.7),
    (32, "AS", "China-Canada: more tariff cuts after Xi talks", 116, 40),
    (33, "AS", "Malaysia: Macron visit seals partnership", 101.7, 3.1),
    (34, "AS", "Thailand: pledges to scrap tariffs on US goods", 100.5, 13.7),
    (35, "AS", "South Korea: IMF lifts 2026 forecast to 3.9%", 127, 36.5),
    (36, "AS", "Football: India beat Pakistan 2-1 in SAFF final", 77, 28),
    (37, "AF", "Kenya: WFP aids 30,000 fleeing Ethiopia clashes", 38, 0.5),
    (38, "AF", "Football: Togo beat Algeria 3-0 in AFCON qualifier", 1.2, 6.1),
    (39, "AM", "Haiti: Aristide's party will field no candidates", -72.7, 19),
    (40, "AM", "US Senate: Van Hollen challenges Schumer", -77, 38.9),
    (41, "OC", "Australia: eases planned backpacker visa curbs", 133, -25),
    (42, "OC", "Darwin: M6.6 quake off Indonesia felt", 130.8, -12.4),
    (43, "AM", "Apple: Pay, iCloud and App Store outage", -122, 37.4),
]

# (number, region, longitude, latitude) for the map pins of stories 1-13.
PINS = [
    (1, "EU", 34, 47),
    (2, "ME", 50.5, 26),
    (3, "AS", 121, 14.6),
    (4, "AF", 23, -2),
    (5, "GL", 32, 39),
    (6, "AM", -99, 19),
    (7, "AM", -122, 37),
    (8, "ME", 33, 29),
    (9, "AS", 106, 47),
    (10, "EU", 18, 46),
    (11, "AS", 90.4, 23.8),
    (12, "EU", 86, 55),
    (13, "AF", 32.6, -25.9),
]


# ------------------------------------------------------- hero art ---

def rotated_rect(draw, cx, cy, w, h, angle_deg, fill):
    import math
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    hw, hh = w / 2.0, h / 2.0
    pts = []
    for sx, sy in [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]:
        pts.append((cx + sx * ca - sy * sa, cy + sx * sa + sy * ca))
    draw.polygon(pts, fill=fill)


def draw_kerch(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(196, 217, 230))
    draw.rectangle([x, y + 82, x + w, y + h - 20], fill=(47, 110, 140))
    for wy in (y + 94, y + 104, y + 114):
        for wx in range(x + 8, x + w - 20, 34):
            draw.line([wx, wy, wx + 20, wy], fill=(120, 180, 200), width=2)
    # bridge deck with a fallen middle span
    draw.rectangle([x + 8, y + 56, x + 128, y + 64], fill=(58, 58, 58))
    draw.rectangle([x + 196, y + 56, x + w - 8, y + 64], fill=(58, 58, 58))
    draw.polygon([(x + 128, y + 58), (x + 164, y + 96), (x + 176, y + 92),
                  (x + 142, y + 56)], fill=(58, 58, 58))
    for px in (x + 30, x + 80, x + 220, x + 280):
        draw.line([px, y + 64, px, y + 82], fill=(58, 58, 58), width=3)
    # smoke plume above the gap
    for cx, cy, r, c in [(150, 18, 14, (138, 138, 138)),
                         (166, 28, 11, (110, 110, 110)),
                         (136, 30, 9, (160, 160, 160)),
                         (158, 40, 8, (130, 130, 130))]:
        draw.ellipse([x + cx - r, y + cy - r, x + cx + r, y + cy + r], fill=c)
    draw.ellipse([x + 152, y + 48, x + 164, y + 60], fill=(255, 150, 40))
    draw.ellipse([x + 155, y + 51, x + 161, y + 57], fill=(255, 220, 80))
    # jets
    for jx, jy in [(78, 16), (258, 12)]:
        draw.polygon([(x + jx + 10, y + jy), (x + jx - 8, y + jy - 6),
                      (x + jx - 8, y + jy + 6)], fill=(40, 40, 40))
        draw.line([x + jx - 8, y + jy, x + jx - 22, y + jy],
                  fill=(40, 40, 40), width=1)
    lab = sans_b(10)
    draw.text((x + 10, y + 6), "CRIMEA", font=lab, fill=(40, 40, 40))
    rt = text_w(draw, "RUSSIA", lab)
    draw.text((x + w - 10 - rt, y + 6), "RUSSIA", font=lab, fill=(40, 40, 40))
    draw.rectangle([x, y + h - 20, x + w, y + h], fill=NAVY)
    cap = sans_b(11)
    ct = "KERCH STRAIT · STRUCK FOR A SECOND DAY"
    draw.text((x + (w - text_w(draw, ct, cap)) / 2, y + h - 16),
              ct, font=cap, fill=(255, 255, 255))
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=2)


def draw_hormuz(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(233, 219, 172))
    draw.polygon([(x + 90, y + 42), (x + 180, y + 34), (x + 260, y + 44),
                  (x + w, y + 38), (x + w, y + h - 20), (x + 110, y + h - 20),
                  (x + 70, y + 80), (x + 90, y + 42)], fill=(168, 203, 216))
    lab = sans_b(10)
    draw.text((x + 118, y + 8), "IRAN", font=lab, fill=(60, 60, 60))
    draw.text((x + 8, y + 58), "BAHRAIN", font=lab, fill=(60, 60, 60))
    draw.text((x + 262, y + 66), "QESHM", font=lab, fill=(60, 60, 60))
    draw.text((x + 252, y + h - 38), "HORMUZ", font=lab, fill=(60, 60, 60))
    # dashed flight path Bahrain -> Qeshm
    import math
    for t in [i / 10.0 for i in range(11)]:
        px = x + 34 + t * 220
        py = y + 62 - 26 * math.sin(math.pi * t)
        if int(t * 10) % 2 == 0:
            draw.line([px, py, px + 12, py - 3], fill=(90, 90, 90), width=2)
    # drone downed marker
    draw.line([x + 142, y + 62, x + 158, y + 78], fill=RED, width=3)
    draw.line([x + 158, y + 62, x + 142, y + 78], fill=RED, width=3)
    pill(draw, x + 108, y + 46, 104, 16, RED, "DRONES DOWNED", sans_b(10))
    pill(draw, x + 140, y + 88, 84, 16, BLUE, "US STRIKES", sans_b(10))
    # tanker
    draw.polygon([(x + 238, y + 104), (x + 292, y + 104), (x + 286, y + 114),
                  (x + 244, y + 114)], fill=(60, 60, 60))
    draw.rectangle([x + 258, y + 96, x + 274, y + 104], fill=(255, 255, 255))
    draw.rectangle([x + 258, y + 96, x + 274, y + 99], fill=RED)
    # explosion star near Hormuz
    ex, ey = x + 240, y + 58
    for ang in range(0, 360, 45):
        import math as _m
        r = 9
        dx = r * _m.cos(_m.radians(ang))
        dy = r * _m.sin(_m.radians(ang))
        draw.line([ex, ey, ex + dx, ey + dy], fill=(255, 150, 40), width=2)
    draw.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=(255, 220, 80))
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=2)


def draw_quad(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(237, 230, 245))
    draw.rectangle([x, y, x + w, y + 28], fill=(106, 63, 160))
    head = sans_b(13)
    ht = "QUAD LEADERS' SUMMIT · MANILA"
    draw.text((x + (w - text_w(draw, ht, head)) / 2, y + 7),
              ht, font=head, fill=(255, 255, 255))
    flags = [(flag_us, "US"), (flag_india, "INDIA"),
             (flag_japan, "JAPAN"), (flag_australia, "AUSTRALIA")]
    card_w, card_h = 66, 44
    total = 4 * card_w + 3 * 10
    start = x + (w - total) / 2
    lab = sans_b(10)
    for i, (fn, name) in enumerate(flags):
        cx = start + i * (card_w + 10)
        draw.rectangle([cx, y + 38, cx + card_w, y + 38 + card_h],
                       fill=(255, 255, 255), outline=(120, 120, 120), width=1)
        fn(draw, cx + 4, y + 42, card_w - 8, 30)
        nw = text_w(draw, name, lab)
        draw.text((cx + (card_w - nw) / 2, y + 86), name, font=lab, fill=INK)
    draw.rectangle([x + 16, y + 106, x + w - 16, y + 112], fill=(138, 109, 75))
    draw.rectangle([x + 30, y + 112, x + 34, y + h - 24], fill=(138, 109, 75))
    draw.rectangle([x + w - 34, y + 112, x + w - 30, y + h - 24], fill=(138, 109, 75))
    draw.rectangle([x, y + h - 20, x + w, y + h], fill=(106, 63, 160))
    cap = sans_b(11)
    ct = "NEW CRITICAL-MINERALS DEALS"
    draw.text((x + (w - text_w(draw, ct, cap)) / 2, y + h - 16),
              ct, font=cap, fill=(255, 255, 255))
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=2)


HERO_ART = {"kerch": draw_kerch, "hormuz": draw_hormuz, "quad": draw_quad}


# ------------------------------------------------------- mid banners ---

def banner_frame(draw, x, y, w, h, bg):
    draw.rectangle([x, y, x + w, y + h], fill=bg)
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)


def draw_banner_ebola(draw, x, y, w, h):
    banner_frame(draw, x, y, w, h, (221, 235, 211))
    draw.rectangle([x + 18, y + 18, x + 72, y + h - 6], fill=(255, 255, 255),
                   outline=(90, 90, 90), width=1)
    draw.rectangle([x + 40, y + 8, x + 50, y + 26], fill=RED)
    draw.rectangle([x + 32, y + 14, x + 58, y + 20], fill=RED)
    draw.rectangle([x + 24, y + 30, x + 66, y + 34], fill=(120, 160, 120))
    draw.rectangle([x + 24, y + 38, x + 66, y + 42], fill=(120, 160, 120))
    pill(draw, x + w - 96, y + 5, 90, 14, RED, "11,000+ CASES", sans_b(9))


def draw_banner_cop31(draw, x, y, w, h):
    banner_frame(draw, x, y, w, h, (211, 232, 228))
    cx, cy, r = x + 34, y + 28, 17
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(74, 144, 164))
    draw.ellipse([cx - r // 2, cy - r, cx + r // 2, cy + r],
                 outline=(255, 255, 255), width=1)
    draw.line([cx - r, cy, cx + r, cy], fill=(255, 255, 255), width=1)
    draw.rounded_rectangle([x + 66, y + 8, x + 74, y + 42], radius=4, fill=RED)
    draw.ellipse([x + 63, y + 40, x + 77, y + 52], fill=RED)
    lab = sans_b(9)
    draw.text((x + 86, y + 12), "DRAFT: PHASE-OUT", font=lab, fill=INK)
    draw.text((x + 86, y + 26), "FOSSIL FUELS?", font=lab, fill=INK)


def draw_banner_measles(draw, x, y, w, h):
    banner_frame(draw, x, y, w, h, (246, 217, 217))
    flag_us(draw, x + 12, y + 12, 30, 19)
    flag_tricolor_v(draw, x + 50, y + 12, 30, 19,
                    [(0, 104, 71), (255, 255, 255), (206, 17, 38)])
    flag_tricolor_h(draw, x + 88, y + 12, 30, 19,
                    [(213, 0, 50), (247, 219, 0), (0, 122, 51)])
    for cx, cy, r in [(150, 18, 7), (168, 34, 5), (138, 40, 4)]:
        draw.ellipse([x + cx - r, y + cy - r, x + cx + r, y + cy + r],
                     fill=RED)
        for dx, dy in [(-r - 2, 0), (r + 2, 0), (0, -r - 2), (0, r + 2)]:
            draw.line([x + cx, y + cy, x + cx + dx, y + cy + dy],
                      fill=RED, width=1)


def draw_banner_nvidia(draw, x, y, w, h):
    banner_frame(draw, x, y, w, h, (17, 17, 17))
    heights = [8, 16, 24, 32]
    for i, hh in enumerate(heights):
        bx = x + 14 + i * 16
        draw.rectangle([bx, y + 46 - hh, bx + 12, y + 46], fill=(118, 200, 60))
    draw.text((x + 88, y + 10), "$115.8BN", font=sans_b(13), fill=(118, 200, 60))
    draw.text((x + 88, y + 30), "DOW -849", font=sans_b(10), fill=(220, 80, 80))


def draw_banner_gaza(draw, x, y, w, h):
    banner_frame(draw, x, y, w, h, (239, 227, 200))
    pill(draw, x + 8, y + 4, 122, 13, RED, "1.4M FACE ACUTE HUNGER", sans_b(8))
    draw.polygon([(x + 16, y + 48), (x + 36, y + 22), (x + 56, y + 48)],
                 fill=(200, 180, 140), outline=(120, 100, 60))
    draw.polygon([(x + 52, y + 48), (x + 66, y + 30), (x + 80, y + 48)],
                 fill=(180, 160, 120), outline=(120, 100, 60))
    draw.rectangle([x + 100, y + 30, x + 140, y + 48], fill=(255, 255, 255),
                   outline=(90, 90, 90), width=1)
    draw.rectangle([x + 140, y + 34, x + 152, y + 48], fill=(200, 200, 200),
                   outline=(90, 90, 90), width=1)
    draw.ellipse([x + 108, y + 46, x + 116, y + 52], fill=(40, 40, 40))
    draw.ellipse([x + 128, y + 46, x + 136, y + 52], fill=(40, 40, 40))


def draw_banner_mongolia(draw, x, y, w, h):
    banner_frame(draw, x, y, w, h, (227, 234, 246))
    draw.polygon([(x + 14, y + 30), (x + 44, y + 12), (x + 74, y + 30)],
                 fill=(120, 120, 130))
    for cx in (22, 36, 50, 64):
        draw.rectangle([x + cx, y + 30, x + cx + 5, y + 50], fill=(120, 120, 130))
    draw.rectangle([x + 12, y + 50, x + 76, y + 54], fill=(120, 120, 130))
    draw.rectangle([x + 96, y + 14, x + 182, y + 38], fill=(255, 255, 255),
                   outline=(90, 90, 90), width=1)
    lab = sans_b(9)
    t = "RESIGNATION"
    draw.text((x + 96 + (86 - text_w(draw, t, lab)) / 2, y + 21), t,
              font=lab, fill=RED)


def draw_banner_serbia(draw, x, y, w, h):
    import math
    banner_frame(draw, x, y, w, h, (220, 232, 247))
    cx, cy = x + 48, y + 52
    for radius, count in [(26, 9), (15, 6)]:
        for i in range(count):
            ang = math.pi * (1 + i / (count - 1))
            px = cx + radius * math.cos(ang)
            py = cy + radius * math.sin(ang) * 0.85
            col = BLUE if (i % 2 == 0) else RED
            draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=col)
    lab = sans_b(10)
    draw.text((x + 92, y + 12), "STUDENTS 140", font=lab, fill=BLUE)
    draw.text((x + 92, y + 28), "VUCIC 103", font=lab, fill=RED)


def draw_banner_bangladesh(draw, x, y, w, h):
    banner_frame(draw, x, y, w, h, (221, 235, 211))
    draw.polygon([(x + 14, y + 48), (x + 14, y + 26), (x + 26, y + 34),
                  (x + 38, y + 22), (x + 50, y + 32), (x + 62, y + 22),
                  (x + 74, y + 30), (x + 86, y + 22), (x + 86, y + 48)],
                 fill=(90, 110, 90))
    draw.rectangle([x + 92, y + 10, x + 100, y + 48], fill=(90, 110, 90))
    pill(draw, x + w - 118, y + 5, 112, 14, GREEN, "TK 30,000 MINIMUM", sans_b(9))


def draw_banner_an12(draw, x, y, w, h):
    banner_frame(draw, x, y, w, h, (216, 222, 232))
    body = (70, 80, 95)
    draw.polygon([(x + 18, y + 20), (x + 118, y + 34), (x + 126, y + 40),
                  (x + 118, y + 44), (x + 20, y + 30)], fill=body)
    draw.polygon([(x + 60, y + 24), (x + 84, y + 12), (x + 92, y + 16),
                  (x + 70, y + 28)], fill=body)
    draw.polygon([(x + 110, y + 32), (x + 128, y + 18), (x + 134, y + 22),
                  (x + 120, y + 38)], fill=body)
    pill(draw, x + 8, y + 38, 132, 13, NAVY, "ALL 19 ABOARD KILLED", sans_b(8))


def draw_banner_maputo(draw, x, y, w, h):
    banner_frame(draw, x, y, w, h, (211, 232, 228))
    draw.line([x + 28, y + 44, x + 68, y + 16], fill=(120, 82, 40), width=5)
    rotated_rect(draw, x + 74, y + 12, 30, 14, -30, (120, 82, 40))
    draw.rectangle([x + 96, y + 40, x + 150, y + 46], fill=(150, 110, 60))
    pill(draw, x + w - 74, y + 5, 68, 14, TEAL, "5 CHARGES", sans_b(9))


BANNERS = {
    "ebola": draw_banner_ebola,
    "cop31": draw_banner_cop31,
    "measles": draw_banner_measles,
    "nvidia": draw_banner_nvidia,
    "gaza": draw_banner_gaza,
    "mongolia": draw_banner_mongolia,
    "serbia": draw_banner_serbia,
    "bangladesh": draw_banner_bangladesh,
    "an12": draw_banner_an12,
    "maputo": draw_banner_maputo,
}


# ------------------------------------------------------- world map ---

CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 71), (-110, 73), (-95, 80), (-85, 76),
     (-80, 73), (-75, 62), (-65, 60), (-60, 47), (-70, 42), (-75, 35),
     (-80, 32), (-85, 28), (-90, 21), (-95, 16), (-100, 15), (-105, 20),
     (-112, 25), (-120, 32), (-125, 40), (-125, 48), (-135, 58),
     (-150, 60), (-165, 60)],
    # Greenland
    [(-58, 64), (-45, 68), (-30, 70), (-22, 76), (-35, 80), (-55, 78),
     (-65, 74)],
    # South America
    [(-79, 9), (-72, 11), (-62, 10), (-52, 5), (-50, 0), (-42, -3),
     (-35, -8), (-38, -15), (-42, -22), (-48, -28), (-55, -34),
     (-62, -39), (-68, -50), (-70, -53), (-74, -44), (-73, -33),
     (-71, -20), (-77, -12), (-80, -5), (-81, 2)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (3, 53), (8, 57), (10, 59),
     (15, 58), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (32, 68),
     (40, 68), (44, 66), (40, 60), (38, 55), (35, 50), (33, 46), (30, 45),
     (28, 44), (23, 40), (19, 42), (15, 44), (12, 44), (8, 44), (3, 42),
     (0, 38), (-2, 37), (-6, 36)],
    # Africa
    [(-10, 30), (-6, 33), (0, 36), (10, 37), (15, 32), (20, 32), (25, 31),
     (30, 31), (32, 28), (35, 27), (38, 22), (40, 18), (43, 12), (48, 11),
     (51, 10), (48, 5), (44, 0), (41, -5), (40, -12), (36, -18), (33, -25),
     (30, -30), (26, -33), (20, -35), (17, -32), (15, -27), (12, -18),
     (12, -10), (9, -2), (9, 4), (4, 6), (-4, 5), (-8, 5), (-13, 8),
     (-16, 12), (-17, 15), (-16, 20), (-14, 25), (-10, 28)],
    # Asia
    [(40, 68), (50, 69), (60, 69), (70, 72), (80, 73), (90, 75), (100, 76),
     (110, 74), (120, 73), (130, 72), (140, 72), (150, 70), (160, 69),
     (170, 67), (178, 65), (170, 60), (162, 58), (158, 52), (150, 45),
     (142, 42), (140, 38), (135, 34), (130, 33), (127, 38), (124, 40),
     (120, 32), (118, 25), (110, 20), (108, 12), (105, 9), (103, 8),
     (100, 8), (98, 10), (95, 16), (92, 21), (89, 22), (86, 20), (82, 17),
     (80, 14), (77, 8), (75, 12), (72, 20), (68, 22), (62, 25), (58, 26),
     (55, 26), (52, 28), (50, 29), (48, 30), (45, 29), (43, 28), (42, 31),
     (40, 35), (40, 42), (40, 48), (40, 55), (40, 62)],
    # Australia
    [(113, -22), (114, -30), (115, -33), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -11), (140, -17),
     (135, -15), (130, -12), (126, -14), (122, -17), (117, -20)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (-2, 51)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (137, 35), (139, 36), (140, 38),
     (141, 40), (142, 43), (144, 44), (142, 42), (140, 39), (138, 36),
     (136, 34), (133, 34), (130, 32)],
    # Indonesia
    [(95, 5), (98, 3), (100, 0), (103, -2), (106, -6), (110, -7), (114, -8),
     (118, -9), (122, -9), (126, -8), (130, -4), (134, -3), (138, -5),
     (140, -8), (136, -7), (132, -4), (128, -3), (124, -1), (120, 1),
     (116, 0), (112, 0), (108, 0), (104, 2), (100, 4), (96, 5)],
    # New Zealand
    [(167, -45), (170, -42), (174, -39), (176, -38), (174, -41), (170, -43),
     (167, -46)],
]


def lonlat_to_xy(lon, lat, mx, my, mw, mh):
    x = mx + (lon + 170) / 360.0 * mw
    y = my + (78 - lat) / 134.0 * mh
    return x, y


def draw_map(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=SEA)
    draw.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    inset = 6
    mx, my, mw, mh = x + inset, y + inset, w - 2 * inset, h - 2 * inset - 26
    for poly in CONTINENTS:
        pts = [lonlat_to_xy(lon, lat, mx, my, mw, mh) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=LAND_LINE)
    for num, region, lon, lat in PINS:
        px, py = lonlat_to_xy(lon, lat, mx, my, mw, mh)
        num_badge(draw, px, py, 9, num, REGION_COLORS[region])
    for num, region, _text, lon, lat in ALSO:
        px, py = lonlat_to_xy(lon, lat, mx, my, mw, mh)
        draw.ellipse([px - 3, py - 3, px + 3, py + 3],
                     fill=REGION_COLORS[region], outline=(255, 255, 255), width=1)
    # legend
    ly = y + h - 24
    items = [("Americas", RED), ("Europe", BLUE), ("Middle East", ORANGE),
             ("Asia", PURPLE), ("Africa", GREEN), ("Oceania", TEAL),
             ("Global & space", DARKPURPLE)]
    font = sans(10)
    lx = x + 8
    for name, color in items:
        draw.ellipse([lx, ly + 2, lx + 7, ly + 9], fill=color)
        lx += 11
        draw.text((lx, ly), name, font=font, fill=INK)
        lx += text_w(draw, name, font) + 10
    font2 = sans(9)
    note = "Pins: stories 1-13  ·  Dots: stories 14-43"
    draw.text((x + 8, ly + 12), note, font=font2, fill=(80, 80, 80))


# ------------------------------------------------------- page layout ---

def draw_masthead(draw, y):
    left = sans_b(13)
    right = sans_b(13)
    draw.text((MARGIN, y), "THE WORLD'S NEWS IN ONE PICTURE",
              font=left, fill=RED)
    rt = "43 STORIES · 6 CONTINENTS · ALL FROM TUESDAY"
    draw.text((W - MARGIN - text_w(draw, rt, right), y), rt,
              font=right, fill=INK)
    title = serif_b(58)
    tt = "Tuesday 17 November 2026"
    draw.text(((W - text_w(draw, tt, title)) / 2, y + 20), tt,
              font=title, fill=INK)
    draw.line([MARGIN, y + 88, W - MARGIN, y + 88], fill=RULE, width=2)


def draw_hero_text(draw, x, y, w, story):
    color = REGION_COLORS[story["region"]]
    num_badge(draw, x + 11, y + 11, 11, story["num"], color)
    kicker = sans_b(11)
    draw.text((x + 28, y + 4), story["kicker"], font=kicker, fill=color)
    lines, hfont = fit_lines(draw, story["headline"], SERIF_BOLD_PATHS, 20, w, 3)
    y = draw_lines(draw, x, y + 26, lines, hfont, INK, 23)
    lines, dfont = fit_lines(draw, story["deck"], SANS_PATHS, 12, w, 2)
    y = draw_lines(draw, x, y + 4, lines, dfont, (50, 50, 50), 15)
    return y


def draw_mid_cell(draw, x, y, w, story):
    BANNERS[story["art"]](draw, x, y, w, 54)
    color = REGION_COLORS[story["region"]]
    kicker = sans_b(10)
    draw.text((x, y + 60), story["kicker"], font=kicker, fill=color)
    lines, hfont = fit_lines(draw, story["headline"], SERIF_BOLD_PATHS, 14, w, 3)
    yy = draw_lines(draw, x, y + 75, lines, hfont, INK, 17)
    lines, dfont = fit_lines(draw, story["deck"], SANS_PATHS, 10, w, 2)
    yy = draw_lines(draw, x, yy + 2, lines, dfont, (50, 50, 50), 13)
    return yy


def draw_also_on(draw, x, y, w):
    head = sans_b(13)
    draw.text((x, y), "ALSO ON TUESDAY 17 NOVEMBER — 30 MORE STORIES",
              font=head, fill=INK)
    col_w = (w - 12) // 2
    font = cond(11)
    row_h = 14.5
    for i, item in enumerate(ALSO):
        num, region, text, _lon, _lat = item
        col = 0 if i < 15 else 1
        row = i if i < 15 else i - 15
        cx = x + col * (col_w + 12)
        cy = y + 22 + row * row_h
        num_badge(draw, cx + 8, cy + 7, 8, num, REGION_COLORS[region])
        max_text_w = col_w - 22
        shown = text
        while shown and text_w(draw, shown, font) > max_text_w:
            shown = shown[:-1]
        if shown != text:
            shown = shown[:-1] + "…"
        draw.text((cx + 20, cy), shown, font=font, fill=INK)


def draw_footer(draw, y):
    draw.line([MARGIN, y, W - MARGIN, y], fill=RULE, width=1)
    size = 10
    while size >= 8:
        font = sans(size)
        left = ("Every story here happened or was first reported on Tuesday "
                "17 November 2026. Contested claims are marked as claims.")
        right = "Sources: Reuters, AP, AFP, BBC, Al Jazeera, WHO, UN. Original drawings."
        if (text_w(draw, left, font) + text_w(draw, right, font)
                <= W - 2 * MARGIN - 24):
            break
        size -= 1
    draw.text((MARGIN, y + 6), left, font=font, fill=(60, 60, 60))
    draw.text((W - MARGIN - text_w(draw, right, font), y + 6), right,
              font=font, fill=(60, 60, 60))


def build():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    draw_masthead(draw, 12)

    hero_y, hero_h = 110, 138
    hero_w = 322
    hero_xs = [MARGIN, MARGIN + hero_w + 13, MARGIN + 2 * (hero_w + 13)]
    for hero, hx in zip(HEROES, hero_xs):
        HERO_ART[hero["art"]](draw, hx, hero_y, hero_w, hero_h)

    text_y = hero_y + hero_h + 8
    for hero, hx in zip(HEROES, hero_xs):
        draw_hero_text(draw, hx, text_y, hero_w, hero)

    mid_y0 = 388
    mid_h = 148
    mid_w = 190
    mid_xs = [MARGIN + i * (mid_w + 10) for i in range(5)]
    for row in range(2):
        for col in range(5):
            story = MIDS[row * 5 + col]
            draw_mid_cell(draw, mid_xs[col], mid_y0 + row * (mid_h + 8),
                          mid_w, story)

    bottom_y = 700
    draw.text((MARGIN, bottom_y), "WHERE IT HAPPENED", font=sans_b(13),
              fill=RED)
    map_x, map_y, map_w, map_h = MARGIN, bottom_y + 22, 460, 218
    draw_map(draw, map_x, map_y, map_w, map_h)
    draw_also_on(draw, 492, bottom_y, W - MARGIN - 492)

    draw_footer(draw, 952)
    return img


def main():
    img = build()
    here = os.path.dirname(os.path.abspath(__file__))
    local_path = os.path.join(here, "entry.png")
    img.save(local_path, format="PNG", optimize=True)
    size = os.path.getsize(local_path)
    if size > 1048576:
        img.save(local_path, format="JPEG", quality=90)
        size = os.path.getsize(local_path)
    try:
        os.makedirs("/output", exist_ok=True)
        img.save("/output/entry.png", format="PNG", optimize=True)
        if os.path.getsize("/output/entry.png") > 1048576:
            img.save("/output/entry.png", format="JPEG", quality=90)
    except Exception:
        pass
    print("entry.png: %dx%d %d bytes" % (img.size[0], img.size[1], size))
    assert img.size == (1024, 1024), "size must be 1024x1024"
    assert size <= 1048576, "file must be at most 1 MiB"


if __name__ == "__main__":
    main()
