import sqlite3
import os
import config
from datetime import datetime

DB_PATH = os.path.join(config.BASE_DIR, "billing.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            phone TEXT PRIMARY KEY,
            name TEXT
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            invoice_no TEXT PRIMARY KEY,
            created_at TIMESTAMP,
            customer_phone TEXT,
            total_amount REAL,
            discount_percent INTEGER DEFAULT 0,
            gst_rate REAL DEFAULT 5,
            FOREIGN KEY (customer_phone) REFERENCES customers(phone)
        )
    ''')
    
    # Auto-migration: add columns if they don't exist (for old databases)
    try:
        c.execute("ALTER TABLE invoices ADD COLUMN discount_percent INTEGER DEFAULT 0")
    except Exception:
        pass  # Column already exists
    try:
        c.execute("ALTER TABLE invoices ADD COLUMN gst_rate REAL DEFAULT 5")
    except Exception:
        pass  # Column already exists
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_no TEXT,
            item_name TEXT,
            hsn TEXT,
            qty INTEGER,
            price REAL,
            line_total REAL,
            FOREIGN KEY (invoice_no) REFERENCES invoices(invoice_no)
        )
    ''')
    conn.commit()
    conn.close()

def get_customer(phone):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT name FROM customers WHERE phone = ?", (phone,))
    row = c.fetchone()
    conn.close()
    return row['name'] if row else None

def save_customer(phone, name):
    if not phone:
        return
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO customers (phone, name) 
        VALUES (?, ?)
        ON CONFLICT(phone) DO UPDATE SET name=excluded.name
    ''', (phone, name))
    conn.commit()
    conn.close()

def generate_new_invoice_no():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT invoice_no FROM invoices ORDER BY rowid DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    if not row:
        return "INV-1001"
    last_inv = row['invoice_no']
    try:
        num = int(last_inv.split("-")[1])
        return f"INV-{num + 1}"
    except:
        return f"INV-{int(datetime.now().timestamp())}"

def save_invoice(invoice_no, customer_phone, items, discount_percent=0, gst_rate=5):
    conn = get_db()
    c = conn.cursor()
    
    subtotal = sum(item.get('line_total', 0) for item in items)
    discount_amount = subtotal * (discount_percent / 100)
    taxable = subtotal - discount_amount
    gst_amount = taxable * (gst_rate / 100)
    total_amount = taxable + gst_amount
    
    c.execute('''
        INSERT INTO invoices (invoice_no, created_at, customer_phone, total_amount, discount_percent, gst_rate)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (invoice_no, datetime.now(), customer_phone, total_amount, discount_percent, gst_rate))
    
    for item in items:
        c.execute('''
            INSERT INTO invoice_items (invoice_no, item_name, hsn, qty, price, line_total)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            invoice_no, 
            item.get('item_name', ''), 
            item.get('hsn', ''), 
            item.get('qty', 0), 
            item.get('price', 0), 
            item.get('line_total', 0)
        ))
        
    conn.commit()
    conn.close()
    return invoice_no, total_amount

def get_invoice_with_items(invoice_no):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT i.invoice_no, i.created_at, i.total_amount, i.discount_percent, i.gst_rate, c.phone, c.name
        FROM invoices i
        LEFT JOIN customers c ON i.customer_phone = c.phone
        WHERE i.invoice_no = ?
    ''', (invoice_no,))
    inv_row = c.fetchone()
    if not inv_row:
        conn.close()
        return None
        
    c.execute('''
        SELECT item_name, hsn, qty, price, line_total
        FROM invoice_items
        WHERE invoice_no = ?
    ''', (invoice_no,))
    item_rows = c.fetchall()
    conn.close()
    
    items = []
    for row in item_rows:
        items.append({
            'item_name': row['item_name'],
            'hsn': row['hsn'],
            'qty': row['qty'],
            'price': row['price'],
            'line_total': row['line_total']
        })
        
    try:
        discount_percent = inv_row['discount_percent'] or 0
    except (IndexError, KeyError):
        discount_percent = 0
    try:
        gst_rate = inv_row['gst_rate'] or 5
    except (IndexError, KeyError):
        gst_rate = 5
        
    return {
        'invoice_no': inv_row['invoice_no'],
        'date': inv_row['created_at'],
        'customer_name': inv_row['name'],
        'customer_phone': inv_row['phone'],
        'total_amount': inv_row['total_amount'],
        'discount_percent': discount_percent,
        'gst_rate': gst_rate,
        'items': items
    }

def get_recent_invoices(limit=50):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT i.invoice_no, i.created_at, i.total_amount, c.name, c.phone
        FROM invoices i
        LEFT JOIN customers c ON i.customer_phone = c.phone
        ORDER BY i.created_at DESC
        LIMIT ?
    ''', (limit,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_sales_metrics():
    conn = get_db()
    c = conn.cursor()
    
    now = datetime.now()
    today_start = now.strftime('%Y-%m-%d 00:00:00')
    month_start = now.strftime('%Y-%m-01 00:00:00')
    
    c.execute("SELECT SUM(total_amount) as total, COUNT(invoice_no) as count FROM invoices WHERE created_at >= ?", (today_start,))
    today_data = c.fetchone()
    
    c.execute("SELECT SUM(total_amount) as total, COUNT(invoice_no) as count FROM invoices WHERE created_at >= ?", (month_start,))
    month_data = c.fetchone()
    
    c.execute("SELECT SUM(total_amount) as total, COUNT(invoice_no) as count FROM invoices")
    all_time_data = c.fetchone()
    
    conn.close()
    
    return {
        'today': today_data['total'] or 0,
        'today_count': today_data['count'] or 0,
        'month': month_data['total'] or 0,
        'month_count': month_data['count'] or 0,
        'all_time': all_time_data['total'] or 0,
        'all_time_count': all_time_data['count'] or 0
    }

def delete_invoice(invoice_no):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM invoice_items WHERE invoice_no = ?", (invoice_no,))
    c.execute("DELETE FROM invoices WHERE invoice_no = ?", (invoice_no,))
    conn.commit()
    conn.close()
