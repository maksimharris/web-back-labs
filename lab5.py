from flask import Blueprint, request, render_template, make_response,redirect, session, current_app
import psycopg2
from psycopg2.extras import RealDictCursor #модуль для работы с именами, а не с индексами столбцов
from werkzeug.security import generate_password_hash, check_password_hash#генерация хэша пароля с солью(случайное число)
import sqlite3
from os import path
lab5  = Blueprint('lab5',__name__)
@lab5.route('/lab5')
def lab():
    return render_template('/lab5/lab5.html')
def db_connect():
    if current_app.config['DB_TYPE'] == 'postgres':
        conn = psycopg2.connect(
            host = "127.0.0.1",
            database = 'maxim_pisarev_knowledge_base',
            user = 'maxim_pisarev_knowledge_base',
            password = '123'
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
    else:
        dir_path = path.dirname(path.realpath(__file__))
        db_path = path.join(dir_path,"database.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.ROW
        cur = conn.cursor()
    return conn, cur
def db_close(conn,cur):
    conn.commit()
    cur.close()
    conn.close()
@lab5.route('/lab5/register', methods = ['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('lab5/register.html')
    login = request.form.get('login')
    password = request.form.get('password')
    if not(login or password):
        return render_template('lab5/register.html', error = 'Заполните все поля')
    conn,cur = db_connect()
    if current_app.config['DB_TYPE'] =='postgres':
        cur.execute("SELECT login FROM users WHERE login = %s;",(login, ))
    else:
        cur.execute("SELECT login FROM users WHERE login = ?;", (login))
 
    #возврат результатов: fetchone() - первую строку, fetchall - все строки
    if cur.fetchone():
        db_close(conn,cur)
        return render_template('lab5/register.html', error = 'Такой пользователь уже существует')
    password_hash = generate_password_hash(password)
    if current_app.config['DB_TYPE'] =='postgres':
        cur.execute("INSERT INTO users (login,password) VALUES (%s, %s);",(login,password_hash))
    else:
        cur.execute("INSERT INTO users (login,password) VALUES (?, ?);",(login,password_hash))

    db_close(conn,cur)
    return render_template('lab5/success.html',login = login, authorized = True)
@lab5.route('/lab5/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab5/login.html')
    login = request.form.get('login')
    password = request.form.get('password')
    if not (login or password):
        return render_template('lab5/login.html', error = 'Заполните поля')
    conn,cur = db_connect()
    if current_app.config['DB_TYPE'] =='postgres':
        cur.execute("SELECT * FROM users WHERE login =%s;",(login, ))
    else:
        cur.execute("SELECT * FROM users WHERE login =?;",(login, ))

    user = cur.fetchone()
    if not user:
        db_close(conn,cur)
        return render_template('lab5/login.html', error = 'Логин и/или пароль неверны')
    if not check_password_hash(user['password'],password):
        db_close(conn,cur)
        return render_template('lab5/login.html', error = 'Логин и/или пароль неверны')
    session['login'] = login
    db_close(conn,cur)
    return render_template('lab5/success_login.html', login=login, authorized = True)
@lab5.route('/lab5/create', methods = ['GET', 'POST'])
def create():
    login = session.get('login')
    if not login:
        return redirect('/lab5/login') #весь условный оператор отражает перенаправление неидентифицированного пользователя на страницу входа
    if request.method == 'GET':
        return render_template('lab5/create_article.html') #если адрес через GET, то показываем форму создания статьи
    title = request.form.get('name')
    article_text = request.form.get('article_text')
    if not(title or article_text):
        return render_template('lab5/create_article.html', error = 'Недостаточно данных')
    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] =='postgres':
        cur.execute("SELECT * FROM users WHERE login = %s;",(login, ))
    else:
        cur.execute("SELECT * FROM users WHERE login = ?;",(login, ))
    login_id = cur.fetchone()["id"]#находим нашего пользователя
    if current_app.config['DB_TYPE'] =='postgres':
        cur.execute("INSERT INTO articles(user_id,title,article_text) VALUES (%s,%s,%s);",(login_id,title,article_text))
    else:
        cur.execute("INSERT INTO articles(user_id,title,article_text) VALUES (?,?,?);",(login_id,title,article_text))

    db_close(conn,cur)
    return redirect('/lab5')
@lab5.route('/lab5/list', methods = ['GET','POST'])
def lists():
    login = session.get('login')
    if not login:
        return redirect('/lab5/login') #перенаправление на вход в базу, если пользователь неидентифицирован
    conn, cur  = db_connect()
    if current_app.config['DB_TYPE'] =='postgres':
        cur.execute("SELECT * FROM users WHERE login = %s;",(login,))
    else:
        cur.execute("SELECT * FROM users WHERE login = ?;",(login,))
    login_id = cur.fetchone()["id"]
    if current_app.config['DB_TYPE'] =='postgres':
        cur.execute("SELECT * FROM articles WHERE user_id = %s;",(login_id,)) #показ только статей пользователя
    else:
        cur.execute("SELECT * FROM articles WHERE user_id = ? ;",(login_id,))
    articles = cur.fetchall()
    db_close(conn,cur)
    if not articles:
            return render_template('/lab5/list.html', error = 'На данный момент у пользователя нет статей.')
    else:
        return render_template('/lab5/list.html', articles = articles)
@lab5.route('/lab5/logout')
def logout():
    session.clear()  # Очищаем сессию
    return redirect('/lab5/login')
@lab5.route('/lab5/edit/<int:article_id>', methods=['GET', 'POST'])
def edit_article(article_id):
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')
    
    conn, cur = db_connect()
    
    # Получаем статью и проверяем, что она принадлежит текущему пользователю
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("""
            SELECT a.* FROM articles a 
            JOIN users u ON a.user_id = u.id 
            WHERE a.id = %s AND u.login = %s;
        """, (article_id, login))
    else:
        cur.execute("""
            SELECT a.* FROM articles a 
            JOIN users u ON a.user_id = u.id 
            WHERE a.id = ? AND u.login = ?;
        """, (article_id, login))
    
    article = cur.fetchone()
    
    if not article:
        db_close(conn, cur)
        return render_template('lab5/error.html', error='Статья не найдена или у вас нет прав для ее редактирования')
    
    if request.method == 'GET':
        db_close(conn, cur)
        return render_template('lab5/edit_article.html', article=article)
    
    # Обработка формы редактирования
    title = request.form.get('name')
    article_text = request.form.get('article_text')
    
    if not title or not article_text:
        db_close(conn, cur)
        return render_template('lab5/edit_article.html', article=article, error='Заполните все поля')
    
    # Обновляем статью
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("""
            UPDATE articles SET title = %s, article_text = %s 
            WHERE id = %s;
        """, (title, article_text, article_id))
    else:
        cur.execute("""
            UPDATE articles SET title = ?, article_text = ? 
            WHERE id = ?;
        """, (title, article_text, article_id))
    
    db_close(conn, cur)
    return redirect('/lab5/list')

@lab5.route('/lab5/delete/<int:article_id>', methods=['POST'])
def delete_article(article_id):
    login = session.get('login')
    if not login:
        return redirect('/lab5/login')
    
    conn, cur = db_connect()
    
    # Проверяем, что статья принадлежит текущему пользователю
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("""
            SELECT a.* FROM articles a 
            JOIN users u ON a.user_id = u.id 
            WHERE a.id = %s AND u.login = %s;
        """, (article_id, login))
    else:
        cur.execute("""
            SELECT a.* FROM articles a 
            JOIN users u ON a.user_id = u.id 
            WHERE a.id = ? AND u.login = ?;
        """, (article_id, login))
    
    article = cur.fetchone()
    
    if not article:
        db_close(conn, cur)
        return render_template('lab5/error.html', error='Статья не найдена или у вас нет прав для ее удаления')
    
    # Удаляем статью
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("DELETE FROM articles WHERE id = %s;", (article_id,))
    else:
        cur.execute("DELETE FROM articles WHERE id = ?;", (article_id,))
    
    db_close(conn, cur)
    return redirect('/lab5/list')