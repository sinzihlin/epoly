import json
import threading
import sqlite3
from PyQt5.QtWidgets import (
    QPushButton, QVBoxLayout, QWidget, QFileDialog,
    QProgressDialog, QMessageBox, QTableWidget, QTableWidgetItem, QComboBox, QLabel, QHBoxLayout
)
from PyQt5.QtCore import Qt  # 確保導入 Qt 以使用對齊選項
from database import fetch_employees, fetch_attendance, update_employee
from json_parser import parse_json  # 引入 JSON 解析功能


def create_gui(main_window):
    central_widget = QWidget()
    main_window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)

    load_button = QPushButton("Load JSON File")
    load_button.clicked.connect(load_json_file)
    layout.addWidget(load_button)

    # 添加姓名篩選和月份篩選的佈局
    filter_layout = QHBoxLayout()

    # 姓名篩選
    name_label = QLabel("Filter by Name:")
    filter_layout.addWidget(name_label)

    global name_combobox
    name_combobox = QComboBox()
    name_combobox.addItem("所有")  # 添加「所有」選項
    name_combobox.currentIndexChanged.connect(filter_attendance)  # 監聽選擇改變事件
    filter_layout.addWidget(name_combobox)

    # 月份篩選
    month_label = QLabel("Select Month:")
    filter_layout.addWidget(month_label)

    global month_combobox
    month_combobox = QComboBox()
    month_combobox.addItems(["所有"] + [f"{i}月" for i in range(1, 13)])  # 添加「所有」和1月至12月
    month_combobox.currentIndexChanged.connect(filter_attendance)  # 監聽選擇改變事件
    filter_layout.addWidget(month_combobox)

    # 將篩選佈局添加到主佈局中
    layout.addLayout(filter_layout)

    global employee_table
    employee_table = QTableWidget()
    employee_table.setColumnCount(8)
    employee_table.setHorizontalHeaderLabels(
        ["ID", "姓名", "固定上班時間", "本薪", "時薪", "勞保", "健保", "自提"]
    )
    employee_table.cellChanged.connect(on_employee_edit)  # 監聽單元格改變事件
    layout.addWidget(employee_table)

    # 設置 ID 列的寬度
    employee_table.setColumnWidth(0, 50)  # 將 ID 列設置為 50 像素

    global attendance_table
    attendance_table = QTableWidget()
    attendance_table.setColumnCount(7)
    attendance_table.setHorizontalHeaderLabels(
        ["ID", "姓名", "日期", "打卡時間", "加班", "狀態", "請假小時"]
    )
    layout.addWidget(attendance_table)

    # 設置考勤 ID 列的寬度
    attendance_table.setColumnWidth(0, 50)  # 將考勤 ID 列設置為 50 像素

    load_initial_data()


def load_initial_data():
    employees = fetch_employees()
    if employees:
        employee_table.setRowCount(len(employees))
        for row_idx, row in enumerate(employees):
            for col_idx, item in enumerate(row):
                employee_table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))

        # 更新姓名下拉選單
        global name_combobox
        name_combobox.addItems([employee[1] for employee in employees])  # 添加所有員工的姓名到下拉選單
        
    # 一開始不過濾月份，顯示所有考勤記錄
    attendance_records = fetch_attendance()
    if attendance_records:
        display_attendance_records(attendance_records)


def display_attendance_records(records):
    attendance_table.setRowCount(len(records))
    for row_idx, row in enumerate(records):
        for col_idx, item in enumerate(row):
            attendance_table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))


def load_json_file():
    file_path, _ = QFileDialog.getOpenFileName(None, "Open JSON File", "", "JSON Files (*.json)")
    if file_path:
        progress_dialog = QProgressDialog("Loading Data...", None, 0, 0)
        progress_dialog.setCancelButtonText("Cancel")
        progress_dialog.setWindowTitle("Loading Data")
        progress_dialog.setModal(True)
        progress_dialog.show()

        # Creating a thread to handle data loading
        thread = threading.Thread(target=lambda: load_json_data(file_path, progress_dialog))
        thread.start()


def load_json_data(file_path, progress_dialog):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            parse_json(data)
            # Update UI in the main thread
            progress_dialog.finished.connect(lambda: show_success_and_cleanup(progress_dialog))
            progress_dialog.setValue(1)  # Set value to indicate completion
    except json.JSONDecodeError:
        progress_dialog.finished.connect(lambda: show_error_and_cleanup("Failed to decode JSON file. Please check the file format."))
    except sqlite3.Error as e:
        progress_dialog.finished.connect(lambda: show_error_and_cleanup(f"Database error: {e}"))
    except Exception as e:
        progress_dialog.finished.connect(lambda: show_error_and_cleanup(f"Failed to load JSON file: {e}"))


def show_success_and_cleanup(progress_dialog):
    progress_dialog.close()
    QMessageBox.information(None, "Success", "Data has been successfully loaded from JSON!")
    load_initial_data()


def show_error_and_cleanup(error_message):
    QMessageBox.critical(None, "Error", error_message)


def on_employee_edit(row, column):
    # 確保在編輯時不會處理空行
    if row >= 0:
        employee_id = employee_table.item(row, 0).text()  # ID 在第一列
        updated_employee = {
            "ID": employee_id,
            "姓名": employee_table.item(row, 1).text() if employee_table.item(row, 1) else "",
            "固定上班時間": employee_table.item(row, 2).text() if employee_table.item(row, 2) else "",
            "本薪": employee_table.item(row, 3).text() if employee_table.item(row, 3) else "",
            "時薪": employee_table.item(row, 4).text() if employee_table.item(row, 4) else "",
            "勞保": employee_table.item(row, 5).text() if employee_table.item(row, 5) else "",
            "健保": employee_table.item(row, 6).text() if employee_table.item(row, 6) else "",
            "自提": employee_table.item(row, 7).text() if employee_table.item(row, 7) else "",
        }
        update_employee(updated_employee)  # 更新數據庫


def filter_attendance():
    selected_month = month_combobox.currentText()  # 獲取選中的月份
    attendance_records = fetch_attendance()  # 獲取所有考勤記錄
    selected_name = name_combobox.currentText()  # 獲取選中的姓名

    # 過濾記錄，確保記錄的日期格式是 YYYY/MM/DD
    filtered_records = []
    
    for record in attendance_records:
        # 檢查月份篩選
        if selected_month == "所有":
            month_match = True
        else:
            month_match = len(record) > 2 and record[2].split('/')[1] == selected_month.replace('月', '')  # 檢查日期格式

        # 檢查姓名篩選
        name_match = selected_name == "所有" or selected_name == record[1]  # 檢查姓名是否匹配
        
        if month_match and name_match:
            filtered_records.append(record)

    display_attendance_records(filtered_records)  # 顯示過濾後的考勤記錄
