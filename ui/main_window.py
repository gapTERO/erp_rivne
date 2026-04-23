from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, QDateTime

from ui.styles import *
from ui.tabs.home_tab import HomeTab
from ui.tabs.orders_tab import OrdersTab
from ui.tabs.production_tab import ProductionTab
from ui.tabs.warehouse_tab import WarehouseTab
from ui.tabs.suppliers_tab import SuppliersTab
from ui.tabs.employees_tab import EmployeesTab
from ui.tabs.reports_tab import ReportsTab
from auth import ROLE_NAMES, get_allowed_tabs

TAB_INFO = [
    (0, "🏠", "Головна",    "Головна — огляд підприємства"),
    (1, "📋", "Замовлення", "Замовлення"),
    (2, "⚙️", "Виробн.",   "Виробництво"),
    (3, "📦", "Склад",      "Склад"),
    (4, "🚛", "Постач.",    "Постачальники"),
    (5, "👥", "Персонал",   "Співробітники"),
    (6, "📊", "Звіти",      "Звіти"),
]


class NavButton(QPushButton):
    def __init__(self, icon_text, label):
        super().__init__()
        self.setFixedSize(68, 62)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 6, 4, 6)
        lay.setSpacing(3)
        lay.setAlignment(Qt.AlignCenter)

        il = QLabel(icon_text)
        il.setAlignment(Qt.AlignCenter)
        il.setStyleSheet("font-size:18px; background:transparent; border:none;")
        il.setAttribute(Qt.WA_TransparentForMouseEvents)

        tl = QLabel(label)
        tl.setAlignment(Qt.AlignCenter)
        tl.setStyleSheet(
            "font-size:10px; background:transparent; border:none; font-weight:500;"
        )
        tl.setAttribute(Qt.WA_TransparentForMouseEvents)

        lay.addWidget(il)
        lay.addWidget(tl)
        self._inactive()

    def _active(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background:{SIDEBAR_ACTIVE};
                border-radius:10px; color:#ffffff;
                border-left:3px solid {ACCENT};
                border-top:none; border-right:none; border-bottom:none;
            }}
        """)

    def _inactive(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background:transparent; border-radius:10px;
                color:#c8d8e8; border:none;
            }}
            QPushButton:hover {{
                background:{SIDEBAR_ACTIVE}; color:#ffffff;
            }}
        """)

    def setActive(self, v):
        self._active() if v else self._inactive()


class Sidebar(QWidget):
    def __init__(self, main_window, allowed_tabs):
        super().__init__()
        self.mw = main_window
        self.allowed = allowed_tabs
        self.buttons = {}
        self.setFixedWidth(72)
        self.setStyleSheet(f"background:{SIDEBAR_BG};")
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(2, 12, 2, 12)
        lay.setSpacing(2)
        lay.setAlignment(Qt.AlignTop)

        logo = QLabel("🌾")
        logo.setAlignment(Qt.AlignCenter)
        logo.setFixedHeight(48)
        logo.setStyleSheet(
            f"font-size:26px; background:{ACCENT}; border-radius:12px; margin:4px;"
        )
        lay.addWidget(logo)
        lay.addSpacing(6)

        for idx, icon, label, _ in TAB_INFO:
            if idx not in self.allowed:
                continue
            btn = NavButton(icon, label)
            btn.clicked.connect(lambda _, i=idx: self._click(i))
            self.buttons[idx] = btn
            lay.addWidget(btn)

        lay.addStretch()

        # ── Кнопка виходу ──────────────────────
        btn_logout = QPushButton("🚪")
        btn_logout.setFixedSize(44, 44)
        btn_logout.setToolTip("Вийти з акаунту")
        btn_logout.setStyleSheet(f"""
            QPushButton {{
                background:transparent; border-radius:10px;
                color:#ef4444; border:none; font-size:20px;
            }}
            QPushButton:hover {{
                background:#3d1515; color:#ff6b6b;
            }}
        """)
        btn_logout.clicked.connect(self.mw.logout)

        logout_wrap = QHBoxLayout()
        logout_wrap.setContentsMargins(0, 0, 0, 0)
        logout_wrap.addStretch()
        logout_wrap.addWidget(btn_logout)
        logout_wrap.addStretch()
        lay.addLayout(logout_wrap)

        lbl_out = QLabel("Вихід")
        lbl_out.setAlignment(Qt.AlignCenter)
        lbl_out.setStyleSheet("color:#ef4444; font-size:9px; font-weight:500;")
        lay.addWidget(lbl_out)

        lay.addSpacing(4)
        ver = QLabel("v1.0")
        ver.setAlignment(Qt.AlignCenter)
        ver.setStyleSheet("color:#7a8fa6; font-size:9px;")
        lay.addWidget(ver)

        first = self.allowed[0] if self.allowed else 0
        if first in self.buttons:
            self.buttons[first].setActive(True)

    def _click(self, idx):
        for b in self.buttons.values():
            b.setActive(False)
        if idx in self.buttons:
            self.buttons[idx].setActive(True)
        self.mw.switch_tab(idx)

    def activate(self, idx):
        for b in self.buttons.values():
            b.setActive(False)
        if idx in self.buttons:
            self.buttons[idx].setActive(True)


