import sqlite3
import logging
def connect_db():
    return sqlite3.connect('employee_attendance.db')

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    
    # 創建員工表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        ID INTEGER PRIMARY KEY,
        姓名 TEXT,
        固定上班時間 TEXT,
        本薪 TEXT,
        時薪 TEXT,
        勞保 TEXT,
        健保 TEXT,
        自提 TEXT
    );
    ''')

    # 創建考勤記錄表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance_records (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER ,
        日期 TEXT,
        打卡時間 TEXT,
        加班 TEXT,
        狀態 TEXT,
        請假小時 TEXT,
        FOREIGN KEY (employee_id) REFERENCES employees(ID)
    );
    ''')

    conn.commit()
    conn.close()


def insert_employee(employee):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO employees (ID, 姓名, 固定上班時間, 本薪, 時薪, 勞保, 健保, 自提) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (int(employee['ID']), employee['姓名'], employee['固定上班時間'],
              employee['本薪'], employee['時薪'], employee['勞保'],
              employee['健保'], employee['自提']))
        conn.commit()
        logging.info(f"Inserted/Updated employee: {employee['ID']}")
    except sqlite3.Error as e:
        logging.error(f"Database error while inserting employee {employee['ID']}: {e}")
    finally:
        conn.close()

def insert_attendance(attendance):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO attendance_records (employee_id, 日期, 打卡時間, 加班, 狀態, 請假小時) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (int(attendance['employee_id']), attendance['日期'],
              attendance['打卡時間'], attendance['加班'],
              attendance['狀態'], attendance['請假小時']))
        conn.commit()
        logging.info(f"Inserted attendance for employee: {attendance['employee_id']}")  # 記錄成功插入的消息
    except sqlite3.Error as e:
        logging.error(f"Database error while inserting attendance for {attendance['employee_id']}: {e}")  # 記錄錯誤
    finally:
        conn.close()

def fetch_employees():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT ID, 姓名, 固定上班時間, 本薪, 時薪, 勞保, 健保, 自提 FROM employees ORDER BY ID')
    records = cursor.fetchall()
    conn.close()
    return records

def fetch_attendance(employee_id=None):
    conn = connect_db()
    cursor = conn.cursor()
    if employee_id:
        cursor.execute('''
            SELECT ar.employee_id, e.姓名, ar.日期, ar.打卡時間, ar.加班, ar.狀態, ar.請假小時 
            FROM attendance_records ar
            JOIN employees e ON ar.employee_id = e.ID
            WHERE ar.employee_id = ?
            ORDER BY ar.employee_id, DATE(ar.日期)
        ''', (int(employee_id),))
    else:
        cursor.execute('''
            SELECT ar.employee_id, e.姓名, ar.日期, ar.打卡時間, ar.加班, ar.狀態, ar.請假小時 
            FROM attendance_records ar
            JOIN employees e ON ar.employee_id = e.ID
            ORDER BY ar.employee_id, DATE(ar.日期)
        ''')
    records = cursor.fetchall()
    conn.close()
    return records
    
def update_employee(employee):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE employees
            SET 姓名 = ?, 固定上班時間 = ?, 本薪 = ?, 時薪 = ?, 勞保 = ?, 健保 = ?, 自提 = ?
            WHERE ID = ?
        ''', (employee['姓名'], employee['固定上班時間'], employee['本薪'], employee['時薪'], employee['勞保'], employee['健保'], employee['自提'], int(employee['ID'])))
        conn.commit()
        logging.info(f"Updated employee: {employee['ID']}")
    except sqlite3.Error as e:
        logging.error(f"Database error while updating employee {employee['ID']}: {e}")
    finally:
        conn.close()
def update_attendance_record(attendance):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE attendance_records 
            SET 打卡時間 = ?, 加班 = ?, 狀態 = ?, 請假小時 = ? 
            WHERE employee_id = ? AND 日期 = ?
        ''', (attendance['打卡時間'], attendance['加班'],
              attendance['狀態'], attendance['請假小時'],
              attendance['employee_id'], attendance['日期']))
        conn.commit()
        logging.info(f"Updated attendance for employee: {attendance['employee_id']} on {attendance['日期']}")
    except sqlite3.Error as e:
        logging.error(f"Database error while updating attendance for {attendance['employee_id']}: {e}")
    finally:
        conn.close()