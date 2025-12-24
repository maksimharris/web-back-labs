import datetime

from flask import Flask, url_for, request, redirect, abort, render_template, current_app
import os
from os import path
from flask_sqlalchemy import SQLAlchemy
from db.models import users
from flask_login import LoginManager
from db import db
from dotenv import load_dotenv  # Добавьте эту строку

load_dotenv()

from lab1 import lab1

from lab2 import lab2

from lab3 import lab3

from lab4 import lab4

from lab5 import lab5

from lab6 import lab6

from lab7 import lab7

from lab8 import lab8

from rgz import rgz
app = Flask(__name__)

login_manager = LoginManager()
login_manager.login_view = 'lab8.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_users(login_id):
    return users.query.get(int(login_id))

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ыускуе_лун')
app.config['DB_TYPE'] = os.getenv('DB_TYPE', 'postgres')

if app.config['DB_TYPE'] == 'postgres':
    db_name = 'maxim_pisarev_orm'
    db_user = 'maxim_pisarev_orm'
    db_password = '123'
    host_ip = '127.0.0.1'
    host_port = 5432

    app.config['SQLALCHEMY_DATABASE_URI'] = \
        f'postgresql://{db_user}:{db_password}@{host_ip}:{host_port}/{db_name}'
else:
    dir_path = path.dirname(path.realpath(__file__))
    db_path = path.join(dir_path, "maxim_pisarev_orm.db")
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

db.init_app(app)


app.register_blueprint(lab1)
app.register_blueprint(lab2)
app.register_blueprint(lab3)
app.register_blueprint(lab4)
app.register_blueprint(lab5)
app.register_blueprint(lab6)
app.register_blueprint(lab7)
app.register_blueprint(lab8)
app.register_blueprint(rgz)

count = 0
access_log = []
@app.errorhandler(404)

def not_found(err):
    global count,access_log
    count += 1
    path = url_for('static',filename = 'lab1/404.jpg')
    time = datetime.datetime.today()
    url = request.url
    client_ip = request.remote_addr
    notes = f'[{str(time)} пользователь {str(client_ip)}] зашёл на адрес {str(url)}'
    access_log.append(notes)
    log_html = ''
    for entry in reversed(access_log):
        log_html += f'<li>{entry}</li>'
    return '''
<!doctype html>
<html>
<style>
    img{
        width:500px;
        height:500px;
        position: relative;
        top:50px;
        left:450px;
        box-shadow: 0px 5px 10px;
        border-radius: 10%;
    }
    img:hover{
        box-shadow: 12px 3px 52px 33px rgba(45, 139, 211, 0.2);
    }
    body{
        background-color: #ecf7d7;
        color: #6b7a4e;
        font-family: 'Courier New', Courier, monospace;
        font-size: 18pt;
    }
    .oops{
        position:absolute;
        left:675px;
        top:25px;
    }
    .journal{
        position:absolute;
        top:600px;
        left:250px;
        font-size:10pt;
        width:1000px;
        height:500px;
    }
</style>
    <body>
        <div class = 'oops'>Упс!</div>
        <img src = "'''+path+'''">
        <div class = 'journal'>
            <h2>Журнал</h2>
            <ul>'''+log_html+'''</ul>
            <a href = "/lab1">Ссылка на корень сайта</a>
        </div>
    </body>
</html>''',404

@app.route("/")
@app.route("/index")


def main():
    return render_template('index.html')
@app.errorhandler(500)
def in_errors(err):
    return '500. Внутренняя ошибка сервера.'

if __name__ == '__main__':
    # Проверяем и создаем таблицы если их нет
    with app.app_context():
        # Импортируем здесь, чтобы избежать циклических импортов
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        # Проверяем есть ли таблица users
        if 'users' not in inspector.get_table_names():
            print("Создание таблиц в базе данных...")
            db.create_all()
            print("✅ Таблицы созданы!")
            
            # Создаем админа по умолчанию
            from werkzeug.security import generate_password_hash
            from db.models import users
            
            admin = users(
                login='admin',
                password=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Пользователь admin создан")
    
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=False
    )