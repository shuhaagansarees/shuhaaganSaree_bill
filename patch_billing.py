import os
import re

with open("billing.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add Watermark just after drawing the interior rect
watermark_code = """
    # ================================================================
    #  WATERMARK
    # ================================================================
    c.saveState()
    c.translate(w / 2, h / 2)
    c.rotate(30)
    c.setFont("Times-Bold", 80)
    c.setFillColorRGB(0.95, 0.95, 0.95)  # Faint grey
    c.drawCentredString(0, 0, "SHUHAAGAN SAREE")
    c.restoreState()
"""
content = content.replace("    c.rect(margin + border_thickness, margin + border_thickness,\n           w - 2 * margin - 2 * border_thickness,\n           h - 2 * margin - 2 * border_thickness,\n           fill=1, stroke=0)", 
                          "    c.rect(margin + border_thickness, margin + border_thickness,\n           w - 2 * margin - 2 * border_thickness,\n           h - 2 * margin - 2 * border_thickness,\n           fill=1, stroke=0)\n" + watermark_code)

# 2. Add HSN calculations
hsn_calcs = """
    hsn_test = "99999999"
    hsn_need = c.stringWidth(hsn_test, table_font, table_font_size) + 2 * col_pad
    hsn_hdr = c.stringWidth("HSN", "Helvetica-Bold", 10) + 2 * col_pad
    hsn_col_w = max(hsn_need, hsn_hdr)
"""
content = content.replace('    pcs_test = "999"', hsn_calcs + '\n    pcs_test = "999"')

hsn_layout = """
    col_amt_right = content_right               # AMOUNT right edge = content_right
    col_amt_x = col_amt_right - amt_col_w       # AMOUNT left edge
    col_rate_right = col_amt_x                   # RATE right edge
    col_rate_x = col_rate_right - rate_col_w     # RATE left edge
    col_pcs_right = col_rate_x                   # PCS right edge
    col_pcs_x = col_pcs_right - pcs_col_w        # PCS left edge
    col_hsn_right = col_pcs_x
    col_hsn_x = col_hsn_right - hsn_col_w
"""
content = re.sub(r'    col_amt_right = content_right.*?col_pcs_x = col_pcs_right - pcs_col_w\s+# PCS left edge', hsn_layout.strip('\n'), content, flags=re.DOTALL)

# Update description end
content = content.replace("    col_desc_x = content_left + no_col_w\n\n", "    col_desc_x = content_left + no_col_w\n\n")

# Draw headers
header_draw = """
    c.drawString(col_desc_x + col_pad, hdr_text_y, "DESCRIPTION")
    c.drawString(col_hsn_x + col_pad, hdr_text_y, "HSN")
    c.drawString(col_pcs_x + col_pad, hdr_text_y, "PCS.")
"""
content = content.replace('    c.drawString(col_desc_x + col_pad, hdr_text_y, "DESCRIPTION")\n    c.drawString(col_pcs_x + col_pad, hdr_text_y, "PCS.")', header_draw.strip('\n'))

# Header line
content = content.replace('    c.line(col_pcs_x, table_top, col_pcs_x, table_top - 180 * mm)', '    c.line(col_hsn_x, table_top, col_hsn_x, table_top - 180 * mm)\n    c.line(col_pcs_x, table_top, col_pcs_x, table_top - 180 * mm)')

# Item rows drawing
item_draw = """
        c.drawString(col_no_x + col_pad, row_y, str(idx))
        desc_text = str(item.get("Item Name", ""))
        
        # We need to wrap the description if it exceeds col_hsn_x - col_desc_x
        max_desc_w = (col_hsn_x - col_desc_x) - 2 * col_pad
        desc_lines = wrap_text(c, desc_text, table_font, table_font_size, max_desc_w)
        
        dy = 0
        for line in desc_lines:
            c.drawString(col_desc_x + col_pad, row_y - dy, line)
            dy += 4 * mm

        c.drawString(col_hsn_x + col_pad, row_y, str(item.get("HSN", "")))
        c.drawString(col_pcs_x + col_pad, row_y, str(item.get("Qty", "")))
"""
content = re.sub(r'        c\.drawString\(col_no_x \+ col_pad, row_y, str\(idx\)\).*?c\.drawString\(col_pcs_x \+ col_pad, row_y, str\(item\.get\("Qty", ""\)\)\)', item_draw.strip('\n'), content, flags=re.DOTALL)

# Terms and conditions at the bottom
tc_code = """
    # ================================================================
    #  TERMS & CONDITIONS
    # ================================================================
    c.setFillColor(HexColor("#444444"))
    c.setFont("Helvetica-Bold", 9)
    c.drawString(content_left + 4 * mm, content_bot + 24 * mm, "Terms & Conditions:")
    c.setFont("Helvetica", 8)
    c.drawString(content_left + 4 * mm, content_bot + 19 * mm, "1. Goods once sold will not be taken back.")
    c.drawString(content_left + 4 * mm, content_bot + 14 * mm, "2. Exchange allowed within 7 days with bill only.")
    c.drawString(content_left + 4 * mm, content_bot + 9 * mm, "3. Subject to Surat jurisdiction.")
"""
content = content.replace('    # ================================================================', tc_code + '\n    # ================================================================', 1)

# Oh wait, replacing the first instance of '    # ================================================================' will put it at the top of the file!
# Let's fix that.
content = content.replace(tc_code + '\n', '') # remove it if it was added

# We should add it right before "    c.save()"
content = content.replace("    c.save()", tc_code + "\n    c.save()")


with open("billing.py", "w", encoding="utf-8") as f:
    f.write(content)
print("billing.py patched successfully")
