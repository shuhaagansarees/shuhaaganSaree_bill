import sys
sys.path.append('.')
from billing import generate_pdf
import fitz

test_data = [
    {
        "id": "TEST-1",
        "items": [
            {
                "customer_name": "Test User 1",
                "customer_phone": "9876543210",
                "item_name": "Red Saree",
                "qty": 1,
                "price": 1200,
                "upi_id": None
            }
        ]
    },
    {
        "id": "TEST-2",
        "items": [
            {
                "customer_name": "Test User 2",
                "customer_phone": "9876543211",
                "item_name": "Silk Saree",
                "qty": 1,
                "price": 2500,
                "upi_id": "test2@upi"
            },
            {
                "customer_name": "Test User 2",
                "customer_phone": "9876543211",
                "item_name": "Cotton Saree",
                "qty": 1,
                "price": 800,
                "upi_id": "test2@upi"
            },
            {
                "customer_name": "Test User 2",
                "customer_phone": "9876543211",
                "item_name": "Designer Blouse",
                "qty": 1,
                "price": 450,
                "upi_id": "test2@upi"
            }
        ]
    },
    {
        "id": "TEST-3",
        "items": [
            {
                "customer_name": "Wholesale Buyer",
                "customer_phone": "9876543212",
                "item_name": "Bulk Sarees",
                "qty": 59,
                "price": 500,
                "upi_id": "test3@upi"
            }
        ]
    }
]

for t in test_data:
    inv = t["id"]
    pdf_path, _ = generate_pdf(inv, t["items"])
    print(f"Generated {pdf_path}")
    doc = fitz.open(pdf_path)
    png_path = f"invoices/{inv}_preview.png"
    doc[0].get_pixmap(dpi=200).save(png_path)
    doc.close()
    print(f"Saved {png_path}")
