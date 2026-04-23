from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QHeaderView, QFrame, QComboBox, QDialog, QFormLayout,
    QDateEdit, QTextEdit, QLineEdit, QTabWidget, QProgressBar,
    QDoubleSpinBox, QSpinBox, QScrollArea, QTableWidgetItem
)
from PyQt5.QtCore import Qt, QDate
from ui.styles import *
from ui.sortable_table import SortableTable
from ui.dialogs import confirm, info, warning


def make_badge(status):
    colors = STATUS_COLORS.get(status, {"bg": "#f1f5f9", "text": "#64748b"})
    w = QWidget()
    l = QHBoxLayout(w)
    l.setContentsMargins(4, 0, 4, 0)
    l.setAlignment(Qt.AlignCenter)
    lbl = QLabel(status)
    lbl.setAlignment(Qt.AlignCenter)
    lbl.setStyleSheet(
        f"background:{colors['bg']}; color:{colors['text']};"
        f"border-radius:10px; padding:3px 10px; font-size:11px; font-weight:600;"
    )
    l.addWidget(lbl)
    return w


def make_sortable_table(headers):
    """Створює SortableTable з типовими налаштуваннями."""
    t = SortableTable()
    t.set_headers(headers)
    t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    t.setEditTriggers(t.NoEditTriggers)
    t.setSelectionBehavior(t.SelectRows)
    t.setSelectionMode(t.SingleSelection)
    t.verticalHeader().setVisible(False)
    t.setAlternatingRowColors(True)
    t.setStyleSheet("QTableWidget { alternate-background-color:#fafafa; }")
    return t


def action_btn(text, slot, primary=False, danger=False):
    b = QPushButton(text)
    b.setFixedHeight(34)
    if danger:
        b.setStyleSheet(f"""
            QPushButton {{background:{DANGER};color:white;border:none;
            border-radius:6px;font-size:13px;padding:0 14px;}}
            QPushButton:hover{{background:#dc2626;}}""")
    elif primary:
        b.setStyleSheet(f"""
            QPushButton {{background:{ACCENT};color:white;border:none;
            border-radius:6px;font-size:13px;padding:0 14px;}}
            QPushButton:hover{{background:{ACCENT_HOVER};}}""")
    else:
        b.setStyleSheet(f"""
            QPushButton {{background:{WHITE};color:{TEXT_PRIMARY};
            border:1px solid {BORDER};border-radius:6px;
            font-size:13px;padding:0 14px;}}
            QPushButton:hover{{background:{BG_LIGHT};}}""")
    b.clicked.connect(slot)
    return b


