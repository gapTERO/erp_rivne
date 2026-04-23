from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QWidget, QGridLayout
)
from PyQt5.QtCore import Qt
from ui.styles import *

# Кольори для ролей
ROLE_COLORS = {
    "admin":       ACCENT,
    "manager":     "#3b82f6",
    "storekeeper": "#22c55e",
    "operator":    "#8b5cf6",
}

ROLE_NAMES = {
    "admin":       "Адміністратор",
    "manager":     "Менеджер",
    "storekeeper": "Комірник",
    "operator":    "Оператор виробництва",
}

# Резервні акаунти якщо БД недоступна
FALLBACK_ACCOUNTS = [
    ("admin",    "admin123",   "admin"),
    ("manager",  "manager123", "manager"),
    ("sklad",    "sklad123",   "storekeeper"),
    ("operator", "oper123",    "operator"),
]


def _load_accounts_from_db():
    """Завантажує список акаунтів з БД для відображення підказок."""
    try:
        from database.db import db_cursor
        with db_cursor() as cur:
            cur.execute("""
                SELECT login, password, role
                FROM users
                WHERE is_active = TRUE
                ORDER BY id
            """)
            rows = cur.fetchall()
            if rows:
                return [(r["login"], r["password"], r["role"]) for r in rows]
    except Exception:
        pass
    return FALLBACK_ACCOUNTS


