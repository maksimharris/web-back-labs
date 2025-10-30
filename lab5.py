from flask import Blueprint, request, render_template, make_response,redirect, session
import psycopg2
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
    conn.commit()
    cur.close()
    conn.close()
    return render_template('lab5/success.html',login = login, authorized = True)
