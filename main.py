import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

from ui.login_window import LoginWindow
from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("ERP Рівне Борошно")

    # Автоматична ініціалізація БД при першому запуску
    try:
        from database.db import init_database
        init_database()
    except Exception:
        pass  # БД недоступна — працюємо в демо-режимі

    login = LoginWindow()
    if login.exec_() != login.Accepted:
        sys.exit(0)

    window = MainWindow(user_info=login.user_info)
    window.show()
    sys.exit(app.exec_())