class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.user_info = None
        self.setWindowTitle("ERP — Рівне Борошно")
        self.setFixedSize(460, 620)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.setStyleSheet(f"QDialog {{ background:{BG_LIGHT}; }}")
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Шапка ──────────────────────────────
        header = QFrame()
        header.setFixedHeight(155)
        header.setStyleSheet("background:#2d3748;")
        hl = QVBoxLayout(header)
        hl.setAlignment(Qt.AlignCenter)
        hl.setSpacing(6)

        logo = QLabel("🌾")
        logo.setAlignment(Qt.AlignCenter)
        logo.setFixedSize(68, 68)
        logo.setStyleSheet(
            f"font-size:38px; background:{ACCENT}; border-radius:16px;"
        )
        lbl_title = QLabel("Рівне Борошно")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet(
            "font-size:20px; font-weight:700; color:white; background:transparent;"
        )
        lbl_sub = QLabel("ERP-система управління виробництвом")
        lbl_sub.setAlignment(Qt.AlignCenter)
        lbl_sub.setStyleSheet(
            "font-size:11px; color:#a0aec0; background:transparent;"
        )
        logo_row = QHBoxLayout()
        logo_row.addStretch()
        logo_row.addWidget(logo)
        logo_row.addStretch()
        hl.addLayout(logo_row)
        hl.addWidget(lbl_title)
        hl.addWidget(lbl_sub)
        root.addWidget(header)

        # ── Форма ──────────────────────────────
        form = QWidget()
        form.setStyleSheet(f"background:{WHITE};")
        fl = QVBoxLayout(form)
        fl.setContentsMargins(36, 22, 36, 22)
        fl.setSpacing(10)

        lbl_enter = QLabel("Вхід до системи")
        lbl_enter.setStyleSheet(
            f"font-size:16px; font-weight:700; color:{TEXT_PRIMARY};"
        )
        fl.addWidget(lbl_enter)

        fl.addWidget(self._lbl("Логін"))
        self.txt_login = QLineEdit()
        self.txt_login.setPlaceholderText("Введіть логін")
        self.txt_login.setFixedHeight(40)
        fl.addWidget(self.txt_login)

        fl.addWidget(self._lbl("Пароль"))
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Введіть пароль")
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setFixedHeight(40)
        self.txt_password.returnPressed.connect(self._login)
        fl.addWidget(self.txt_password)

        self.lbl_error = QLabel("")
        self.lbl_error.setAlignment(Qt.AlignCenter)
        self.lbl_error.setStyleSheet(f"""
            color:{DANGER}; font-size:12px; font-weight:600;
            background:#fee2e2; border-radius:6px; padding:6px; border:none;
        """)
        self.lbl_error.setVisible(False)
        fl.addWidget(self.lbl_error)

        btn = QPushButton("Увійти")
        btn.setFixedHeight(44)
        btn.setStyleSheet(f"""
            QPushButton {{
                background:{ACCENT}; color:white; border:none;
                border-radius:8px; font-size:14px; font-weight:600;
            }}
            QPushButton:hover {{ background:{ACCENT_HOVER}; }}
            QPushButton:pressed {{ background:#c87e00; }}
        """)
        btn.clicked.connect(self._login)
        fl.addWidget(btn)

        # ── Акаунти з БД ───────────────────────
        fl.addSpacing(6)

        hdr_row = QHBoxLayout()
        lbl_h = QLabel("Акаунти користувачів:")
        lbl_h.setStyleSheet(
            f"font-size:12px; font-weight:700; color:{TEXT_PRIMARY};"
        )
        self.lbl_source = QLabel("БД")
        self.lbl_source.setStyleSheet(f"""
            font-size:10px; font-weight:600; color:{SUCCESS};
            background:#dcfce7; border-radius:4px; padding:2px 6px; border:none;
        """)
        hdr_row.addWidget(lbl_h)
        hdr_row.addWidget(self.lbl_source)
        hdr_row.addStretch()
        fl.addLayout(hdr_row)

        # Таблиця акаунтів
        self.grid_widget = QWidget()
        self.grid_widget.setStyleSheet(
            f"background:{BG_LIGHT}; border-radius:8px; border:none;"
        )
        self.grid_lay = QGridLayout(self.grid_widget)
        self.grid_lay.setContentsMargins(10, 10, 10, 10)
        self.grid_lay.setSpacing(6)
        self.grid_lay.setHorizontalSpacing(10)
        fl.addWidget(self.grid_widget)

        hint = QLabel("Натисніть на логін для автозаповнення")
        hint.setStyleSheet(f"font-size:10px; color:{TEXT_SECONDARY};")
        hint.setAlignment(Qt.AlignCenter)
        fl.addWidget(hint)

        root.addWidget(form)

        # Завантажуємо акаунти
        self._load_accounts()

    def _load_accounts(self):
        """Завантажує та відображає акаунти."""
        accounts = _load_accounts_from_db()

        # Визначаємо джерело
        is_db = accounts != FALLBACK_ACCOUNTS
        if is_db:
            self.lbl_source.setText("З бази даних")
            self.lbl_source.setStyleSheet(f"""
                font-size:10px; font-weight:600; color:{SUCCESS};
                background:#dcfce7; border-radius:4px; padding:2px 6px; border:none;
            """)
        else:
            self.lbl_source.setText("Демо-режим")
            self.lbl_source.setStyleSheet(f"""
                font-size:10px; font-weight:600; color:{WARNING};
                background:#fef3c7; border-radius:4px; padding:2px 6px; border:none;
            """)

        # Очищуємо попередній вміст
        while self.grid_lay.count():
            item = self.grid_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Заголовки
        for col, txt in enumerate(["Логін", "Пароль", "Роль"]):
            lh = QLabel(txt)
            lh.setStyleSheet(
                f"font-size:10px; font-weight:700; color:{TEXT_SECONDARY}; "
                f"text-transform:uppercase;"
            )
            self.grid_lay.addWidget(lh, 0, col)

        # Рядки з акаунтами
        for row, (login, password, role) in enumerate(accounts, start=1):
            color = ROLE_COLORS.get(role, TEXT_SECONDARY)
            role_name = ROLE_NAMES.get(role, role)

            # Логін — кольоровий бейдж, клікабельний
            badge = QLabel(login)
            badge.setAlignment(Qt.AlignCenter)
            badge.setFixedHeight(26)
            badge.setCursor(Qt.PointingHandCursor)
            badge.setToolTip(f"Клікніть щоб увійти як {login}")
            badge.setStyleSheet(f"""
                background:{color}22; color:{color};
                border:1px solid {color}88;
                border-radius:5px; padding:2px 8px;
                font-size:12px; font-weight:700; font-family:Consolas,monospace;
            """)
            badge.mousePressEvent = lambda e, l=login, p=password: self._autofill(l, p)
            self.grid_lay.addWidget(badge, row, 0)

            # Пароль
            lp = QLabel(password)
            lp.setStyleSheet(f"""
                font-size:12px; color:{TEXT_PRIMARY};
                font-family:Consolas,monospace;
                background:#f8fafc; border:1px solid {BORDER};
                border-radius:4px; padding:2px 6px;
            """)
            self.grid_lay.addWidget(lp, row, 1)

            # Роль
            lr = QLabel(role_name)
            lr.setStyleSheet(f"font-size:11px; color:{TEXT_SECONDARY};")
            self.grid_lay.addWidget(lr, row, 2)

    def _lbl(self, text):
        l = QLabel(text)
        l.setStyleSheet(f"font-size:12px; color:{TEXT_SECONDARY}; font-weight:500;")
        return l

    def _autofill(self, login, password):
        self.txt_login.setText(login)
        self.txt_password.setText(password)
        self.lbl_error.setVisible(False)
        self.txt_password.setFocus()

    def _login(self):
        from auth import authenticate
        login    = self.txt_login.text().strip()
        password = self.txt_password.text()

        if not login or not password:
            self._show_error("Введіть логін та пароль")
            return

        result = authenticate(login, password)
        if result:
            self.user_info = result
            self.accept()
        else:
            self._show_error("Невірний логін або пароль")
            self.txt_password.clear()
            self.txt_password.setFocus()

    def _show_error(self, msg):
        self.lbl_error.setText(msg)
        self.lbl_error.setVisible(True)
