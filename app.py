from flask import Flask, render_template, request, redirect, url_for, session,flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize database
def initialize_database():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS checkout (
    #         id INTEGER PRIMARY KEY,
    #         item_id INTEGER,
    #         user_id INTEGER,
    #         FOREIGN KEY(item_id) REFERENCES inventory(id),
    #         FOREIGN KEY(user_id) REFERENCES users(id)
    #     )
    # ''')
    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS users (
    #         id INTEGER PRIMARY KEY,
    #         username TEXT NOT NULL,
    #         password TEXT NOT NULL
    #     )
    # ''')
    # cursor.execute('''
    #     CREATE TABLE IF NOT EXISTS inventory (
    #         id INTEGER PRIMARY KEY,
    #         item_name TEXT NOT NULL,
    #         quantity INTEGER NOT NULL,
    #         owner TEXT NOT NULL,
    #         vendor Text NULL,
    #         cost INTEGER NOT NULL,
    #         total INTEGER NOT NULL
    #     )
    # ''')
    

    
    # cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', 'admin'))
    # cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('user1', 'pass1'))
    # cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('user2', 'pass2'))
    # cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('user3', 'pass3'))

    # cursor.execute('INSERT INTO inventory (item_name, quantity,owner,vendor,cost,total) VALUES (?, ?, ?, ?, ?, ?)', ('Item A', 10,'user1','ven1', 52, 520))
    # cursor.execute('INSERT INTO inventory (item_name, quantity,owner,vendor,cost,total) VALUES (?, ?, ?, ?, ?, ?)', ('Item B', 5,'user2','ven3', 20, 100))
    # cursor.execute('INSERT INTO inventory (item_name, quantity,owner,vendor,cost,total) VALUES (?, ?, ?, ?, ?, ?)', ('Item C', 15,'user3','ven5', 50, 750))
    conn.commit()
    conn.close()

# User authentication
def authenticate_user(username, password):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE username=? AND password=?', (username, password))
    user_id = cursor.fetchone()
    conn.close()
    return user_id

# Routes
@app.route('/')
def login():
    return render_template('login.html')

# ...
# ...

# Route to display user-specific inventory data and handle data addition
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' in session:
        username = session['username']
        if request.method == 'POST':
            item_name = request.form['item_name']
            quantity = int(request.form['quantity'])
            owner = request.form['owner']
            vendor = request.form['vendor']  # Get vendor from the form
            cost = int(request.form['cost'])  # Get cost from the form
            total = quantity * cost  # Calculate total

            conn = sqlite3.connect('inventory.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO inventory (item_name, quantity, owner, vendor, cost, total) VALUES (?, ?, ?, ?, ?, ?)',
                           (item_name, quantity, owner, vendor, cost, total))
            conn.commit()
            conn.close()

        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()

        if username == 'admin':
            cursor.execute('SELECT * FROM inventory')
            cursor.execute('SELECT DISTINCT owner FROM inventory')  # Fetch the list of users
            users = [row[0] for row in cursor.fetchall()]
        else:
            cursor.execute('SELECT * FROM inventory WHERE owner = ?', (username,))
            users = []

        inventory_data = cursor.fetchall()
        conn.close()

        return render_template('dashboard.html', inventory_data=inventory_data, username=username, users=users)
    else:
        return redirect(url_for('login'))


@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'username' in session:
        username = session['username']
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()

        if request.method == 'POST':
            item_id = int(request.form['item_id'])
            transfer_quantity = int(request.form['transfer_quantity'])
            user_to = request.form['user_to']

            # Fetch the selected item
            cursor.execute('SELECT item_name, quantity, cost FROM inventory WHERE id = ?', (item_id,))
            item = cursor.fetchone()
            item_name = item[0]
            available_quantity = item[1]
            item_cost = item[2]

            # Check if transfer quantity is valid
            if transfer_quantity <= 0 or transfer_quantity > available_quantity:
                error_message = 'Invalid transfer quantity'
            else:
                # Update quantity in current user's inventory
                cursor.execute('UPDATE inventory SET quantity = quantity - ? WHERE id = ?', (transfer_quantity, item_id))

                # Calculate the cost for transferred items
                transferred_cost = item_cost * transfer_quantity

                # Add transferred items to the target user's inventory
                cursor.execute('INSERT INTO inventory (item_name, quantity, owner, cost, total) VALUES (?, ?, ?, ?, ?)',
                               (item_name, transfer_quantity, user_to, item_cost, transferred_cost))

                conn.commit()

                flash(f'{transfer_quantity} {item_name} transferred to {user_to}!', 'success')
                return redirect(url_for('dashboard'))

        cursor.execute('SELECT id, item_name, quantity FROM inventory WHERE owner = ?', (username,))
        user_inventory = cursor.fetchall()

        cursor.execute('SELECT DISTINCT owner FROM inventory WHERE owner != ?', (username,))
        other_users = [row[0] for row in cursor.fetchall()]

        conn.close()

        return render_template('transfer.html', user_inventory=user_inventory, other_users=other_users)
    else:
        return redirect(url_for('login'))


# ...

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'username' in session and session['username'] == 'admin':
        if request.method == 'POST':
            new_username = request.form['new_username']
            new_password = request.form['new_password']

            conn = sqlite3.connect('inventory.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (new_username, new_password))
            user_id = cursor.lastrowid  # Get the ID of the newly added user

            # Add initial inventory items for the new user
            initial_item_names = request.form.getlist('initial_item_name[]')
            initial_item_quantities = request.form.getlist('initial_item_quantity[]')
            initial_item_costs = request.form.getlist('initial_item_cost[]')
            initial_item_vendors = request.form.getlist('initial_item_vendor[]')  # New line

            for name, quantity, cost, vendor in zip(initial_item_names, initial_item_quantities, initial_item_costs, initial_item_vendors):  # Modified line
                cursor.execute('INSERT INTO inventory (item_name, quantity, owner, vendor, cost, total) VALUES (?, ?, ?, ?, ?, ?)',
                               (name, quantity, new_username, vendor, cost, int(quantity) * int(cost)))  # Modified line

            conn.commit()
            conn.close()

            flash('New user and items added successfully!', 'success')
            return redirect(url_for('dashboard'))

        return render_template('add_user.html')
    else:
        return redirect(url_for('login'))


@app.route('/show')
def show_inventory():
    if 'username' in session:
        username = session['username']
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()

        if username == 'admin':
            cursor.execute('SELECT * FROM inventory')
        else:
            cursor.execute('SELECT * FROM inventory WHERE owner = ?', (username,))

        inventory_data = cursor.fetchall()
        conn.close()
        return render_template('show.html', inventory_data=inventory_data)
    else:
        return redirect(url_for('login'))


@app.route('/update', methods=['POST'])
def update_item():
    if 'username' in session:
        username = session['username']
        item_id = int(request.form['item_id'])
        new_quantity = int(request.form['new_quantity'])

        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()

        cursor.execute('UPDATE inventory SET quantity = ? WHERE id = ?', (new_quantity, item_id))
        conn.commit()
        conn.close()

        return redirect(url_for('show_inventory'))
    else:
        return redirect(url_for('login'))

# ...

@app.route('/delete', methods=['POST'])
def delete_item():
    item_id = int(request.form['item_id'])
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM inventory WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('show_inventory'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/error')
def error():
    return render_template('error.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']

    user_id = authenticate_user(username, password)

    if user_id:
        session['username'] = username
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('error'))

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)
