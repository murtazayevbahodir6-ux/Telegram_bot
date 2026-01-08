import sqlite3

DB_NAME = 'employee.db'


def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employee_db (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        first_name TEXT,
        last_name TEXT,
        direction TEXT,
        experience INTEGER,
        duty TEXT,
        registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()


def add_employee(user_id, first_name, last_name, direction, experience, duty):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO employee_db (user_id, first_name, last_name, direction, experience, duty)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, first_name, last_name, direction, experience, duty))

    conn.commit()
    conn.close()


def get_all_employees():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM employee_db")
    records = cursor.fetchall()
    conn.close()
    return records
