import sys
import logging
import traceback
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from gui import create_gui
from database import create_tables

logging.basicConfig(
    filename='app.log',  # 日誌文件名
    level=logging.ERROR,  # 設定日誌級別為 ERROR，這樣只記錄錯誤
    format='%(asctime)s - %(levelname)s - %(message)s'  # 日誌格式
)

def main():
    try:
        create_tables()
        app = QApplication(sys.argv)
        main_window = QMainWindow()
        main_window.setWindowTitle("Employee Attendance Management")
        main_window.resize(1200, 600)  # 增大窗口以顯示兩個表格

        create_gui(main_window)  # 創建 GUI 界面

        main_window.show()
        sys.exit(app.exec_())
    except Exception as e:
        logging.error("Application crashed", exc_info=True)  # 記錄完整的回溯信息

if __name__ == "__main__":
    main()
