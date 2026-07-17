import os
import sys

# ---------- FILE LOCATIONS ----------
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
    _INTERNAL_DIR = os.path.join(BASE_DIR, "_internal")
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    _INTERNAL_DIR = BASE_DIR

# ---------- SHOP DETAILS ----------
SHOP_NAME = "Shuhaagan Sarees"
SHOP_BRAND_TITLE = "SHUHAAGAN SAREE"       # exact bill-book branding (no 's')

SHOP_ADDRESSES = [
    ("Dindoli", "Shop No. UG-01/02, Shree Krishna AC Mall, Near Flower Garden, Nr. Community Hall, Dindoli, Surat, Gujarat"),
    ("Godadara", "Shop No. 4, Devikrupa Row House, Nr. Shree Krishna Stellar, Opp Priyanka Metro City, Maharana Pratap Road, Godadara, Surat, Gujarat 395010"),
]
SHOP_PHONES = ["+91 97271 14581", "+91 99981 97511"]
GST_NUMBER = "24FOTPS0133A1Z4"
SHOP_GST = GST_NUMBER

EMAIL = "shuhaagansarees@gmail.com"
INSTAGRAM = "@shuhaagan_sarees"

TAGLINE = "Time-Honored Textiles, Timeless, Chic"
CATEGORIES = (
    "DESIGNER & SILK SAREE \u2022 ETHNIC SUITS \u2022 PURE CHUNARI "
    "\u2022 BRIDAL LEHENGAS \u2022 PURE SAREES \u2022 GOWNS SHARARA"
)

TERMS_OF_SALE = [
    "Payment to be made by A/c. Payee\u2019s Cheque / Draft only.",
    "Interest @ 24% per annum will be charged on overdue bills.",
    "We are not responsible for any loss or damage during Transit.",
    "Disputes will be settled in Surat Court only.",
    "Complaint within 7 days after that no complaint will be entertained.",
    "Goods once sold will not be taken back or exchanged.",
]

# ---------- BRAND COLOURS ----------
BRAND_MAROON = "#7A1F2B"
BRAND_GOLD = "#C9A24B"
BRAND_MAROON_LIGHT = "#F7EAEC"

# Logo: look in the project root first (as per Part 2 instructions),
# then _internal for PyInstaller 6+.
_logo_root = os.path.join(BASE_DIR, "logo.png")
_logo_internal = os.path.join(_INTERNAL_DIR, "assets", "logo.png")
LOGO_PATH = _logo_root if os.path.exists(_logo_root) else _logo_internal

EXCEL_PATH = os.path.join(BASE_DIR, "billing_data.xlsx")
PDF_FOLDER = os.path.join(BASE_DIR, "invoices")
QR_FOLDER = os.path.join(BASE_DIR, "qr_codes")
LOG_PATH = os.path.join(BASE_DIR, "error.log")

os.makedirs(PDF_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)
