import re

with open("billing.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update function signature and total_amount calculation
old_sig = """def generate_pdf(invoice_no, items):
    \"\"\"Generates a bill-book style branded PDF invoice matching the physical
    Shuhaagan Saree bill book design.  Returns (pdf_path, total_amount).\"\"\"
    customer_name = items[0]["customer_name"]
    customer_phone = items[0]["customer_phone"]
    upi_id = items[0]["upi_id"]

    total_amount = sum((it["qty"] or 0) * (it["price"] or 0) for it in items)"""

new_sig = """def generate_pdf(invoice_no, items, discount_percent=0, gst_rate=5):
    \"\"\"Generates a bill-book style branded PDF invoice matching the physical
    Shuhaagan Saree bill book design.  Returns (pdf_path, total_amount).\"\"\"
    customer_name = items[0]["customer_name"]
    customer_phone = items[0]["customer_phone"]
    upi_id = items[0]["upi_id"]

    subtotal = sum((it["qty"] or 0) * (it["price"] or 0) for it in items)
    discount_amount = subtotal * (discount_percent / 100)
    taxable = subtotal - discount_amount
    gst_amount = taxable * (gst_rate / 100)
    total_amount = taxable + gst_amount"""

content = content.replace(old_sig, new_sig)


# 2. Update the "TOTAL AMOUNT row" drawing section
old_total_draw = """    # ── TOTAL AMOUNT row ──
    total_row_y = nr_y
    c.setFillColor(MAROON)
    c.setFont("Helvetica-Bold", 14)
    formatted_total = format_indian_rupee(total_amount)
    
    label_str = "TOTAL AMOUNT"
    total_str = f"Rs. {formatted_total}"
    
    label_w = c.stringWidth(label_str, "Helvetica-Bold", 14)
    total_w = c.stringWidth(total_str, "Helvetica-Bold", 14)
    
    value_x = col_amt_right - col_pad
    value_left = value_x - total_w
    label_x = col_pcs_x
    label_right = label_x + label_w
    
    if label_right > value_left - 8 * mm:
        c.drawRightString(value_x, total_row_y, f"{label_str}      {total_str}")
        print(f"Total row overlapped. Combined to right. Gap was: {value_left - label_right:.2f}")
    else:
        c.drawString(label_x, total_row_y, label_str)
        c.drawRightString(value_x, total_row_y, total_str)
        print(f"Total row fits. Gap: {value_left - label_right:.2f}")

    # Gold line under total
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.line(content_left, total_row_y - 4 * mm,
           content_right, total_row_y - 4 * mm)"""

new_total_draw = """    # ── TOTAL BREAKDOWN ──
    c.setFillColor(HexColor("#333333"))
    c.setFont("Helvetica", 10)
    
    breakdown_y = nr_y + 10 * mm
    label_x = col_rate_x
    value_x = col_amt_right - col_pad
    
    if discount_percent > 0 or gst_rate > 0:
        c.drawString(label_x, breakdown_y, "Subtotal:")
        c.drawRightString(value_x, breakdown_y, f"Rs. {format_indian_rupee(subtotal)}")
        breakdown_y -= 5 * mm
        
    if discount_percent > 0:
        c.drawString(label_x, breakdown_y, f"Discount ({discount_percent}%):")
        c.drawRightString(value_x, breakdown_y, f"- Rs. {format_indian_rupee(discount_amount)}")
        breakdown_y -= 5 * mm
        
        c.drawString(label_x, breakdown_y, "Taxable Value:")
        c.drawRightString(value_x, breakdown_y, f"Rs. {format_indian_rupee(taxable)}")
        breakdown_y -= 5 * mm
        
    if gst_rate > 0:
        half_gst = gst_rate / 2
        c.drawString(label_x, breakdown_y, f"CGST ({half_gst}%):")
        c.drawRightString(value_x, breakdown_y, f"Rs. {format_indian_rupee(gst_amount / 2)}")
        breakdown_y -= 5 * mm
        
        c.drawString(label_x, breakdown_y, f"SGST ({half_gst}%):")
        c.drawRightString(value_x, breakdown_y, f"Rs. {format_indian_rupee(gst_amount / 2)}")
        breakdown_y -= 5 * mm
        
    # ── GRAND TOTAL row ──
    total_row_y = breakdown_y - 2 * mm
    c.setFillColor(MAROON)
    c.setFont("Helvetica-Bold", 14)
    formatted_total = format_indian_rupee(total_amount)
    
    c.drawString(label_x, total_row_y, "GRAND TOTAL")
    c.drawRightString(value_x, total_row_y, f"Rs. {formatted_total}")

    # Gold line under total
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.line(content_left, total_row_y - 4 * mm,
           content_right, total_row_y - 4 * mm)
    
    # Update nr_y so QR code places correctly
    nr_y = total_row_y"""

content = content.replace(old_total_draw, new_total_draw)

with open("billing.py", "w", encoding="utf-8") as f:
    f.write(content)
print("billing.py patched successfully")
