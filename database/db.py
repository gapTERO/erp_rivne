import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

DB_CONFIG = {
    "host":     "ep-little-dream-alrb1y5k-pooler.c-3.eu-central-1.aws.neon.tech",
    "database": "neondb",
    "user":     "neondb_owner",
    "password": "npg_X89FuHGRYTKt",
    "port":     5432,
    "sslmode":  "require",
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

@contextmanager
def db_cursor():
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            yield cur
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_database():
    with db_cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id         SERIAL PRIMARY KEY,
                login      VARCHAR(50)  UNIQUE NOT NULL,
                password   VARCHAR(200) NOT NULL,
                role       VARCHAR(50)  NOT NULL DEFAULT 'operator',
                full_name  VARCHAR(200),
                is_active  BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS customers (
                id         SERIAL PRIMARY KEY,
                name       VARCHAR(200) NOT NULL,
                phone      VARCHAR(50),
                email      VARCHAR(100),
                address    TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS products (
                id           SERIAL PRIMARY KEY,
                name         VARCHAR(200) NOT NULL,
                unit         VARCHAR(20)  DEFAULT 'кг',
                price_per_kg DECIMAL(10,2) DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS orders (
                id            SERIAL PRIMARY KEY,
                order_number  VARCHAR(20) UNIQUE NOT NULL,
                customer_id   INTEGER REFERENCES customers(id),
                product_id    INTEGER REFERENCES products(id),
                quantity_kg   DECIMAL(10,2) NOT NULL,
                total_price   DECIMAL(10,2),
                status        VARCHAR(50) DEFAULT 'Нове',
                responsible   VARCHAR(100),
                delivery_date DATE,
                comment       TEXT,
                created_at    TIMESTAMP DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS warehouse (
                id            SERIAL PRIMARY KEY,
                material_name VARCHAR(200) NOT NULL,
                category      VARCHAR(50)  DEFAULT 'Сировина',
                quantity_kg   DECIMAL(10,2) DEFAULT 0,
                min_quantity  DECIMAL(10,2) DEFAULT 0,
                unit          VARCHAR(20)   DEFAULT 'кг',
                last_updated  TIMESTAMP DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS warehouse_operations (
                id             SERIAL PRIMARY KEY,
                warehouse_id   INTEGER REFERENCES warehouse(id),
                operation_type VARCHAR(50),
                quantity_kg    DECIMAL(10,2),
                supplier_name  VARCHAR(200),
                comment        TEXT,
                created_at     TIMESTAMP DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS production (
                id          SERIAL PRIMARY KEY,
                shift_date  DATE NOT NULL,
                shift_type  VARCHAR(50),
                master_name VARCHAR(100),
                product_id  INTEGER REFERENCES products(id),
                planned_kg  DECIMAL(10,2),
                actual_kg   DECIMAL(10,2) DEFAULT 0,
                status      VARCHAR(50) DEFAULT 'Відкрита',
                created_at  TIMESTAMP DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS suppliers (
                id             SERIAL PRIMARY KEY,
                name           VARCHAR(200) NOT NULL,
                edrpou         VARCHAR(20),
                contact_person VARCHAR(100),
                phone          VARCHAR(50),
                email          VARCHAR(100),
                address        TEXT,
                product_type   VARCHAR(200),
                rating         INTEGER DEFAULT 5,
                last_delivery  DATE,
                created_at     TIMESTAMP DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS employees (
                id         SERIAL PRIMARY KEY,
                full_name  VARCHAR(200) NOT NULL,
                position   VARCHAR(100),
                department VARCHAR(100),
                phone      VARCHAR(50),
                email      VARCHAR(100),
                hire_date  DATE,
                shift_type VARCHAR(50),
                status     VARCHAR(50) DEFAULT 'Активний',
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)

        cur.execute("SELECT COUNT(*) AS cnt FROM users")
        if cur.fetchone()["cnt"] == 0:
            cur.execute("""
                INSERT INTO users (login, password, role, full_name) VALUES
                ('admin',    'admin123',   'admin',       'Мельник Іван Петрович'),
                ('manager',  'manager123', 'manager',     'Ковальчук Ольга Степанівна'),
                ('sklad',    'sklad123',   'storekeeper', 'Павленко Тетяна Іванівна'),
                ('operator', 'oper123',    'operator',    'Кравченко Андрій Васильович');
            """)

        cur.execute("SELECT COUNT(*) AS cnt FROM products")
        if cur.fetchone()["cnt"] == 0:
            cur.execute("""
                INSERT INTO products (name, unit, price_per_kg) VALUES
                ('Борошно вищий сорт', 'кг', 18.50),
                ('Борошно 1-й сорт',   'кг', 16.00),
                ('Борошно 2-й сорт',   'кг', 13.50),
                ('Висівки пшеничні',   'кг',  6.00);
            """)

        cur.execute("SELECT COUNT(*) AS cnt FROM warehouse")
        if cur.fetchone()["cnt"] == 0:
            cur.execute("""
                INSERT INTO warehouse (material_name, category, quantity_kg, min_quantity) VALUES
                ('Пшениця',            'Сировина',         48500, 10000),
                ('Мішки паперові',     'Пакування',         2000,   500),
                ('Мішки поліетиленові','Пакування',         1500,   300),
                ('Борошно вищий сорт', 'Готова продукція',  8200,  1000),
                ('Борошно 1-й сорт',   'Готова продукція',  5100,  1000),
                ('Висівки пшеничні',   'Готова продукція',  3400,   500);
            """)

        cur.execute("SELECT COUNT(*) AS cnt FROM customers")
        if cur.fetchone()["cnt"] == 0:
            cur.execute("""
                INSERT INTO customers (name, phone, email) VALUES
                ('АТБ-Маркет',         '0800-300-100',  'zakaz@atbmarket.com'),
                ('Сільпо',             '044-490-88-00', 'supply@silpo.ua'),
                ('Новус',              '044-500-80-00', 'orders@novus.ua'),
                ('ФОП Ковальчук В.М.', '050-123-45-67', ''),
                ('Хліб Рівненський',   '0362-26-30-00', 'info@khlib.rv.ua');
            """)

        cur.execute("SELECT COUNT(*) AS cnt FROM suppliers")
        if cur.fetchone()["cnt"] == 0:
            cur.execute("""
                INSERT INTO suppliers (name, contact_person, phone, product_type, rating) VALUES
                ('Агро-Захід ТОВ', 'Бондаренко О.І.', '067-100-20-30', 'Пшениця',             5),
                ('Зерно-Трейд',    'Литвиненко В.П.', '050-200-30-40', 'Пшениця, Кукурудза',  4),
                ('УкрАгро Плюс',   'Семченко Р.А.',   '093-300-40-50', 'Пшениця',             5);
            """)

        cur.execute("SELECT COUNT(*) AS cnt FROM employees")
        if cur.fetchone()["cnt"] == 0:
            cur.execute("""
                INSERT INTO employees (full_name, position, department, phone, shift_type, status) VALUES
                ('Мельник Іван Петрович',       'Директор виробництва', 'Керівництво', '050-111-22-33', 'Денна', 'Активний'),
                ('Ковальчук Ольга Степанівна',  'Менеджер',             'Продажі',     '067-222-33-44', 'Денна', 'Активний'),
                ('Грищенко Василь Миколайович', 'Майстер зміни',        'Виробництво', '093-333-44-55', 'Нічна', 'Активний'),
                ('Павленко Тетяна Іванівна',    'Комірник',             'Склад',       '063-444-55-66', 'Денна', 'Активний'),
                ('Кравченко Андрій Васильович', 'Оператор мельниці',    'Виробництво', '098-555-66-77', 'Денна', 'Відпустка');
            """)

    print("✅ База даних ініціалізована!")
