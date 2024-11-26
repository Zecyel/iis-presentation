import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO users (username, password) VALUES (?, ?)",
            ('admin', 'password'))

cur.execute("INSERT INTO products (name, price, url) VALUES (?, ?, ?)",
            ('Product1', 10.00, 'http://example.com/product1'))
cur.execute("INSERT INTO products (name, price, url) VALUES (?, ?, ?)",
            ('Product2', 20.00, 'http://example.com/product2'))

connection.commit()
connection.close()