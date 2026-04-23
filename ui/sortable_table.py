from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt


class SortableTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._sort_col = -1
        self._sort_asc = True
        self._headers  = []
        self._raw_data = []   # зберігаємо останні дані для пересортування
        self.setSortingEnabled(False)
        self.horizontalHeader().setSectionsClickable(True)
        self.horizontalHeader().sectionClicked.connect(self._on_header)

    def set_headers(self, headers: list):
        self._headers = list(headers)
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

    # ── Зберігаємо дані при кожному заповненні ──
    def store_data(self, rows: list):
        """
        rows — список dict з ключами що відповідають стовпцям.
        Виклик перед fill_from_stored() для сортування.
        """
        self._raw_data = rows

    # ── Клік на заголовок ──────────────────────
    def _on_header(self, col: int):
        if self._sort_col == col:
            self._sort_asc = not self._sort_asc
        else:
            self._sort_col = col
            self._sort_asc = False
        self._update_header_labels()
        # Викликаємо зовнішній callback якщо є
        if hasattr(self, '_sort_callback') and self._sort_callback:
            self._sort_callback(col, self._sort_asc)

    def set_sort_callback(self, fn):
        """fn(col, asc) — викликається при кліку на заголовок."""
        self._sort_callback = fn

    def _update_header_labels(self):
        labels = []
        for i, h in enumerate(self._headers):
            if i == self._sort_col:
                labels.append(h + (" ▲" if self._sort_asc else " ▼"))
            else:
                labels.append(h)
        self.setHorizontalHeaderLabels(labels)

    def get_sort_state(self):
        return self._sort_col, self._sort_asc
