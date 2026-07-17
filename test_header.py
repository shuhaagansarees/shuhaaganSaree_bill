import sys, textwrap
sys.path.append('.')
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import config

c = canvas.Canvas('dummy.pdf', pagesize=A4)
w, h = A4
margin = 8 * mm
border_thickness = 8 * mm
content_left = margin + border_thickness + 3 * mm
content_right = w - margin - border_thickness - 3 * mm

logo_w = 46 * mm
logo_x = content_left + 4 * mm
title_x = logo_x + logo_w + 6 * mm
contact_right = content_right - 4 * mm

right_widths = []
right_widths.extend(c.stringWidth(p, "Helvetica-Bold", 11) for p in config.SHOP_PHONES)
if hasattr(config, "SHOP_GST") and config.SHOP_GST:
    right_widths.append(c.stringWidth("GST : " + config.SHOP_GST, "Helvetica-Bold", 10))

addr1_full = f"{config.SHOP_ADDRESSES[0][0]}: {config.SHOP_ADDRESSES[0][1]}"
for addr_line in textwrap.wrap(addr1_full, 48):
    right_widths.append(c.stringWidth(addr_line, "Helvetica", 8))

addr2_full = f"{config.SHOP_ADDRESSES[1][0]}: {config.SHOP_ADDRESSES[1][1]}"
for addr_line in textwrap.wrap(addr2_full, 48):
    right_widths.append(c.stringWidth(addr_line, "Helvetica", 8))

right_widths.append(c.stringWidth(config.EMAIL, "Helvetica", 8))
icon_size = 4 * mm
right_widths.append(c.stringWidth(config.INSTAGRAM, "Helvetica", 8) + icon_size + 1.5 * mm)

max_right_w = max(right_widths)
contact_left_bound = contact_right - max_right_w
allowed_left_w = contact_left_bound - title_x - 5 * mm

title_size = 26
saree_size = 14
tagline_size = 9
cat_size = 7

cat_parts = config.CATEGORIES.split('\u2022')
cat_lines = []
current_line = ""
for part in cat_parts:
    part = part.strip()
    test_line = f"{current_line} \u2022 {part}".strip(" \u2022")
    if c.stringWidth(test_line, "Helvetica-Bold", cat_size) < allowed_left_w:
        current_line = test_line
    else:
        if current_line:
            cat_lines.append(current_line)
        current_line = part
if current_line:
    cat_lines.append(current_line)

while title_size > 12:
    if c.stringWidth("SHUHAAGAN", "Times-Bold", title_size) <= allowed_left_w and \
       c.stringWidth("SAREE", "Times-Bold", saree_size) <= allowed_left_w and \
       c.stringWidth(config.TAGLINE, "Times-Italic", tagline_size) <= allowed_left_w:
        break
    title_size -= 1
    saree_size = max(10, title_size - 10)
    tagline_size = max(7, tagline_size - 0.5)

max_left_w = max([
    c.stringWidth("SHUHAAGAN", "Times-Bold", title_size),
    c.stringWidth("SAREE", "Times-Bold", saree_size),
    c.stringWidth(config.TAGLINE, "Times-Italic", tagline_size),
] + [c.stringWidth(cl, "Helvetica-Bold", cat_size) for cl in cat_lines])

left_right_bound = title_x + max_left_w
print(f"Right Col Left: {contact_left_bound:.2f}, Left Col Right: {left_right_bound:.2f}, Gap: {contact_left_bound - left_right_bound:.2f}, Title Size: {title_size}pt")
print("cat_lines count:", len(cat_lines))
