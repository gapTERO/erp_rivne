from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame
)
from PyQt5.QtCore import Qt
from ui.styles import *


class MsgDialog(QDialog):
    """Універсальний діалог — повідомлення або підтвердження."""
    def __init__(self, parent, title, message, detail=None,
                 mode="info", confirm_text="Так", cancel_text="Ні, скасувати"):
        super().__init__(parent)
        self.confirmed = False
        self.setWindowTitle(title)
        self.setMinimumWidth(380)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.setStyleSheet("""
            QDialog { background: #ffffff; }
            QLabel  { color: #1a2332; background: transparent; }
        """)
        self._build(message, detail, mode, confirm_text, cancel_text)

    def _build(self, message, detail, mode, confirm_text, cancel_text):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)

        icons = {"info": "ℹ️", "warning": "⚠️", "error": "❌", "question": "❓"}
        top = QHBoxLayout()
        icon = QLabel(icons.get(mode, "ℹ️"))
        icon.setStyleSheet("font-size:28px; background:transparent;")
        icon.setFixedWidth(44)

        col = QVBoxLayout()
        lm = QLabel(message)
        lm.setStyleSheet("font-size:14px; font-weight:600; color:#1a2332; background:transparent;")
        lm.setWordWrap(True)
        col.addWidget(lm)
        if detail:
            ld = QLabel(detail)
            ld.setStyleSheet("font-size:12px; color:#6b7a8d; background:transparent;")
            ld.setWordWrap(True)
            col.addWidget(ld)

        top.addWidget(icon)
        top.addLayout(col)
        root.addLayout(top)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background:#e2e8f0; border:none; max-height:1px;")
        root.addWidget(sep)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        if mode == "question":
            btn_no = QPushButton(cancel_text)
            btn_no.setFixedHeight(36)
            btn_no.setStyleSheet("""
                QPushButton {
                    background:white; color:#1a2332;
                    border:1px solid #e2e8f0; border-radius:6px;
                    font-size:13px; padding:0 16px;
                }
                QPushButton:hover { background:#f4f6f9; }
            """)
            btn_no.clicked.connect(self.reject)
            btn_row.addWidget(btn_no)
            btn_row.addSpacing(8)

        danger = mode == "error" or "видалити" in confirm_text.lower()
        color  = "#ef4444" if danger else "#f5a623"
        hover  = "#dc2626" if danger else "#e09410"
        btn_ok = QPushButton(confirm_text)
        btn_ok.setFixedHeight(36)
        btn_ok.setStyleSheet(f"""
            QPushButton {{
                background:{color}; color:white; border:none;
                border-radius:6px; font-size:13px; font-weight:600; padding:0 16px;
            }}
            QPushButton:hover {{ background:{hover}; }}
        """)
        btn_ok.clicked.connect(self._ok)
        btn_row.addWidget(btn_ok)
        root.addLayout(btn_row)

    def _ok(self):
        self.confirmed = True
        self.accept()


# ── Зручні функції ────────────────────────────

def info(parent, title, message, detail=None):
    d = MsgDialog(parent, title, message, detail, mode="info", confirm_text="OK")
    d.exec_()

def warning(parent, title, message, detail=None):
    d = MsgDialog(parent, title, message, detail, mode="warning", confirm_text="OK")
    d.exec_()

def confirm(parent, title, message, confirm_text="Так",
            danger=False, detail=None) -> bool:
    mode = "error" if danger else "question"
    d = MsgDialog(parent, title, message, detail,
                  mode=mode, confirm_text=confirm_text)
    d.exec_()
    return d.confirmed
