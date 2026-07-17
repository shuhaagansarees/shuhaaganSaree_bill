import urllib.request, json, re, fitz
import os

try:
    req = urllib.request.Request('http://127.0.0.1:5000/')
    with urllib.request.urlopen(req) as res:
        html = res.read().decode()
    
    invoices = re.findall(r'<h3>Invoice: (INV-\d+)</h3>', html)
    if not invoices:
        print('No pending invoices found.')
    else:
        inv = invoices[0]
        print(f'Generating {inv}...')
        post_req = urllib.request.Request(f'http://127.0.0.1:5000/generate/{inv}', method='POST')
        with urllib.request.urlopen(post_req) as post_res:
            print('Generation successful.')
        
        pdf_path = f'dist/billing_system/invoices/{inv}.pdf'
        if os.path.exists(pdf_path):
            doc = fitz.open(pdf_path)
            png_path = f'dist/billing_system/invoices/{inv}_final_preview.png'
            doc[0].get_pixmap(dpi=200).save(png_path)
            doc.close()
            print(f'Preview saved to {png_path}')
        else:
            print('PDF not found!')
            
except Exception as e:
    print('Error:', e)