class TopBar(QFrame):
    def __init__(self, user_info):
        super().__init__()
        self.setFixedHeight(52)
        self.setStyleSheet(
            f"QFrame {{ background:{WHITE}; border-bottom:1px solid {BORDER}; }}"
        )
        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 0, 20, 0)

        self.lbl_title = QLabel("Головна — огляд підприємства")
        self.lbl_title.setStyleSheet(
            f"font-size:15px; font-weight:600; color:{TEXT_PRIMARY}; border:none;"
        )

        role_name = ROLE_NAMES.get(user_info["role"], user_info["role"])
        full_name  = user_info.get("full_name", "")

        lbl_user = QLabel(f"👤  {full_name}  |  {role_name}")
        lbl_user.setStyleSheet(
            f"font-size:12px; color:{TEXT_SECONDARY}; border:none;"
        )

        lbl_company = QLabel("Рівне Борошно")
        lbl_company.setStyleSheet(f"""
            font-size:12px; font-weight:600; color:white;
            background:{ACCENT}; border-radius:12px;
            padding:3px 14px; border:none;
        """)

        self.lbl_time = QLabel()
        self.lbl_time.setStyleSheet(
            f"font-size:12px; color:{TEXT_SECONDARY}; border:none;"
        )
        self._tick()
        t = QTimer(self)
        t.timeout.connect(self._tick)
        t.start(60000)

        lay.addWidget(self.lbl_title)
        lay.addStretch()
        lay.addWidget(lbl_user)
        lay.addSpacing(16)
        lay.addWidget(lbl_company)
        lay.addSpacing(16)
        lay.addWidget(self.lbl_time)

    def _tick(self):
        self.lbl_time.setText(
            QDateTime.currentDateTime().toString("dd.MM.yyyy  hh:mm")
        )

    def set_title(self, t):
        self.lbl_title.setText(t)


class MainWindow(QMainWindow):
    def __init__(self, user_info):
        super().__init__()
        self.user_info    = user_info
        self.allowed_tabs = get_allowed_tabs(user_info["role"])
        self.setWindowTitle(
            f"ERP — Рівне Борошно  [{ROLE_NAMES.get(user_info['role'], '')}]"
        )
        self.setMinimumSize(1100, 650)
        self.resize(1400, 800)
        self.setStyleSheet(MAIN_STYLE)

        self._all_tabs = [
            HomeTab(), OrdersTab(), ProductionTab(),
            WarehouseTab(), SuppliersTab(), EmployeesTab(), ReportsTab(),
        ]
        self._build()

    def _build(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = Sidebar(self, self.allowed_tabs)
        root.addWidget(self.sidebar)

        right = QVBoxLayout()
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(0)

        self.topbar = TopBar(self.user_info)
        right.addWidget(self.topbar)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background:{BG_LIGHT};")
        for tab in self._all_tabs:
            self.stack.addWidget(tab)

        right.addWidget(self.stack)
        right_w = QWidget()
        right_w.setLayout(right)
        root.addWidget(right_w)

        first = self.allowed_tabs[0] if self.allowed_tabs else 0
        self.switch_tab(first)

    def switch_tab(self, index):
        if index not in self.allowed_tabs:
            QMessageBox.warning(self, "Доступ заборонено",
                                "У вас немає прав для перегляду цього розділу.")
            return
        self.stack.setCurrentIndex(index)
        self.topbar.set_title(TAB_INFO[index][3])
        self.sidebar.activate(index)
        tab = self._all_tabs[index]
        if hasattr(tab, "refresh"):
            tab.refresh()

    def logout(self):
        reply = QMessageBox.question(
            self, "Вихід",
            "Ви дійсно хочете вийти з акаунту?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        # Закриваємо головне вікно і показуємо логін знову
        from ui.login_window import LoginWindow
        self.hide()
        login = LoginWindow()
        if login.exec_() == LoginWindow.Accepted:
            new_window = MainWindow(user_info=login.user_info)
            new_window.show()
            # Зберігаємо посилання щоб не знищилось збирачем сміття
            self._next_window = new_window
        self.close()
