#Excel Sheet Testing
import openpyxl

path = "C:/Users/regin/OneDrive/Desktop/TestBook.xlsx"

wb_obj = openpyxl.load_workbook(path)
sheet_obj = wb_obj.active
sheet_obj.cell(row=2, column=2).value = "hello"
cell_obj = sheet_obj.cell(row = 2, column = 2)
print(cell_obj.value)
wb_obj.save(path)
