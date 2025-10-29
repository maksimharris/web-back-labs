import datetime

from flask import Flask, url_for, request, redirect, abort, render_template

from lab1 import lab1

from lab2 import lab2

from lab3 import lab3

from lab4 import lab4

app = Flask(__name__)

app.secret_key = 'ыускуе_лун'
app.register_blueprint(lab1)
app.register_blueprint(lab2)
app.register_blueprint(lab3)
app.register_blueprint(lab4)
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