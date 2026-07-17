import os

content = """import base64
import logging
import os
import sys
import threading
import webbrowser
from datetime import datetime

from flask import Flask, render_template_string, redirect, url_for, send_file, abort, request, jsonify
from werkzeug.exceptions import HTTPException

import config
import billing
import database

app = Flask(__name__)

logging.basicConfig(
    filename=config.LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logging.info("App starting. BASE_DIR=%s", config.BASE_DIR)

# Initialize DB
database.init_db()

def _logo_data_uri():
    try:
        if os.path.exists(config.LOGO_PATH):
            with open(config.LOGO_PATH, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("ascii")
            return f"data:image/png;base64,{b64}"
    except Exception:
        logging.exception("Could not load logo")
    return ""

PAGE_STYLE = '''
<style>
  body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4ecec; margin: 0; padding: 20px; }
  .container { max-width: 900px; margin: 0 auto; background: white; padding: 0;
               border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); overflow: hidden; }
  .brand-header { background: linear-gradient(135deg, #8B0000, #D4AF37); color: white;
                  padding: 20px 28px; display: flex; align-items: center; justify-content: space-between; }
  .header-left { display: flex; align-items: center; gap: 16px; }
  .brand-header img { height: 50px; width: 50px; border-radius: 8px; background: white;
                       object-fit: contain; padding: 4px; }
  .brand-header h1 { margin: 0; font-size: 22px; text-shadow: 1px 1px 2px rgba(0,0,0,0.3); }
  
  .tabs { display: flex; background: #333; }
  .tab { flex: 1; text-align: center; padding: 12px; color: white; cursor: pointer; font-weight: bold; text-decoration: none; }
  .tab:hover { background: #555; }
  .tab.active { background: #8B0000; }
  
  .body-pad { padding: 25px; }
  
  .form-group { margin-bottom: 15px; }
  .form-group label { display: block; font-weight: bold; margin-bottom: 5px; color: #555; font-size: 14px;}
  .form-control { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; font-size: 15px;}
  .form-row { display: flex; gap: 15px; }
  .form-row > div { flex: 1; }
  
  table.items-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
  table.items-table th, table.items-table td { border: 1px solid #ddd; padding: 10px; text-align: left; }
  table.items-table th { background: #f9f9f9; font-weight: bold; color: #333; }
  table.items-table input { width: 100%; padding: 6px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
  
  .btn { background: #8B0000; color: white; border: none; padding: 10px 20px;
         border-radius: 6px; cursor: pointer; font-size: 15px; font-weight: bold; text-decoration: none; display: inline-block;}
  .btn:hover { background: #600000; }
  .btn-green { background: #2e7d32; }
  .btn-green:hover { background: #1b5e20; }
  .btn-blue { background: #1976d2; }
  .btn-blue:hover { background: #115293; }
  
  .dashboard-cards { display: flex; gap: 20px; margin-bottom: 25px; }
  .card { flex: 1; background: #fffdfa; border: 1px solid #eadfd2; border-left: 5px solid #C9A24B; padding: 20px; border-radius: 8px; }
  .card h3 { margin: 0 0 10px 0; color: #555; font-size: 14px; text-transform: uppercase;}
  .card .value { font-size: 24px; font-weight: bold; color: #8B0000; }
  
  .invoice-list { border: 1px solid #eee; border-radius: 8px; overflow: hidden; }
  .invoice-row { display: flex; justify-content: space-between; padding: 12px 15px; border-bottom: 1px solid #eee; }
  .invoice-row:last-child { border-bottom: none; }
  .invoice-row:nth-child(even) { background: #fafafa; }
  
  .dash-footer { background: #f9f4f4; padding: 15px 28px; font-size: 12px; color: #555;
                 border-top: 1px solid #eadfd2; line-height: 1.5; text-align: center; }
</style>
'''

HEADER_BLOCK = '''
<div class="brand-header">
  <div class="header-left">
    {% if logo %}<img src="{{ logo }}" alt="logo">{% endif %}
    <div>
      <h1>{{ shop_name }}</h1>
    </div>
  </div>
</div>
<div class="tabs">
  <a href="/" class="tab {% if active_tab == 'create' %}active{% endif %}">Create Bill</a>
  <a href="/dashboard" class="tab {% if active_tab == 'dashboard' %}active{% endif %}">Dashboard & Sales</a>
</div>
'''

CREATE_TEMPLATE = PAGE_STYLE + '''
<html><head><title>Create Bill - {{ shop_name }}</title></head>
<body>
<div class="container">
  ''' + HEADER_BLOCK + '''
  <div class="body-pad">
    <form action="/generate_new" method="POST" id="billForm">
      
      <div class="card" style="margin-bottom:20px;">
          <h3 style="color:#8B0000; margin-bottom:15px; border-bottom:1px solid #eee; padding-bottom:10px;">Customer Details</h3>
          <div class="form-row">
            <div class="form-group">
              <label>Mobile Number</label>
              <input type="text" name="customer_phone" id="customer_phone" class="form-control" placeholder="10-digit number" required onblur="fetchCustomer()">
            </div>
            <div class="form-group">
              <label>Customer Name</label>
              <input type="text" name="customer_name" id="customer_name" class="form-control" placeholder="Auto-filled if exists" required>
            </div>
          </div>
      </div>
      
      <div class="card">
          <h3 style="color:#8B0000; margin-bottom:15px; border-bottom:1px solid #eee; padding-bottom:10px;">Bill Items</h3>
          <table class="items-table" id="itemsTable">
            <thead>
              <tr>
                <th>Item Description</th>
                <th style="width: 15%;">HSN Code</th>
                <th style="width: 10%;">Qty</th>
                <th style="width: 15%;">Rate (Rs)</th>
                <th style="width: 15%;">Total (Rs)</th>
                <th style="width: 5%;"></th>
              </tr>
            </thead>
            <tbody id="itemsBody">
            </tbody>
          </table>
          <button type="button" class="btn" style="background:#555; margin-top:10px;" onclick="addRow()">+ Add Item</button>
      </div>
      
      <div style="text-align:right; margin-top: 20px;">
        <h2 style="color:#8B0000; margin: 0 0 15px 0;">Grand Total: Rs. <span id="grandTotal">0.00</span></h2>
        <button type="submit" class="btn btn-green" style="font-size: 18px; padding: 12px 30px;" id="generateBtn">Generate Bill & PDF</button>
      </div>
      
    </form>
  </div>
</div>

<script>
let rowCount = 0;
function addRow() {
    rowCount++;
    const tr = document.createElement('tr');
    tr.id = 'row_' + rowCount;
    tr.innerHTML = `
        <td><input type="text" name="item_name[]" required></td>
        <td><input type="text" name="hsn[]"></td>
        <td><input type="number" name="qty[]" value="1" min="1" onchange="calc(${rowCount})" onkeyup="calc(${rowCount})" required></td>
        <td><input type="number" step="0.01" name="price[]" value="0" onchange="calc(${rowCount})" onkeyup="calc(${rowCount})" required></td>
        <td><input type="number" step="0.01" name="line_total[]" readonly style="background:#eee;"></td>
        <td><button type="button" onclick="removeRow(${rowCount})" style="background:red; color:white; border:none; border-radius:4px; padding:5px; cursor:pointer;">X</button></td>
    `;
    document.getElementById('itemsBody').appendChild(tr);
}

function removeRow(id) {
    document.getElementById('row_' + id).remove();
    calcGrandTotal();
}

function calc(id) {
    const row = document.getElementById('row_' + id);
    const qty = parseFloat(row.querySelector('input[name="qty[]"]').value) || 0;
    const price = parseFloat(row.querySelector('input[name="price[]"]').value) || 0;
    const total = qty * price;
    row.querySelector('input[name="line_total[]"]').value = total.toFixed(2);
    calcGrandTotal();
}

function calcGrandTotal() {
    let total = 0;
    const totals = document.querySelectorAll('input[name="line_total[]"]');
    totals.forEach(t => {
        total += parseFloat(t.value) || 0;
    });
    document.getElementById('grandTotal').innerText = total.toFixed(2);
}

function fetchCustomer() {
    const phone = document.getElementById('customer_phone').value.trim();
    if (phone.length >= 10) {
        fetch('/api/customer/' + phone)
            .then(r => r.json())
            .then(data => {
                if (data.name) {
                    document.getElementById('customer_name').value = data.name;
                }
            });
    }
}

// Add first row by default
addRow();
</script>
</body></html>
'''

DASHBOARD_TEMPLATE = PAGE_STYLE + '''
<html><head><title>Dashboard - {{ shop_name }}</title></head>
<body>
<div class="container">
  ''' + HEADER_BLOCK + '''
  <div class="body-pad">
    <h2 style="margin-top:0; color:#333;">Sales Overview</h2>
    <div class="dashboard-cards">
      <div class="card">
        <h3>Today's Sales</h3>
        <div class="value">Rs. {{ metrics.today | round(2) }}</div>
        <div style="font-size:12px; color:#777; margin-top:5px;">{{ metrics.today_count }} bills generated</div>
      </div>
      <div class="card">
        <h3>This Month</h3>
        <div class="value">Rs. {{ metrics.month | round(2) }}</div>
        <div style="font-size:12px; color:#777; margin-top:5px;">{{ metrics.month_count }} bills generated</div>
      </div>
      <div class="card">
        <h3>All Time</h3>
        <div class="value">Rs. {{ metrics.all_time | round(2) }}</div>
        <div style="font-size:12px; color:#777; margin-top:5px;">{{ metrics.all_time_count }} bills total</div>
      </div>
    </div>
    
    <h2 style="color:#333;">Recent Bills</h2>
    <div class="invoice-list">
      {% for inv in recent_invoices %}
      <div class="invoice-row">
        <div>
          <strong>{{ inv.invoice_no }}</strong> <span style="color:#777; font-size:13px; margin-left:10px;">{{ inv.created_at[:10] }}</span><br>
          <span style="font-size:14px;">{{ inv.name }} ({{ inv.phone }})</span>
        </div>
        <div style="text-align:right;">
          <div style="font-weight:bold; color:#8B0000;">Rs. {{ inv.total_amount | round(2) }}</div>
          <a href="/success/{{ inv.invoice_no }}" style="font-size:12px; color:#1976d2; text-decoration:none;">View & Print &rarr;</a>
        </div>
      </div>
      {% else %}
      <div style="padding:20px; text-align:center; color:#777;">No bills generated yet.</div>
      {% endfor %}
    </div>
  </div>
</div>
</body></html>
'''

SUCCESS_TEMPLATE = PAGE_STYLE + '''
<html><head><title>Bill Ready - {{ shop_name }}</title></head>
<body>
<div class="container">
  ''' + HEADER_BLOCK + '''
  <div class="body-pad" style="text-align:center; padding: 40px 20px;">
    <div style="display:inline-block; background: #e8f5e9; color:#2e7d32; padding:15px; border-radius:50%; margin-bottom:15px;">
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
    </div>
    <h1 style="color:#2e7d32; margin:0 0 10px 0;">Bill Generated Successfully!</h1>
    <h3 style="color:#555; margin:0 0 30px 0;">Invoice No: {{ invoice_no }} | Total: Rs. {{ total_amount }}</h3>
    
    <div style="display:flex; justify-content:center; gap:15px; flex-wrap:wrap;">
      <a href="/download/{{ invoice_no }}" class="btn btn-blue" target="_blank">📄 View/Download PDF</a>
      
      <!-- Print directly opens the PDF and calls print -->
      <a href="/download/{{ invoice_no }}" class="btn" style="background:#424242;" target="_blank" onclick="setTimeout(() => window.print(), 1000);">🖨️ Print Bill</a>
      
      {% set wa_msg = "Hello " + customer_name + ",%0a%0aThank you for shopping at " + shop_name + "!%0aYour bill amount is Rs. " + (total_amount|string) + ".%0a%0aRegards,%0a" + shop_name %}
      <a href="https://wa.me/91{{ customer_phone }}?text={{ wa_msg }}" class="btn btn-green" target="_blank">💬 Send via WhatsApp</a>
    </div>
    
    <div style="margin-top:40px;">
      <a href="/" style="color:#8B0000; font-weight:bold; text-decoration:none;">&larr; Create Another Bill</a>
    </div>
  </div>
</div>
</body></html>
'''

@app.route("/")
def index():
    return render_template_string(CREATE_TEMPLATE, shop_name=config.SHOP_NAME, logo=_logo_data_uri(), active_tab='create')

@app.route("/dashboard")
def dashboard():
    metrics = database.get_sales_metrics()
    recent_invoices = database.get_recent_invoices(20)
    return render_template_string(DASHBOARD_TEMPLATE, shop_name=config.SHOP_NAME, logo=_logo_data_uri(), active_tab='dashboard', metrics=metrics, recent_invoices=recent_invoices)

@app.route("/api/customer/<phone>")
def api_customer(phone):
    name = database.get_customer(phone)
    return jsonify({"name": name or ""})

@app.route("/generate_new", methods=["POST"])
def generate_new():
    phone = request.form.get("customer_phone")
    name = request.form.get("customer_name")
    
    item_names = request.form.getlist("item_name[]")
    hsns = request.form.getlist("hsn[]")
    qtys = request.form.getlist("qty[]")
    prices = request.form.getlist("price[]")
    line_totals = request.form.getlist("line_total[]")
    
    database.save_customer(phone, name)
    invoice_no = database.generate_new_invoice_no()
    
    items = []
    for i in range(len(item_names)):
        items.append({
            "item_name": item_names[i],
            "hsn": hsns[i] if i < len(hsns) else "",
            "qty": float(qtys[i] or 1),
            "price": float(prices[i] or 0),
            "line_total": float(line_totals[i] or 0)
        })
    
    # Save to DB
    database.save_invoice(invoice_no, phone, items)
    
    # Generate PDF
    # Convert DB items format to what billing.py expects
    billing_items = []
    for item in items:
        billing_items.append({
            "Item Name": item["item_name"],
            "HSN": item["hsn"],
            "Qty": item["qty"],
            "Price": item["price"],
            "Line Total": item["line_total"]
        })
    
    pdf_path, total_amount = billing.generate_pdf(invoice_no, billing_items, customer_name=name, customer_phone=phone)
    
    return redirect(url_for("success", invoice_no=invoice_no))

@app.route("/success/<invoice_no>")
def success(invoice_no):
    inv_data = database.get_invoice_with_items(invoice_no)
    if not inv_data:
        abort(404)
    return render_template_string(SUCCESS_TEMPLATE, 
        invoice_no=invoice_no, 
        total_amount=inv_data['total_amount'],
        customer_name=inv_data['customer_name'],
        customer_phone=inv_data['customer_phone'],
        shop_name=config.SHOP_NAME, 
        logo=_logo_data_uri(),
        active_tab='create'
    )

@app.route("/download/<invoice_no>")
def download(invoice_no):
    pdf_path = os.path.join(config.PDF_FOLDER, f"{invoice_no}.pdf")
    if not os.path.exists(pdf_path):
        abort(404, "PDF not found.")
    return send_file(pdf_path, as_attachment=False)  # inline viewing so print works

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000/")

if __name__ == "__main__":
    t = threading.Timer(1.0, open_browser)
    t.start()
    app.run(host="127.0.0.1", port=5000, debug=False)
"""

with open('app_new.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("app_new.py written!")
