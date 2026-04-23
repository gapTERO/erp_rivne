from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QScrollArea, QPushButton, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, QRect
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QFont, QCursor
from ui.styles import *

try:
    from database.db import db_cursor
    DB_AVAILABLE = True
except Exception:
    DB_AVAILABLE = False


# ── KPI картка ───────────────────────────────
class KpiCard(QFrame):
    def __init__(self, title, value, subtitle, color=ACCENT):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color:{WHITE};
                border:1px solid {BORDER};
                border-radius:10px;
            }}
        """)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(110)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(4)

        bar = QFrame()
        bar.setFixedHeight(3)
        bar.setStyleSheet(f"background:{color}; border-radius:2px; border:none;")
        lay.addWidget(bar)
        lay.addSpacing(4)

        lbl_t = QLabel(title)
        lbl_t.setStyleSheet(
            f"font-size:10px; color:{TEXT_SECONDARY}; font-weight:600; border:none;"
        )
        lay.addWidget(lbl_t)

        self.lbl_v = QLabel(value)
        self.lbl_v.setStyleSheet(
            f"font-size:30px; font-weight:700; color:{TEXT_PRIMARY}; border:none;"
        )
        lay.addWidget(self.lbl_v)

        self.lbl_s = QLabel(subtitle)
        self.lbl_s.setStyleSheet(
            f"font-size:11px; color:{TEXT_SECONDARY}; border:none;"
        )
        lay.addWidget(self.lbl_s)

    def set_value(self, v):   self.lbl_v.setText(str(v))
    def set_subtitle(self, s): self.lbl_s.setText(str(s))


# ── Інтерактивний графік ─────────────────────
class BarChart(QWidget):
    """Стовпчиковий графік з підсвіткою при кліку."""

    def __init__(self, on_day_click=None):
        super().__init__()
        self.on_day_click = on_day_click   # callback(label, value)
        self.data = []
        self.selected = -1                 # індекс вибраного дня
        self.hovered  = -1
        self.setMinimumHeight(160)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setMouseTracking(True)
        self._rects = []                   # зберігаємо координати стовпців

    def set_data(self, data):
        self.data = data
        self.selected = len(data) - 1     # за замовч. — останній день
        self._rects = []
        self.update()

    def _compute_rects(self):
        if not self.data:
            return []
        w, h = self.width(), self.height()
        pad_b, pad_t = 28, 22
        chart_h = h - pad_b - pad_t
        n = len(self.data)
        max_v = max(v for _, v in self.data) or 1
        slot_w = w / n
        rects = []
        for i, (_, val) in enumerate(self.data):
            bar_w = int(slot_w * 0.55)
            x     = int(i * slot_w + (slot_w - bar_w) / 2)
            bar_h = max(4, int((val / max_v) * chart_h))
            y     = pad_t + chart_h - bar_h
            rects.append((x, y, bar_w, bar_h))
        return rects

    def paintEvent(self, event):
        if not self.data:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        pad_b, pad_t = 28, 22
        chart_h = h - pad_b - pad_t

        rects = self._compute_rects()
        self._rects = rects
        slot_w = w / len(self.data)

        for i, ((label, val), (x, y, bw, bh)) in enumerate(zip(self.data, rects)):
            selected = (i == self.selected)
            hovered  = (i == self.hovered and not selected)

            if selected:
                color = QColor(ACCENT)
            elif hovered:
                color = QColor("#b0c0d4")
            else:
                color = QColor("#d1dbe8")

            p.setBrush(QBrush(color))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(x, y, bw, bh, 4, 4)

            # значення над стовпцем
            val_str = f"{val//1000}к" if val >= 1000 else str(val)
            f = QFont("Segoe UI", 8)
            f.setBold(selected)
            p.setFont(f)
            c = QColor(ACCENT) if selected else QColor(TEXT_SECONDARY)
            p.setPen(QPen(c))
            p.drawText(QRect(x - 4, y - 19, bw + 8, 16), Qt.AlignCenter, val_str)

            # підпис дня
            p.setPen(QPen(QColor(ACCENT if selected else TEXT_SECONDARY)))
            f2 = QFont("Segoe UI", 9)
            f2.setBold(selected)
            p.setFont(f2)
            p.drawText(QRect(x - 4, h - pad_b + 4, bw + 8, 20),
                       Qt.AlignCenter, label)

        p.end()

    def mouseMoveEvent(self, event):
        idx = self._hit(event.x())
        if idx != self.hovered:
            self.hovered = idx
            self.update()

    def mousePressEvent(self, event):
        idx = self._hit(event.x())
        if idx >= 0:
            self.selected = idx
            self.update()
            if self.on_day_click:
                label, val = self.data[idx]
                self.on_day_click(label, val)

    def leaveEvent(self, event):
        self.hovered = -1
        self.update()

    def _hit(self, mx):
        for i, (x, y, bw, bh) in enumerate(self._rects):
            if x - 4 <= mx <= x + bw + 4:
                return i
        return -1


# ── Бейдж статусу ────────────────────────────
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


# ── Головна вкладка ──────────────────────────
class HomeTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Демо-дані по днях для фільтрації таблиці при кліку
        self._week_orders = {}   # {"Пн": [...], ...}
        self._all_orders  = []
        self._build()
        self.refresh()
        QTimer(self).timeout.connect(self.refresh)

    def _build(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border:none;")

        container = QWidget()
        main = QVBoxLayout(container)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(14)

        # ── KPI рядок ──────────────────────────
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(12)
        self.kpi_orders = KpiCard("Замовлень сьогодні", "—", "за сьогодні",    ACCENT)
        self.kpi_wheat  = KpiCard("Пшениця на складі",  "—", "кг залишок",     "#3b82f6")
        self.kpi_prod   = KpiCard("Вироблено за добу",  "—", "кг борошна",     SUCCESS)
        self.kpi_staff  = KpiCard("Персонал активний",  "—", "співробітників",  "#8b5cf6")
        for c in [self.kpi_orders, self.kpi_wheat, self.kpi_prod, self.kpi_staff]:
            kpi_row.addWidget(c)
        main.addLayout(kpi_row)

        # ── Графік + склад ──────────────────────
        mid = QHBoxLayout()
        mid.setSpacing(12)

        chart_frame = QFrame()
        chart_frame.setStyleSheet(
            f"background:{WHITE}; border:1px solid {BORDER}; border-radius:10px;"
        )
        cf = QVBoxLayout(chart_frame)
        cf.setContentsMargins(16, 14, 16, 14)
        cf.setSpacing(6)

        ch_hdr = QHBoxLayout()
        self.lbl_chart_title = QLabel("Виробництво — 7 днів (кг)")
        self.lbl_chart_title.setStyleSheet(
            f"font-size:13px; font-weight:600; color:{TEXT_PRIMARY}; border:none;"
        )
        ch_hdr.addWidget(self.lbl_chart_title)
        ch_hdr.addStretch()
        self.lbl_chart_hint = QLabel("Натисніть на день щоб побачити замовлення")
        self.lbl_chart_hint.setStyleSheet(
            f"font-size:10px; color:{TEXT_SECONDARY}; border:none;"
        )
        ch_hdr.addWidget(self.lbl_chart_hint)
        cf.addLayout(ch_hdr)

        self.bar_chart = BarChart(on_day_click=self._on_day_click)
        self.bar_chart.setMinimumHeight(160)
        cf.addWidget(self.bar_chart)
        mid.addWidget(chart_frame, 3)

        # Стан складу
        stock_frame = QFrame()
        stock_frame.setStyleSheet(
            f"background:{WHITE}; border:1px solid {BORDER}; border-radius:10px;"
        )
        sf = QVBoxLayout(stock_frame)
        sf.setContentsMargins(16, 14, 16, 14)
        sf.setSpacing(6)
        lbl_st = QLabel("Стан складу")
        lbl_st.setStyleSheet(
            f"font-size:13px; font-weight:600; color:{TEXT_PRIMARY}; border:none;"
        )
        sf.addWidget(lbl_st)
        self.stock_layout = QVBoxLayout()
        self.stock_layout.setSpacing(5)
        sf.addLayout(self.stock_layout)
        sf.addStretch()
        mid.addWidget(stock_frame, 2)

        main.addLayout(mid)

        # ── Останні замовлення ──────────────────
        orders_frame = QFrame()
        orders_frame.setStyleSheet(
            f"background:{WHITE}; border:1px solid {BORDER}; border-radius:10px;"
        )
        of = QVBoxLayout(orders_frame)
        of.setContentsMargins(16, 14, 16, 14)
        of.setSpacing(10)

        oh = QHBoxLayout()
        self.lbl_orders_title = QLabel("Останні замовлення")
        self.lbl_orders_title.setStyleSheet(
            f"font-size:13px; font-weight:600; color:{TEXT_PRIMARY}; border:none;"
        )
        oh.addWidget(self.lbl_orders_title)
        oh.addStretch()

        btn_ref = QPushButton("Оновити")   # без емодзі — щоб влізало
        btn_ref.setFixedSize(90, 30)
        btn_ref.setObjectName("secondary")
        btn_ref.clicked.connect(self._on_refresh_click)
        oh.addWidget(btn_ref)
        of.addLayout(oh)

        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(5)
        self.orders_table.setHorizontalHeaderLabels(
            ["№", "Клієнт", "Продукт", "Кількість", "Статус"]
        )
        hh = self.orders_table.horizontalHeader()
        hh.setSectionResizeMode(QHeaderView.Stretch)
        hh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.orders_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.orders_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.orders_table.verticalHeader().setVisible(False)
        self.orders_table.setFixedHeight(220)
        self.orders_table.setAlternatingRowColors(True)
        self.orders_table.setStyleSheet(
            "QTableWidget { alternate-background-color:#fafafa; }"
        )
        of.addWidget(self.orders_table)
        main.addWidget(orders_frame)
        main.addStretch()

        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    # ── Клік на день графіка ─────────────────
    def _on_day_click(self, label, val):
        self.lbl_orders_title.setText(f"Замовлення — {label}  ({val:,} кг вироблено)".replace(",", " "))
        orders = self._week_orders.get(label, [])
        if orders:
            self._fill_orders_table(orders)
        else:
            # немає даних по дню — показуємо всі
            self._fill_orders_table(self._all_orders)
            self.lbl_orders_title.setText(f"{label}: дані відсутні — показано всі замовлення")

    def _on_refresh_click(self):
        self.lbl_orders_title.setText("Останні замовлення")
        self.refresh()

    # ── Оновлення ────────────────────────────
    def refresh(self):
        if DB_AVAILABLE:
            try:
                self._refresh_db()
                return
            except Exception:
                pass
        self._refresh_demo()

    def _refresh_db(self):
        with db_cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) AS c FROM orders WHERE DATE(created_at)=CURRENT_DATE"
            )
            self.kpi_orders.set_value(str(cur.fetchone()["c"]))

            cur.execute(
                "SELECT quantity_kg FROM warehouse WHERE material_name='Пшениця' LIMIT 1"
            )
            r = cur.fetchone()
            self.kpi_wheat.set_value(f"{int(r['quantity_kg']):,}".replace(",", " ") if r else "—")

            cur.execute(
                "SELECT COALESCE(SUM(actual_kg),0) AS t FROM production WHERE shift_date=CURRENT_DATE"
            )
            self.kpi_prod.set_value(f"{int(cur.fetchone()['t']):,}".replace(",", " "))

            cur.execute("SELECT COUNT(*) AS c FROM employees WHERE status='Активний'")
            self.kpi_staff.set_value(str(cur.fetchone()["c"]))

            cur.execute(
                "SELECT material_name, quantity_kg, min_quantity "
                "FROM warehouse ORDER BY category, material_name LIMIT 5"
            )
            self._update_stock(cur.fetchall())

            cur.execute("""
                SELECT o.order_number, c.name AS customer,
                       p.name AS product, o.quantity_kg, o.status
                FROM orders o
                JOIN customers c ON o.customer_id=c.id
                JOIN products  p ON o.product_id=p.id
                ORDER BY o.created_at DESC LIMIT 8
            """)
            self._all_orders = [dict(r) for r in cur.fetchall()]
            self._fill_orders_table(self._all_orders)

            cur.execute("""
                SELECT shift_date, COALESCE(SUM(actual_kg),0) AS total
                FROM production
                WHERE shift_date >= CURRENT_DATE - INTERVAL '6 days'
                GROUP BY shift_date ORDER BY shift_date
            """)
            days_uk = ["Пн","Вт","Ср","Чт","Пт","Сб","Нд"]
            chart_data = []
            for r in cur.fetchall():
                d = r["shift_date"]
                label = days_uk[d.weekday()]
                chart_data.append((label, int(r["total"])))
            if chart_data:
                self.bar_chart.set_data(chart_data)

    def _refresh_demo(self):
        self.kpi_orders.set_value("12")
        self.kpi_wheat.set_value("48 500")
        self.kpi_prod.set_value("32 000")
        self.kpi_staff.set_value("24")

        self._update_stock([
            {"material_name": "Пшениця",    "quantity_kg": 48500, "min_quantity": 10000},
            {"material_name": "Борошно в/с", "quantity_kg": 8200,  "min_quantity": 1000},
            {"material_name": "Борошно 1с",  "quantity_kg": 5100,  "min_quantity": 1000},
            {"material_name": "Мішки",       "quantity_kg": 2000,  "min_quantity": 500},
        ])

        # демо-замовлення по днях
        all_orders = [
            {"order_number":"#1042","customer":"АТБ-Маркет",    "product":"Борошно в/с","quantity_kg":5000, "status":"Виконано"},
            {"order_number":"#1043","customer":"Новус",          "product":"Борошно 1с", "quantity_kg":2000, "status":"В роботі"},
            {"order_number":"#1044","customer":"ФОП Ковальчук",  "product":"Висівки",    "quantity_kg":800,  "status":"Нове"},
            {"order_number":"#1045","customer":"Сільпо",         "product":"Борошно в/с","quantity_kg":10000,"status":"В роботі"},
            {"order_number":"#1041","customer":"Хліб Рівненський","product":"Борошно 2с","quantity_kg":3000, "status":"Виконано"},
        ]
        self._all_orders = all_orders

        # розбиваємо по днях для кліку
        self._week_orders = {
            "Пн": [all_orders[4]],
            "Вт": [all_orders[0], all_orders[2]],
            "Ср": [all_orders[3]],
            "Чт": [all_orders[1]],
            "Пт": [all_orders[0], all_orders[4]],
            "Сб": [all_orders[1], all_orders[2], all_orders[3]],
            "Нд": [all_orders[4]],
        }

        self._fill_orders_table(all_orders)

        self.bar_chart.set_data([
            ("Пн", 28000), ("Вт", 34000), ("Ср", 22000),
            ("Чт", 38000), ("Пт", 31000), ("Сб", 41000), ("Нд", 29000),
        ])

    def _update_stock(self, rows):
        while self.stock_layout.count():
            item = self.stock_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for row in rows:
            qty  = float(row["quantity_kg"])
            mq   = float(row["min_quantity"])
            ok   = qty >= mq

            f = QFrame()
            f.setStyleSheet(f"background:{BG_LIGHT}; border-radius:6px; border:none;")
            fl = QHBoxLayout(f)
            fl.setContentsMargins(10, 6, 10, 6)

            dot = QLabel("●")
            dot.setFixedWidth(14)
            dot.setStyleSheet(
                f"color:{SUCCESS if ok else DANGER}; font-size:10px; border:none;"
            )
            lbl_n = QLabel(row["material_name"])
            lbl_n.setStyleSheet(f"font-size:12px; color:{TEXT_PRIMARY}; border:none;")
            lbl_q = QLabel(f"{int(qty):,} кг".replace(",", " "))
            lbl_q.setStyleSheet(
                f"font-size:12px; font-weight:700; color:{TEXT_PRIMARY}; border:none;"
            )
            fl.addWidget(dot)
            fl.addWidget(lbl_n)
            fl.addStretch()
            fl.addWidget(lbl_q)
            self.stock_layout.addWidget(f)

    def _fill_orders_table(self, rows):
        self.orders_table.setRowCount(0)
        for row in rows:
            r = self.orders_table.rowCount()
            self.orders_table.insertRow(r)
            self.orders_table.setItem(r, 0, QTableWidgetItem(str(row["order_number"])))
            self.orders_table.setItem(r, 1, QTableWidgetItem(str(row["customer"])))
            self.orders_table.setItem(r, 2, QTableWidgetItem(str(row["product"])))
            qty = int(float(row["quantity_kg"]))
            self.orders_table.setItem(r, 3, QTableWidgetItem(f"{qty:,} кг".replace(",", " ")))
            self.orders_table.setCellWidget(r, 4, make_badge(row["status"]))
            self.orders_table.setRowHeight(r, 36)