# ─────────────────────────────────────────────
#  ВИРОБНИЦТВО
# ─────────────────────────────────────────────
class ProductionTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []
        self._build()
        self.refresh()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)

        # Панель зміни
        info_f = QFrame()
        info_f.setStyleSheet(
            f"background:{WHITE}; border:1px solid {BORDER}; border-radius:10px;"
        )
        il = QHBoxLayout(info_f)
        il.setContentsMargins(16, 12, 16, 12)

        self.lbl_shift = QLabel("Зміна: завантаження...")
        self.lbl_shift.setStyleSheet(
            f"font-size:14px; font-weight:600; color:{TEXT_PRIMARY}; border:none;"
        )
        il.addWidget(self.lbl_shift)
        il.addStretch()
        il.addWidget(action_btn("▶  Відкрити зміну", self._open_shift, primary=True))
        il.addWidget(action_btn("⏹  Закрити зміну",  self._close_shift))
        il.addWidget(action_btn("🔄", self.refresh))
        root.addWidget(info_f)

        lbl = QLabel("Виробничий план на сьогодні")
        lbl.setStyleSheet(f"font-size:14px; font-weight:600; color:{TEXT_PRIMARY};")
        root.addWidget(lbl)

        self.table = make_sortable_table(
            ["Продукт", "План (кг)", "Факт (кг)", "Залишок (кг)", "Виконання %", "Статус"]
        )
        self.table.set_sort_callback(self._on_sort)
        root.addWidget(self.table)

        bl = QHBoxLayout()
        bl.addWidget(action_btn("➕  Додати план",    self._add_plan,    primary=True))
        bl.addWidget(action_btn("📝  Внести факт",    self._enter_actual))
        bl.addStretch()
        root.addLayout(bl)

    def _on_sort(self, col, asc):
        # col 4=прогрес-бар, col 5=статус (widgets) — не сортуємо
        if col >= 4 or not self.data:
            return
        def key(r):
            if col >= len(r):
                return (1, "")
            v = r[col]
            try: return (0, float(str(v).replace(" ","")))
            except: return (1, str(v).lower())
        self.data.sort(key=key, reverse=not asc)
        self._fill()

    def refresh(self):
        self.data = []
        try:
            from database.db import db_cursor
            with db_cursor() as cur:
                cur.execute("""
                    SELECT p.name, pr.planned_kg, pr.actual_kg, pr.status
                    FROM production pr JOIN products p ON pr.product_id=p.id
                    WHERE pr.shift_date=CURRENT_DATE
                """)
                for r in cur.fetchall():
                    pl, fa = float(r["planned_kg"]), float(r["actual_kg"])
                    pct = min(100, int(fa/pl*100)) if pl else 0
                    self.data.append([r["name"], int(pl), int(fa), max(0,int(pl-fa)), pct, r["status"]])
        except Exception:
            pass
        if not self.data:
            self.data = [
                ["Борошно вищий сорт", 15000, 12300, 2700, 82, "Відкрита"],
                ["Борошно 1-й сорт",   8000,  5400,  2600, 68, "Відкрита"],
                ["Висівки пшеничні",   4000,  3800,  200,  95, "Закрита"],
            ]
        today = QDate.currentDate().toString("dd.MM.yyyy")
        self.lbl_shift.setText(f"Зміна: {today}  |  Майстер: Грищенко В.М.")
        self._fill()

    def _fill(self):
        self.table.setRowCount(len(self.data))
        for r, row in enumerate(self.data):
            product, plan, fact, remain, pct, status = row
            self.table.setItem(r, 0, QTableWidgetItem(str(product)))
            self.table.setItem(r, 1, QTableWidgetItem(f"{plan:,}".replace(",", " ")))
            self.table.setItem(r, 2, QTableWidgetItem(f"{fact:,}".replace(",", " ")))
            self.table.setItem(r, 3, QTableWidgetItem(f"{remain:,}".replace(",", " ")))
            bar = QProgressBar()
            bar.setValue(pct)
            bar.setFormat(f"{pct}%")
            bar.setTextVisible(True)
            c = SUCCESS if pct >= 80 else (WARNING if pct >= 50 else DANGER)
            bar.setStyleSheet(f"""
                QProgressBar {{border:none;border-radius:4px;background:#e2e8f0;height:18px;}}
                QProgressBar::chunk {{background:{c};border-radius:4px;}}
            """)
            self.table.setCellWidget(r, 4, bar)
            self.table.setCellWidget(r, 5, make_badge(status))
            self.table.setRowHeight(r, 40)

    def _open_shift(self):
        info(self, "Зміна", "Зміну відкрито!")

    def _close_shift(self):
        if confirm(self, "Закрити зміну", "Закрити поточну зміну?", "Так, закрити"):
            info(self, "Зміна", "Зміну закрито!")

    def _add_plan(self):
        info(self, "Додати план", "Форма додавання плану (в розробці)")

    def _enter_actual(self):
        row = self.table.currentRow()
        if row < 0:
            warning(self, "Увага", "Оберіть рядок зі списку.")
            return
        product = self.table.item(row, 0).text() if self.table.item(row, 0) else "?"
        info(self, "Внести факт", f"Введення факт. даних для: {product}")


