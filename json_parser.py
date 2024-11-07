import json
from database import insert_employee, insert_attendance
import logging

def parse_json(data):
    last_employee = {}

    for record in data:
        try:
            if record['ID'] and record['姓名']:
                # 轉換 ID 為整數
                employee_id = int(record['ID'])
                 # 检查 '固定上班時間' 是否为空字符串
                fixed_work_time = record.get('固定上班時間', "08:00")
                if not fixed_work_time:  # 如果是空字符串，设置为默认值
                    fixed_work_time = "08:00"
                last_employee = {
                    'ID': employee_id,
                    '姓名': record['姓名'],
                    '固定上班時間': fixed_work_time,  # 确保默认值为 "08:00"
                    '本薪': record.get('本薪', ""),
                    '時薪': record.get('時薪', ""),
                    '勞保': record.get('勞保', ""),
                    '健保': record.get('健保', ""),
                    '自提': record.get('自提', ""),
                }
                insert_employee(last_employee)
                logging.info(f"Processed employee record: {last_employee['ID']}")

            if last_employee:
                attendance_record = {
                    'employee_id': last_employee['ID'],
                    '日期': record['日期'],
                    '打卡時間': format_time(record['打卡時間']),
                    '加班': record.get('加班', ""),
                    '狀態': record.get('狀態', ""),
                    '請假小時': record.get('請假小時', ""),
                }
                insert_attendance(attendance_record)
                logging.info(f"Processed attendance record for employee: {attendance_record['employee_id']}")
        except Exception as e:
            logging.error(f"Error processing record {record}: {e}")

def format_time(time_str):
    """Formats time from HHMM to HH:MM"""
    if time_str == "休假" or time_str == "未打卡":
        return time_str  # 如果是休假或未打卡，直接返回
    if len(time_str) == 4:  # 確保是HHMM格式
        return f"{time_str[:2]}:{time_str[2:]}"  # 格式化為HH:MM
    return time_str  # 返回原始值以防其他情況


            