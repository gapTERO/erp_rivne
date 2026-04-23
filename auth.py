"""
Авторизація з базою даних Neon.
Таблиця users: id, login, password, role, full_name, is_active
"""

ROLE_ACCESS = {
    "admin":       [0, 1, 2, 3, 4, 5, 6],
    "manager":     [0, 1, 4, 6],
    "storekeeper": [0, 3, 4],
    "operator":    [0, 2, 3],
}

ROLE_NAMES = {
    "admin":       "Адміністратор",
    "manager":     "Менеджер",
    "storekeeper": "Комірник",
    "operator":    "Оператор виробництва",
}

# Резервні дані якщо БД недоступна
_FALLBACK_USERS = {
    "admin":    {"password": "admin123",   "role": "admin",       "full_name": "Мельник І.П."},
    "manager":  {"password": "manager123", "role": "manager",     "full_name": "Ковальчук О.С."},
    "sklad":    {"password": "sklad123",   "role": "storekeeper", "full_name": "Павленко Т.І."},
    "operator": {"password": "oper123",    "role": "operator",    "full_name": "Кравченко А.В."},
}


def authenticate(login: str, password: str):
    """
    Шукає користувача в БД, потім у резервному списку.
    Повертає {"role": ..., "full_name": ...} або None.
    """
    # ── Спроба з БД ───────────────────────────
    try:
        from database.db import db_cursor
        with db_cursor() as cur:
            cur.execute("""
                SELECT role, full_name
                FROM users
                WHERE login = %s
                  AND password = %s
                  AND is_active = TRUE
            """, (login, password))
            row = cur.fetchone()
            if row:
                return {"role": row["role"], "full_name": row["full_name"]}
            # логін є але пароль невірний — повертаємо None
            cur.execute("SELECT id FROM users WHERE login=%s", (login,))
            if cur.fetchone():
                return None   # логін знайдено, пароль неправильний
    except Exception:
        pass   # БД недоступна — переходимо до резерву

    # ── Резервний режим (без БД) ──────────────
    user = _FALLBACK_USERS.get(login)
    if user and user["password"] == password:
        return {"role": user["role"], "full_name": user["full_name"]}
    return None


def get_allowed_tabs(role: str):
    return ROLE_ACCESS.get(role, [0])
