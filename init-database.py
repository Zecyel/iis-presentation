import sqlite3

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO users (username, password) VALUES (?, ?)",
            ('admin', 'password'))

cur.execute("INSERT INTO products (name, price) VALUES (?, ?)",
            ('Product1', 10.00))
cur.execute("INSERT INTO products (name, price) VALUES (?, ?)",
            ('Product2', 20.00))

connection.commit()
connection.close()