# ─────────────────────────────────────────────
#  СКЛАД
# ─────────────────────────────────────────────
class WarehouseTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.raw_data  = []
        self.prod_data = []
        self._build()
        self.refresh()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)

        bl = QHBoxLayout()
        bl.addWidget(action_btn("📥  Прихід сировини", self._income, primary=True))
        bl.addWidget(action_btn("📤  Витрата",         self._expense))
        bl.addWidget(action_btn("📋  Інвентаризація",  self._inventory))
        bl.addStretch()
        bl.addWidget(action_btn("🔄  Оновити", self.refresh))
        root.addLayout(bl)

        tabs = QTabWidget()

        self.table_raw = make_sortable_table(
            ["Найменування", "Залишок", "Мін. норма", "Одиниця", "Статус"]
        )
        self.table_raw.set_sort_callback(lambda c,a: self._sort_tab(self.table_raw, self.raw_data, c, a))

        self.table_prod = make_sortable_table(
            ["Найменування", "Залишок", "Мін. норма", "Одиниця", "Статус"]
        )
        self.table_prod.set_sort_callback(lambda c,a: self._sort_tab(self.table_prod, self.prod_data, c, a))

        tabs.addTab(self._wrap(self.table_raw),  "🌾  Сировина")
        tabs.addTab(self._wrap(self.table_prod), "🏭  Готова продукція")
        root.addWidget(tabs)

    def _wrap(self, w):
        c = QWidget()
        l = QVBoxLayout(c)
        l.setContentsMargins(0, 8, 0, 0)
        l.addWidget(w)
        return c

    def _sort_tab(self, table, data, col, asc):
        # col 4 = Статус (widget) — не сортуємо, немає в даних
        if col >= 4 or not data:
            return
        def key(r):
            if col >= len(r):
                return (1, "")
            v = r[col]
            try: return (0, float(str(v).replace(" ","")))
            except: return (1, str(v).lower())
        data.sort(key=key, reverse=not asc)
        self._fill_table(table, data)

    def refresh(self):
        self.raw_data, self.prod_data = [], []
        try:
            from database.db import db_cursor
            with db_cursor() as cur:
                cur.execute("SELECT * FROM warehouse WHERE category IN ('Сировина','Пакування') ORDER BY material_name")
                for r in cur.fetchall():
                    self.raw_data.append([r["material_name"], float(r["quantity_kg"]), float(r["min_quantity"]), r["unit"]])
                cur.execute("SELECT * FROM warehouse WHERE category='Готова продукція' ORDER BY material_name")
                for r in cur.fetchall():
                    self.prod_data.append([r["material_name"], float(r["quantity_kg"]), float(r["min_quantity"]), r["unit"]])
        except Exception:
            pass
        if not self.raw_data:
            self.raw_data = [
                ["Пшениця", 48500, 10000, "кг"],
                ["Мішки паперові", 2000, 500, "шт"],
                ["Мішки поліетиленові", 1500, 300, "шт"],
            ]
        if not self.prod_data:
            self.prod_data = [
                ["Борошно вищий сорт", 8200, 1000, "кг"],
                ["Борошно 1-й сорт", 5100, 1000, "кг"],
                ["Висівки пшеничні", 3400, 500, "кг"],
            ]
        self._fill_table(self.table_raw, self.raw_data)
        self._fill_table(self.table_prod, self.prod_data)

    def _fill_table(self, table, data):
        table.setRowCount(len(data))
        for r, row in enumerate(data):
            name, qty, min_q, unit = row[0], row[1], row[2], row[3]
            ok = qty >= min_q
            table.setItem(r, 0, QTableWidgetItem(str(name)))
            table.setItem(r, 1, QTableWidgetItem(f"{int(qty):,}".replace(",", " ")))
            table.setItem(r, 2, QTableWidgetItem(f"{int(min_q):,}".replace(",", " ")))
            table.setItem(r, 3, QTableWidgetItem(str(unit)))
            status = "✅ Норма" if ok else "⚠️ Критично"
            c = {"bg": "#dcfce7","text":"#15803d"} if ok else {"bg":"#fee2e2","text":"#991b1b"}
            lbl = QLabel(status)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(
                f"background:{c['bg']};color:{c['text']};border-radius:10px;padding:3px 8px;font-size:11px;"
            )
            table.setCellWidget(r, 4, lbl)
            table.setRowHeight(r, 36)

    def _income(self):
        info(self, "Прихід", "Форма приходу сировини (в розробці)")

    def _expense(self):
        info(self, "Витрата", "Форма витрати (в розробці)")

    def _inventory(self):
        info(self, "Інвентаризація", "Форма інвентаризації (в розробці)")


