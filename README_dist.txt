Shuhaagan Sarees — Billing System
==================================

HOW TO USE
1. Double-click billing_system.exe
   - A black window will open (keep it open while billing).
   - Your browser will open automatically to the billing dashboard.
2. Add new orders as rows in billing_data.xlsx and save the file.
3. Refresh the dashboard in your browser to see new pending invoices.
4. Click "Confirm & Generate Bill" to create the PDF invoice.
5. Download the PDF from the button that appears, or find it in the
   "invoices" folder.
6. To stop the app, close the black window.

IF SOMETHING GOES WRONG
- A file named error_log.txt will appear in this same folder with the
  exact error details. Send that file if you need help.
- Make sure billing_data.xlsx is closed in Excel before generating a bill
  (Excel locks the file while it's open, which can block saving).

FOLDERS
- invoices/   -> generated PDF bills
- qr_codes/   -> UPI QR codes used inside the PDFs
- assets/     -> shop logo used on the dashboard and PDFs
