from flask import Blueprint, request, render_template, make_response,redirect, session
import psycopg2
from psycopg2.extras import RealDictCursor #модуль для работы с именами, а не с индексами столбцов
lab5  = Blueprint('lab5',__name__)
@lab5.route('/lab5')
def lab():
    return render_template('/lab5/lab5.html')
@lab5.route('/lab5/register', methods = ['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('lab5/register.html')
    login = request.form.get('login')
    password = request.form.get('password')
    if not(login or password):
        return render_template('lab5/register.html', error = 'Заполните все поля')
    conn = psycopg2.connect(
        host = "127.0.0.1",
        database = 'maxim_pisarev_knowledge_base',
        user = 'maxim_pisarev_knowledge_base',
        password = '123'
    )
    cur = conn.cursor()
    cur.execute(f"SELECT login FROM users WHERE login = '{login}';")
    #возврат результатов: fetchone() - первую строку, fetchall - все строки
    if cur.fetchone():
        cur.close()
        conn.close()
        return render_template('lab5/register.html', error = 'Такой пользователь не существует')
    cur.execute(f"INSERT INTO users (login,password) VALUES ('{login}','{password}');")
    conn.commit() #благодаря этой команде выполняется запись в саму БД
    cur.close()
    conn.close()
    return render_template('lab5/success.html',login = login, authorized = True)
@lab5.route('/lab5/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab5/login.html')
    login = request.form.get('login')
    password = request.form.get('password')
    if not (login or password):
        return render_template('lab5/login.html', error = 'Заполните поля')
    conn = psycopg2.connect(
        host = '127.0.0.1',
        database = 'maxim_pisarev_knowledge_base',
        user = 'maxim_pisarev_knowledge_base',
        password = '123'
    )
    cur = conn.cursor(cursor_factory= RealDictCursor)
    cur.execute(f"SELECT * FROM users WHERE login = '{login}';")
    user = cur.fetchone()
    if not user:
        cur.close() #освобождение памяти запроса 
        conn.close() #освобождение места для БД
        return render_template('lab5/login.html', error = 'Логин и/или пароль неверны')
    if user['password'] != password:
        cur.close()
        conn.close()
        return render_template('lab5/login.html', error = 'Логин и/или пароль неверны')
    session['login'] = login
    cur.close()
    conn.close()
    return render_template('lab5/success_login.html', login=login, authorized = True)