import json
import threading
import sqlite3
from tkinter import Button, Frame, filedialog, messagebox, Toplevel
from tkinter import ttk
from tksheet import Sheet
from database import fetch_employees, fetch_attendance, update_employee
from json_parser import parse_json  # 引入 JSON 解析功能


def create_gui(root):
    load_button = Button(root, text="Load JSON File", command=load_json_file)
    load_button.pack(pady=10)

    employee_frame = Frame(root)
    employee_frame.pack(fill="both", expand=True)

    global employee_sheet
    employee_sheet = Sheet(employee_frame,
             headers=["ID", "姓名", "固定上班時間", "本薪", "時薪", "勞保", "健保", "自提"],
             height=200,
             width=1000)
    employee_sheet.enable_bindings()
    employee_sheet.pack(fill="both", expand=True)
    employee_sheet.bind("<FocusOut>", on_employee_edit)

    attendance_frame = Frame(root)
    attendance_frame.pack(fill="both", expand=True)

    global attendance_sheet
    attendance_sheet = Sheet(attendance_frame,
             headers=["ID", "姓名","日期", "打卡時間", "加班", "狀態", "請假小時"],
             height=200,
             width=1000)
    attendance_sheet.enable_bindings()
    attendance_sheet.pack(fill="both", expand=True)

    load_initial_data()
    

def load_initial_data():
    employees = fetch_employees()
    if employees:
        employee_sheet.set_sheet_data([[str(cell) for cell in row] for row in employees])
    attendance_records = fetch_attendance()
    if attendance_records:
        attendance_sheet.set_sheet_data([[str(cell) for cell in row] for row in attendance_records])

def load_json_file():
    file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if file_path:
        # 創建進度條窗口（在主線程中）
        progress_window = Toplevel()
        progress_window.title("Loading Data")
        progress_window.geometry("300x100")
        
        progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
        progress_bar.pack(expand=True, fill='x', padx=20, pady=20)
        progress_bar.start()
        
        # 更新進度條窗口
        progress_window.update()
        
        # 創建線程處理數據
        thread = threading.Thread(target=lambda: load_json_data(file_path, progress_window))
        thread.start()

def load_json_data(file_path, progress_window):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            parse_json(data)
            # 使用 after 方法在主線程中更新 UI
            progress_window.after(0, lambda: show_success_and_cleanup(progress_window))
    except json.JSONDecodeError:
        progress_window.after(0, lambda: show_error_and_cleanup("Failed to decode JSON file. Please check the file format.", progress_window))
    except sqlite3.Error as e:
        progress_window.after(0, lambda: show_error_and_cleanup(f"Database error: {e}", progress_window))
    except Exception as e:
        progress_window.after(0, lambda: show_error_and_cleanup(f"Failed to load JSON file: {e}", progress_window))

def show_success_and_cleanup(progress_window):
    progress_window.destroy()
    messagebox.showinfo("Success", "Data has been successfully loaded from JSON!")
    load_initial_data()

def show_error_and_cleanup(error_message, progress_window):
    progress_window.destroy()
    messagebox.showerror("Error", error_message)

def on_employee_select(event):
    selected_row = employee_sheet.get_selected_row()
    if selected_row:
        employee_id = selected_row[0]
        display_attendance_records(employee_id)


def on_employee_edit(event = None):
    print('有近來')
     # Get the currently selected cell
    # Get the currently selected cell
    selected_cells = employee_sheet.get_currently_selected()
    if selected_cells:  # Ensure this line is properly aligned
        index = selected_cells[0]  # Assuming only one cell is selected
        
        row, column = index.row, index.column
        employee_id = employee_sheet.get_cell_data(row, 0)  # Assuming ID is in the first column

        # Get the entire row data
        updated_employee = {
            "ID": employee_id,
            "姓名": employee_sheet.get_cell_data(row, 1),
            "固定上班時間": employee_sheet.get_cell_data(row, 2),
            "本薪": employee_sheet.get_cell_data(row, 3),
            "時薪": employee_sheet.get_cell_data(row, 4),
            "勞保": employee_sheet.get_cell_data(row, 5),
            "健保": employee_sheet.get_cell_data(row, 6),
            "自提": employee_sheet.get_cell_data(row, 7),
        }

        # Update the database
        update_employee(updated_employee)
