import sqlite3

def create_sample_db():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    # Create the users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Create the inventory table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL
        )
    ''')

    # Insert sample users
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', 'admin'))
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('user1', 'pass1'))

    # Insert sample inventory items
    cursor.execute('INSERT INTO inventory (item_name, quantity) VALUES (?, ?)', ('Item A', 10))
    cursor.execute('INSERT INTO inventory (item_name, quantity) VALUES (?, ?)', ('Item B', 5))
    cursor.execute('INSERT INTO inventory (item_name, quantity) VALUES (?, ?)', ('Item C', 15))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_sample_db()
    print("database created successfully.")