# ─────────────────────────────────────────────
#  ПОСТАЧАЛЬНИКИ
# ─────────────────────────────────────────────
class SuppliersTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []
        self._build()
        self.refresh()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)

        bl = QHBoxLayout()
        bl.addWidget(action_btn("➕  Додати",    self._add, primary=True))
        bl.addWidget(action_btn("✏️  Редагувати", self._edit))
        bl.addWidget(action_btn("🗑  Видалити",   self._delete, danger=True))
        bl.addStretch()

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  Пошук постачальника...")
        self.search.setFixedWidth(240)
        self.search.textChanged.connect(self._filter)
        bl.addWidget(self.search)
        bl.addWidget(action_btn("🔄", self.refresh))
        root.addLayout(bl)

        self.table = make_sortable_table(
            ["Назва", "Контакт", "Телефон", "Продукція", "Рейтинг", "Остання поставка"]
        )
        self.table.set_sort_callback(self._on_sort)
        root.addWidget(self.table)

    def _on_sort(self, col, asc):
        def key(r):
            v = r[col]
            try: return (0, float(str(v).replace("⭐","")))
            except: return (1, str(v).lower())
        self.data.sort(key=key, reverse=not asc)
        self._fill(self.data)

    def refresh(self):
        self.data = []
        try:
            from database.db import db_cursor
            with db_cursor() as cur:
                cur.execute("SELECT * FROM suppliers ORDER BY name")
                for r in cur.fetchall():
                    self.data.append([
                        r["name"], r.get("contact_person",""), r.get("phone",""),
                        r.get("product_type",""), r.get("rating",0), str(r.get("last_delivery","") or "")
                    ])
        except Exception:
            pass
        if not self.data:
            self.data = [
                ["Агро-Захід ТОВ",  "Бондаренко О.І.", "067-100-20-30", "Пшениця",             5, "10.04.2026"],
                ["Зерно-Трейд",     "Литвиненко В.П.", "050-200-30-40", "Пшениця, Кукурудза",  4, "05.04.2026"],
                ["УкрАгро Плюс",    "Семченко Р.А.",   "093-300-40-50", "Пшениця",             5, "01.04.2026"],
            ]
        self._fill(self.data)

    def _fill(self, data):
        self.table.setRowCount(len(data))
        for r, row in enumerate(data):
            for c, val in enumerate(row):
                v = "⭐" * int(val) if c == 4 else str(val)
                self.table.setItem(r, c, QTableWidgetItem(v))
            self.table.setRowHeight(r, 36)

    def _filter(self):
        text = self.search.text().lower()
        filtered = [r for r in self.data if text in str(r[0]).lower()]
        self._fill(filtered)

    def _add(self):
        info(self, "Додати", "Форма додавання постачальника (в розробці)")

    def _edit(self):
        row = self.table.currentRow()
        if row < 0:
            warning(self, "Увага", "Оберіть постачальника зі списку.")
            return
        name = self.table.item(row, 0).text() if self.table.item(row, 0) else "?"
        info(self, "Редагувати", f"Редагування: {name} (в розробці)")

    def _delete(self):
        row = self.table.currentRow()
        if row < 0:
            warning(self, "Увага", "Оберіть постачальника зі списку.")
            return
        name = self.table.item(row, 0).text() if self.table.item(row, 0) else "?"
        if confirm(self, "Видалити постачальника",
                   f"Видалити постачальника «{name}»?",
                   confirm_text="Так, видалити", danger=True):
            info(self, "Видалено", f"Постачальника «{name}» видалено.")
            self.refresh()


