import json
from database import insert_employee, insert_attendance
import logging
import sqlite3  # 假設您使用的是 SQLite

def parse_json(data):
    last_employee = {}

    for record in data:
        try:
            # 檢查必要字段
            if not all(k in record for k in ('ID', '姓名')):
                raise ValueError(f"Missing required fields in record: {record}")
            
            if record['ID'] and record['姓名']:
                # 轉換 ID 為整數
                try:
                    employee_id = int(record['ID'])
                except ValueError:
                    logging.error(f"Invalid ID format in record: {record}")
                    continue  # 跳過這條記錄

                fixed_work_time = record.get('固定上班時間', "08:00")
                if not fixed_work_time:  # 如果是空字符串，設置為預設值
                    fixed_work_time = "08:00"
                last_employee = {
                    'ID': employee_id,
                    '姓名': record['姓名'],
                    '固定上班時間': fixed_work_time,
                    '本薪': record.get('本薪', ""),
                    '時薪': record.get('時薪', ""),
                    '勞保': record.get('勞保', ""),
                    '健保': record.get('健保', ""),
                    '自提': record.get('自提', ""),
                }
                
                try:
                    insert_employee(last_employee)
                    logging.info(f"Processed employee record: {last_employee['ID']}")
                except sqlite3.IntegrityError as ie:
                    logging.error(f"Integrity error inserting employee record {last_employee}: {ie}")
                except sqlite3.OperationalError as oe:
                    logging.error(f"Operational error inserting employee record {last_employee}: {oe}")
                except Exception as e:
                    logging.error(f"Unexpected error inserting employee record {last_employee}: {e}")

            if last_employee:
                attendance_record = {
                    'employee_id': last_employee['ID'],
                    '日期': record['日期'],
                    '打卡時間': format_time(record['打卡時間']),
                    '加班': record.get('加班', ""),
                    '狀態': record.get('狀態', ""),
                    '請假小時': record.get('請假小時', ""),
                }
                try:
                    insert_attendance(attendance_record)
                    logging.info(f"Processed attendance record for employee: {attendance_record['employee_id']}")
                except sqlite3.IntegrityError as ie:
                    logging.error(f"Integrity error inserting attendance record {attendance_record}: {ie}")
                except sqlite3.OperationalError as oe:
                    logging.error(f"Operational error inserting attendance record {attendance_record}: {oe}")
                except Exception as e:
                    logging.error(f"Unexpected error inserting attendance record {attendance_record}: {e}")

        except KeyError as ke:
            logging.error(f"Key error in record {record}: {ke}")
        except ValueError as ve:
            logging.error(f"Value error in record {record}: {ve}")
        except Exception as e:
            logging.error(f"Unexpected error processing record {record}: {e}")

def format_time(time_str):
    """Formats time from HHMM to HH:MM"""
    if time_str == "休假" or time_str == "未打卡":
        return time_str  # 如果是休假或未打卡，直接返回
    if len(time_str) == 4:  # 確保是HHMM格式
        return f"{time_str[:2]}:{time_str[2:]}"  # 格式化為HH:MM
    return time_str  # 返回原始值以防其他情況
