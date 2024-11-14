import sys
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QVBoxLayout, QLabel, QWidget
from PyQt5.QtCore import Qt
from gui import create_gui
from database import create_tables

main_window = None

# 設定日誌紀錄
logging.basicConfig(
    filename='app.log',  # 日誌文件名
    level=logging.ERROR,  # 設定日誌級別為 ERROR
    format='%(asctime)s - %(levelname)s - %(message)s'  # 日誌格式
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Employee Attendance Management")
        self.resize(1200, 600)  # 增大窗口以顯示兩個表格
        
        # 創建中心窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 添加一個標籤來顯示錯誤信息
        self.error_label = QLabel(self)
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet("color: red;")
        layout.addWidget(self.error_label)

        create_gui(self)

    def show_success_and_cleanup(self):
        """顯示成功消息並清理。"""
        QMessageBox.information(self, "成功", "資料已成功從 JSON 加載！")
        load_initial_data()  # 重新加載資料以刷新表格

    def show_error_and_cleanup(self, error_message):
        """顯示錯誤消息。"""
        QMessageBox.critical(self, "錯誤", error_message)

    def show_error(self, message):
        """在 GUI 中顯示錯誤信息"""
        self.error_label.setText(message)

    def keyPressEvent(self, event):
        """處理鍵盤事件，按下 Command + W 時關閉應用。"""
        if event.key() == Qt.Key_W and event.modifiers() == Qt.MetaModifier:  # Qt.MetaModifier 是 Command 鍵
            self.close()  # 關閉窗口
        else:
            super().keyPressEvent(event)  # 處理其他按鍵事件

def main():
    global main_window
    try:
        create_tables()
        app = QApplication(sys.argv)
        main_window = MainWindow()
        main_window.show()

        sys.exit(app.exec_())
    except Exception as e:
        logging.error("Application crashed", exc_info=True)
        QMessageBox.critical(None, "Error", f"An unexpected error occurred:\n\n{str(e)}")

if __name__ == "__main__":
    main()