# ─────────────────────────────────────────────
#  СПІВРОБІТНИКИ
# ─────────────────────────────────────────────
class EmployeesTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []
        self._build()
        self.refresh()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)

        bl = QHBoxLayout()
        bl.addWidget(action_btn("➕  Додати",      self._add, primary=True))
        bl.addWidget(action_btn("✏️  Редагувати",  self._edit))
        bl.addWidget(action_btn("🚪  Звільнити",   self._fire, danger=True))
        bl.addStretch()

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍  Пошук за ПІБ або посадою...")
        self.search.setFixedWidth(280)
        self.search.textChanged.connect(self._filter)
        bl.addWidget(self.search)
        bl.addWidget(action_btn("🔄", self.refresh))
        root.addLayout(bl)

        self.table = make_sortable_table(
            ["ПІБ", "Посада", "Відділ", "Телефон", "Зміна", "Статус"]
        )
        self.table.set_sort_callback(self._on_sort)
        root.addWidget(self.table)

    def _on_sort(self, col, asc):
        def key(r):
            return str(r[col]).lower()
        self.data.sort(key=key, reverse=not asc)
        self._fill(self.data)

    def refresh(self):
        self.data = []
        try:
            from database.db import db_cursor
            with db_cursor() as cur:
                cur.execute("SELECT * FROM employees ORDER BY full_name")
                for r in cur.fetchall():
                    self.data.append([
                        r["full_name"], r.get("position",""), r.get("department",""),
                        r.get("phone",""), r.get("shift_type",""), r.get("status","")
                    ])
        except Exception:
            pass
        if not self.data:
            self.data = [
                ["Мельник Іван Петрович",       "Директор виробництва", "Керівництво", "050-111-22-33", "Денна", "Активний"],
                ["Ковальчук Ольга Степанівна",  "Менеджер",             "Продажі",     "067-222-33-44", "Денна", "Активний"],
                ["Грищенко Василь Миколайович", "Майстер зміни",        "Виробництво", "093-333-44-55", "Нічна", "Активний"],
                ["Павленко Тетяна Іванівна",    "Комірник",             "Склад",       "063-444-55-66", "Денна", "Активний"],
                ["Кравченко Андрій Васильович", "Оператор мельниці",    "Виробництво", "098-555-66-77", "Денна", "Відпустка"],
            ]
        self._fill(self.data)

    def _fill(self, data):
        self.table.setRowCount(len(data))
        for r, row in enumerate(data):
            for c in range(5):
                self.table.setItem(r, c, QTableWidgetItem(str(row[c])))
            self.table.setCellWidget(r, 5, make_badge(row[5]))
            self.table.setRowHeight(r, 36)

    def _filter(self):
        text = self.search.text().lower()
        filtered = [r for r in self.data
                    if text in str(r[0]).lower() or text in str(r[1]).lower()]
        self._fill(filtered)

    def _add(self):
        info(self, "Додати", "Форма додавання співробітника (в розробці)")

    def _edit(self):
        row = self.table.currentRow()
        if row < 0:
            warning(self, "Увага", "Оберіть співробітника зі списку.")
            return
        name = self.table.item(row, 0).text() if self.table.item(row, 0) else "?"
        info(self, "Редагувати", f"Редагування: {name} (в розробці)")

    def _fire(self):
        row = self.table.currentRow()
        if row < 0:
            warning(self, "Увага", "Оберіть співробітника зі списку.")
            return
        name = self.table.item(row, 0).text() if self.table.item(row, 0) else "?"
        if confirm(self, "Звільнити співробітника",
                   f"Звільнити «{name}»?",
                   confirm_text="Так, звільнити", danger=True):
            info(self, "Виконано", f"«{name}» звільнено.")
            self.refresh()


