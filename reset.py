import openpyxl
import os

wb = openpyxl.load_workbook('dist/billing_system/billing_data.xlsx')
ws = wb.active
for row in ws.iter_rows(min_row=2):
    row[8].value = 'Pending'
wb.save('dist/billing_system/billing_data.xlsx')
print("Reset all to pending")
