from flask import Flask, request, render_template_string, redirect, url_for
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template_string('''
        <form action="/login" method="post">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    ''')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = get_db_connection()
    user = conn.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'").fetchone()
    conn.close()
    if user:
        return redirect(url_for('search'))
    else:
        return 'Invalid credentials'

@app.route('/search')
def search():
    query = request.args.get('query')
    conn = get_db_connection()
    if query:
        conn.executescript(f"""
            CREATE TEMP TABLE temp_products AS
            SELECT * FROM products WHERE name LIKE '%{query}%';
        """)
        products = conn.execute('SELECT * FROM temp_products').fetchall()
    else:
        products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template_string('''
        <form action="/search" method="get">
            Search: <input type="text" name="query"><br>
            <input type="submit" value="Search">
        </form>
        <ul>
        {% for product in products %}
            <li><a href="{{ product['url'] }}">{{ product['name'] }} - ${{ product['price'] }}</a></li>
        {% endfor %}
        </ul>
    ''', products=products)

if __name__ == '__main__':
    app.run(debug=True)