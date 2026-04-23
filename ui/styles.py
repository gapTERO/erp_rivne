SIDEBAR_BG     = "#252d3a"
SIDEBAR_ACTIVE = "#323d4e"
ACCENT         = "#f5a623"
ACCENT_HOVER   = "#e09410"
WHITE          = "#ffffff"
BG_LIGHT       = "#f4f6f9"
BG_CARD        = "#ffffff"
TEXT_PRIMARY   = "#1a2332"
TEXT_SECONDARY = "#6b7a8d"
BORDER         = "#e2e8f0"
SUCCESS        = "#22c55e"
WARNING        = "#f59e0b"
DANGER         = "#ef4444"
INFO           = "#3b82f6"

STATUS_COLORS = {
    "Нове":       {"bg": "#dbeafe", "text": "#1d4ed8"},
    "В роботі":   {"bg": "#fef3c7", "text": "#92400e"},
    "Виконано":   {"bg": "#dcfce7", "text": "#15803d"},
    "Скасовано":  {"bg": "#fee2e2", "text": "#991b1b"},
    "Відкрита":   {"bg": "#fef3c7", "text": "#92400e"},
    "Закрита":    {"bg": "#dcfce7", "text": "#15803d"},
    "Активний":   {"bg": "#dcfce7", "text": "#15803d"},
    "Відпустка":  {"bg": "#fef3c7", "text": "#92400e"},
    "Звільнений": {"bg": "#fee2e2", "text": "#991b1b"},
}

MAIN_STYLE = f"""
QMainWindow, QDialog {{
    background-color: {BG_LIGHT};
    font-family: 'Segoe UI', Arial, sans-serif;
}}
QLabel {{
    color: {TEXT_PRIMARY};
    font-size: 13px;
}}
QPushButton {{
    background-color: {ACCENT};
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: {ACCENT_HOVER};
}}
QPushButton:pressed {{
    background-color: #c87e00;
}}
QPushButton#secondary {{
    background-color: transparent;
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
}}
QPushButton#secondary:hover {{
    background-color: {BG_LIGHT};
}}
QPushButton#danger {{
    background-color: {DANGER};
}}
QPushButton#danger:hover {{
    background-color: #dc2626;
}}
QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox, QDoubleSpinBox {{
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 7px 10px;
    font-size: 13px;
    background: white;
    color: {TEXT_PRIMARY};
}}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {{
    border-color: {ACCENT};
}}
QTableWidget {{
    background: white;
    border: 1px solid {BORDER};
    border-radius: 8px;
    gridline-color: {BORDER};
    font-size: 13px;
    color: {TEXT_PRIMARY};
}}
QTableWidget::item {{
    padding: 8px 10px;
}}
QTableWidget::item:selected {{
    background-color: #fff7ed;
    color: {TEXT_PRIMARY};
}}
QHeaderView::section {{
    background-color: {BG_LIGHT};
    color: {TEXT_SECONDARY};
    font-size: 11px;
    font-weight: 600;
    padding: 8px 10px;
    border: none;
    border-bottom: 1px solid {BORDER};
    border-right: 1px solid {BORDER};
}}
QHeaderView::section:hover {{
    background-color: #e8edf3;
    color: {TEXT_PRIMARY};
}}
QScrollBar:vertical {{
    background: {BG_LIGHT};
    width: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: #cbd5e1;
    border-radius: 3px;
}}
QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: 8px;
    background: white;
}}
QTabBar::tab {{
    background: transparent;
    padding: 8px 16px;
    color: {TEXT_SECONDARY};
    font-size: 13px;
}}
QTabBar::tab:selected {{
    color: {ACCENT};
    border-bottom: 2px solid {ACCENT};
    font-weight: 500;
}}
QGroupBox {{
    border: 1px solid {BORDER};
    border-radius: 8px;
    margin-top: 8px;
    padding-top: 8px;
    font-size: 13px;
    font-weight: 500;
    color: {TEXT_PRIMARY};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
}}
QMessageBox {{
    background-color: #ffffff;
}}
QMessageBox QLabel {{
    color: {TEXT_PRIMARY};
    font-size: 13px;
    background: transparent;
    min-width: 250px;
}}
QMessageBox QPushButton {{
    background-color: {ACCENT};
    color: white;
    border: none;
    padding: 7px 20px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
    min-width: 90px;
}}
QMessageBox QPushButton:hover {{
    background-color: {ACCENT_HOVER};
}}
QMessageBox QPushButton:last-child {{
    background-color: white;
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
}}
QMessageBox QPushButton:last-child:hover {{
    background-color: {BG_LIGHT};
}}
"""
