import sys
import logging
import traceback
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QVBoxLayout, QLabel, QWidget
from PyQt5.QtCore import Qt
from gui import create_gui
from database import create_tables

logging.basicConfig(
    filename='app.log',  # 日誌文件名
    level=logging.ERROR,  # 設定日誌級別為 ERROR，這樣只記錄錯誤
    format='%(asctime)s - %(levelname)s - %(message)s'  # 日誌格式
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Employee Attendance Management")
        self.resize(1200, 600)  # 增大窗口以顯示兩個表格
        
        # 创建一个中心窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 添加一個標籤來顯示錯誤信息
        self.error_label = QLabel(self)
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet("color: red;")
        layout.addWidget(self.error_label)

        create_gui(self)

    def show_error(self, message):
        """在 GUI 中顯示錯誤信息"""
        self.error_label.setText(message)

def main():
    try:
        create_tables()
        app = QApplication(sys.argv)
        main_window = MainWindow()
        main_window.show()

        # 這裡應該是您用來處理 JSON 數據的代碼
        # 例如，您可能會有讀取文件和解析 JSON 的代碼
        # 如果發生異常，可以使用下面的方式來顯示錯誤信息
        # main_window.show_error("An error occurred while processing the data.")

        sys.exit(app.exec_())
    except Exception as e:
        logging.error("Application crashed", exc_info=True)
        QMessageBox.critical(None, "Error", f"An unexpected error occurred:\n\n{str(e)}")

if __name__ == "__main__":
    main()
