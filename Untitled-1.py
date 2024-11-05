import os
import json
import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox
from tksheet import Sheet  # 確保引入 tksheet

# 設置環境變量以靜默 Tk 的過時警告
os.environ['TK_SILENCE_DEPRECATION'] = '1'

def load_json_file():
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                save_to_database(data)
                messagebox.showinfo("Success", "Data has been successfully saved to the database!")
                display_attendance_records()  # 更新表格以顯示新數據
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load JSON file: {e}")

def save_to_database(data):
    conn = sqlite3.connect('employee_attendance.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        ID TEXT PRIMARY KEY,
        姓名 TEXT,
        勞保 TEXT,
        健保 TEXT,
        自提 TEXT
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance_records (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id TEXT,
        日期 TEXT,
        時間 TEXT,
        加班 TEXT,
        FOREIGN KEY (employee_id) REFERENCES employees(ID)
    );
    ''')

    employee_records = []
    attendance_records = []
    current_employee = {}

    for record in data:
        if record['ID'] and record['姓名']:
            current_employee = {
                'ID': record['ID'],
                '姓名': record['姓名'],
                '勞保': record['勞保'],
                '健保': record['健保'],
                '自提': record['自提'],
            }
            employee_records.append(current_employee)
        
        if '日期' in record and '時間' in record:
            attendance_record = {
                'employee_id': current_employee['ID'],
                '日期': record['日期'],
                '時間': record['時間'],
                '加班': record['加班'],
            }
            attendance_records.append(attendance_record)

    for employee in employee_records:
        cursor.execute('''
        INSERT OR REPLACE INTO employees (ID, 姓名, 勞保, 健保, 自提) 
        VALUES (?, ?, ?, ?, ?)
        ''', (employee['ID'], employee['姓名'], employee['勞保'], employee['健保'], employee['自提']))

    for attendance in attendance_records:
        cursor.execute('''
        INSERT INTO attendance_records (employee_id, 日期, 時間, 加班) 
        VALUES (?, ?, ?, ?)
        ''', (attendance['employee_id'], attendance['日期'], attendance['時間'], attendance['加班']))

    conn.commit()
    conn.close()

def display_attendance_records():
    conn = sqlite3.connect('employee_attendance.db')
    cursor = conn.cursor()

    cursor.execute('''
    SELECT employees.姓名, attendance_records.日期, attendance_records.時間, attendance_records.加班 
    FROM attendance_records 
    JOIN employees ON attendance_records.employee_id = employees.ID
    ''')
    records = cursor.fetchall()

    # 調試輸出
    print("Fetched records:", records)  # 確認從數據庫獲取的記錄

    # 直接設定 sheet 的資料
    if records:
        sheet.set_sheet_data([[str(cell) for cell in row] for row in records])
    else:
        sheet.set_sheet_data([])  # 清空表格如果沒有記錄

    conn.close()

# 創建主窗口
root = tk.Tk()
root.title("Employee Attendance Management")

# 設定窗口的初始大小
root.geometry("600x400")  # 確保窗口足夠大以顯示表格

# 創建一個按鈕來選擇 JSON 文件
load_button = tk.Button(root, text="Load JSON File", command=load_json_file)
load_button.pack(pady=10)

# 使用 Sheet 替換 Treeview
frame = tk.Frame(root)
frame.pack(fill="both", expand=True)

sheet = Sheet(frame,
             headers=["姓名", "日期", "時間", "加班"],
             height=400,
             width=600)
sheet.enable_bindings()
sheet.pack(fill="both", expand=True)

# 在加載數據後立即顯示表格
display_attendance_records()

# 運行主循環
root.mainloop()
