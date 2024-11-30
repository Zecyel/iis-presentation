# SQL注入攻防实战。

## 1. 登录校验绕过

当服务器启动了如下的服务时：

```python
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
```

可以通过构造 password 为 `' or 1=1 or '`，使得拼接后的 sql 查询字符串为 `SELECT * FROM users WHERE username = '123' AND password = '' or 1=1 or ''`，由于 1=1 始终为真，所以 .fetchone 必然能获得有效数据，从而绕过了登录校验。

## 2. 数据库注入攻击

例如有如下商品查询服务：

```python
@app.route('/search')
def search():
    query = request.args.get('query')
    conn = get_db_connection()
    conn.executescript(f"""
        CREATE TEMP TABLE temp_products AS
        SELECT * FROM products WHERE name LIKE '%{query}%';
    """)
    products = conn.execute('SELECT * FROM temp_products').fetchall()
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
```

一般来说，sqlite 的 `conn.execute` 函数并不允许执行多条语句。但是这段代码中使用了 `conn.executescript`，于是可以使用类似于 `%'; update products set url='https://www.kfchk.com/index.html'--` 的语句，使得数据库执行用户输入的 sql 语句，从而达到篡改数据库内部信息的功能。实际上，这个漏洞等价于远程代码执行漏洞，用户可以通过 SQL 语句执行任何命令，包括但不限于：篡改数据库数据，窃取数据库有价值的数据，攻击服务器宿主机。

## 3. XSS 跨站脚本攻击

以上的都是针对数据库的攻击，实际上还可以将脚本注入到用户界面。这可以通过 XSS 跨站脚本攻击来实现。

假如说有如下代码：

```python
@app.route('/users')
def users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    
    user_list = '<ul>'
    for user in users:
        user_list += f'<li>{ user["username"] }</li>'
    user_list += '</ul>'
    
    return user_list
```

那么不难发现，如果不加以限制，那么可以注册一个用户名叫做 `test</li><script>alert('kfc crazy thursday v me 50');</script><li>jack` 的用户，这样在所有人查看用户列表的时候都会弹出 `kfc crazy thursday v me 50` 的诈骗信息。