# ─────────────────────────────────────────────
#  ЗВІТИ
# ─────────────────────────────────────────────
class ReportsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(14)

        panel = QFrame()
        panel.setStyleSheet(
            f"background:{WHITE}; border:1px solid {BORDER}; border-radius:10px;"
        )
        pl = QHBoxLayout(panel)
        pl.setContentsMargins(14, 10, 14, 10)
        pl.setSpacing(12)

        pl.addWidget(QLabel("Звіт:"))
        self.cmb = QComboBox()
        self.cmb.setFixedWidth(260)
        self.cmb.addItems([
            "Звіт про виробництво за період",
            "Звіт залишків на складі",
            "Виконання замовлень",
            "Аналіз постачальників",
            "Фінансовий звіт",
        ])
        pl.addWidget(self.cmb)

        pl.addWidget(QLabel("З:"))
        self.d_from = QDateEdit()
        self.d_from.setDate(QDate.currentDate().addDays(-30))
        self.d_from.setCalendarPopup(True)
        self.d_from.setFixedWidth(120)
        pl.addWidget(self.d_from)

        pl.addWidget(QLabel("По:"))
        self.d_to = QDateEdit()
        self.d_to.setDate(QDate.currentDate())
        self.d_to.setCalendarPopup(True)
        self.d_to.setFixedWidth(120)
        pl.addWidget(self.d_to)

        pl.addStretch()
        pl.addWidget(action_btn("📊  Сформувати", self._generate, primary=True))
        pl.addWidget(action_btn("📄  PDF",        lambda: info(self,"PDF","Експорт PDF (в розробці)")))
        pl.addWidget(action_btn("📑  Excel",      lambda: info(self,"Excel","Експорт Excel (в розробці)")))
        root.addWidget(panel)

        preview = QFrame()
        preview.setStyleSheet(
            f"background:{WHITE}; border:1px solid {BORDER}; border-radius:10px;"
        )
        pv = QVBoxLayout(preview)
        pv.setContentsMargins(16, 14, 16, 14)

        self.lbl_title = QLabel("Оберіть звіт та натисніть «Сформувати»")
        self.lbl_title.setStyleSheet(
            f"font-size:15px; font-weight:600; color:{TEXT_PRIMARY};"
        )
        pv.addWidget(self.lbl_title)

        self.report_table = make_sortable_table(["Показник", "Значення"])
        pv.addWidget(self.report_table)
        root.addWidget(preview)

    def _generate(self):
        name  = self.cmb.currentText()
        df    = self.d_from.date().toString("dd.MM.yyyy")
        dt    = self.d_to.date().toString("dd.MM.yyyy")
        self.lbl_title.setText(f"{name}  ({df} — {dt})")

        if "виробництво" in name.lower():
            headers = ["Дата", "Продукт", "План (кг)", "Факт (кг)", "Виконання"]
            rows = [
                ["14.04.2026","Борошно в/с","15 000","13 200","88%"],
                ["14.04.2026","Борошно 1с", "8 000", "6 100", "76%"],
                ["15.04.2026","Борошно в/с","15 000","12 300","82%"],
            ]
        elif "залишк" in name.lower():
            headers = ["Найменування","Залишок","Мін. норма","Одиниця","Статус"]
            rows = [
                ["Пшениця","48 500","10 000","кг","✅ Норма"],
                ["Борошно в/с","8 200","1 000","кг","✅ Норма"],
                ["Висівки","3 400","500","кг","✅ Норма"],
            ]
        elif "замовл" in name.lower():
            headers = ["№","Клієнт","Продукт","Кількість","Сума","Статус"]
            rows = [
                ["#1042","АТБ-Маркет","Борошно в/с","5 000 кг","92 500 грн","Виконано"],
                ["#1043","Новус","Борошно 1с","2 000 кг","32 000 грн","В роботі"],
            ]
        else:
            headers = ["Показник","Значення"]
            rows = [
                ["Всього замовлень","12"],
                ["Виконано","8"],
                ["В роботі","3"],
                ["Загальна сума","314 300 грн"],
            ]

        self.report_table.set_headers(headers)
        self.report_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                self.report_table.setItem(r, c, QTableWidgetItem(val))
            self.report_table.setRowHeight(r, 36)
