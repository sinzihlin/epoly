from tkinter import Tk
from gui import create_gui
from database import create_tables
import logging
import traceback

logging.basicConfig(
    filename='app.log',  # 日誌文件名
    level=logging.ERROR,  # 設定日誌級別為 ERROR，這樣只記錄錯誤
    format='%(asctime)s - %(levelname)s - %(message)s'  # 日誌格式
)
def main():
    try:
        create_tables()
        root = Tk()
        root.title("Employee Attendance Management")
        root.geometry("1200x600")  # 增大窗口以顯示兩個表格

        create_gui(root)  # 創建 GUI 界面

        root.mainloop()
    except Exception as e:
        logging.error("Application crashed", exc_info=True)  # 記錄完整的回溯信息

if __name__ == "__main__":
    main()

