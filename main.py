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
        <a href="{{ url_for('products') }}">Product List</a><br>
        <a href="{{ url_for('search') }}">Search Products</a><br>
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
        return redirect(url_for('products'))
    else:
        return 'Invalid credentials'

@app.route('/products')
def products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template_string('''
        <ul>
        {% for product in products %}
            <li><a href="{{ url_for('product', product_id=product['id']) }}">{{ product['name'] }} - ${{ product['price'] }}</a></li>
        {% endfor %}
        </ul>
        <form action="/search" method="get">
            Search: <input type="text" name="query"><br>
            <input type="submit" value="Search">
        </form>
    ''', products=products)

@app.route('/product/<int:product_id>')
def product(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()
    if product:
        return render_template_string('''
            <h1>{{ product['name'] }}</h1>
            <p>Price: ${{ product['price'] }}</p>
        ''', product=product)
    else:
        return 'Product not found'

@app.route('/search')
def search():
    query = request.args.get('query')
    conn = get_db_connection()
    products = conn.execute(f"SELECT * FROM products WHERE name LIKE '%{query}%'").fetchall()
    conn.close()
    return render_template_string('''
        <form action="/search" method="get">
            Search: <input type="text" name="query"><br>
            <input type="submit" value="Search">
        </form>
        <ul>
        {% for product in products %}
            <li><a href="{{ url_for('product', product_id=product['id']) }}">{{ product['name'] }} - ${{ product['price'] }}</a></li>
        {% endfor %}
        </ul>
    ''', products=products)

if __name__ == '__main__':
    app.run(debug=True)