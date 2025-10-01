from flask import Blueprint, url_for, request, redirect
import datetime
lab1 = Blueprint('lab1',__name__)

@lab1.route("/lab1/web")
def web():
    return """<!doctype html> 
        <html> 
            <body>
                <h1>web-сервер на flask</h1>
                <a href ="/lab1/author">author</a>
            </body>
        </html>""", 200, {
            'X-Server': 'sample',
            'Content-Type':'text/plain; charset=utf-8'
        }
@lab1.route("/lab1/author")
def author():
    name = "Писарев Максим Иванович"
    group = "ФБИ-31"
    faculty = "ФБ"
    return """<!doctype html>
        <html>
            <body>
                <p>Студент: """ + name + """</p>
                <p>Группа: """ + group + """</p>
                <p>Факультет: """+ faculty + """</p>
                <a href ="/lab1/web">web</a>
            </body>
        </html>"""
@lab1.route("/lab1/image")
def image():
    path = url_for("static",filename ='oak.jpg')
    path1 = url_for("static",filename ='lab1.css')
    return '''
<!doctype html>
<html>
    <body>
        <link rel="stylesheet" href="'''+path1+'''">
        <h1>Дуб</h1>
        <img src =" '''+ path +''' ">
    </body>
</html>''',{
    'Content-Language':'ru',
    'From':'maksim.pisarev.1986@mail.ru',
    'Accept-Charset': 'utf-8'
}
count = 0
@lab1.route("/lab1/counter")
def counter():
    global count
    count +=1
    time = datetime.datetime.today()
    url = request.url
    client_ip = request.remote_addr
    return '''
<!doctype html>
<html>
    <body>
        Сколько раз вы сюда заходили: ''' + str(count) + '''
        <hr>
        Дата и время: ''' + str(time) + '''<br>
        Запрошенный адрес: ''' + str(url) + '''<br>
        Ваш IP-адрес: ''' + str(client_ip) + '''<br>
        <hr>
        <a href="/lab1/clear_counter">Страница очищения счётчика</a>
    </body>
<html>
'''
@lab1.route("/lab1/info")
def info():
    return redirect("/lab1/author")
@lab1.route("/lab1/created")
def created():
    return '''
<!doctype html>
<html>
    <body>
        <h1>Создано успешно</h1>
        <div><i>что-то создано...</i></div>
    </body>
</html>
''', 201
access_log = []

@lab1.route("/lab1/clear_counter")
def clear_counter():
    global count
    count =0
    return '''
<!doctype html>
<html>
    <body>
        <div><i>Счётчик очищен!</i></div>
    </body>
</html>
'''

@lab1.route('/lab1')
def lab():
    return '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Лабораторная 1</title>
</head>
<body>
    Flask &ndash; фреймворк для создания веб-приложений на языке
    программирования Python, использующий набор инструментов
    Werkzeug, а также шаблонизатор Jinja2. Относится к категории так
    называемых микрофреймворков &ndash; минималистичных каркасов
    веб-приложений, сознательно предоставляющих лишь самые базовые возможности.
    <hr>
    <a href = "/">*ссылка*</a>
    <h2>Список роутов</h2>
    <ul>
        <li><a href = "/lab1/web">Создание первой страницы</a></li>
        <li><a href = "/lab1/author">Информация об авторе</a></li>
        <li><a href = "/lab1/image">Картинка</a></li>
        <li><a href = "/lab1/counter">Счётчик</a></li>
        <li><a href = "/lab1/info">Перенаправление на инфо об авторе</a></li>
        <li><a href = "/lab1/created">Код ответа 201</a></li>
        <li><a href = "/lab1/clear_counter">Очистка счётчика</a></li>
        <li><a href = "/index">Основное меню лабораторных</a></li>
        <li>Список ошибок<ul>
            <li><a href = "/lab1/not_query">400</a></li>
            <li><a href = "/lab1/non_auth">401</a></li>
            <li><a href = "/lab1/no_rights">403</a></li>
            <li><a href = "/lab1/no_methods">405</a></li>
            <li><a href = "/lab1/teapot">418</a></li>
        </ul></li>
        <li><a href = "/lab1/works">Работа обработчика ошибки 500.</a></li>
    </ul>
</body>
</html>
'''
@lab1.route("/lab1/not_query")
def not_query():
    return '''
<!doctype html>
<html>
    <body>
        400. Неправильный, некорректный запрос
    </body>
</html>
''',400
@lab1.route("/lab1/non_auth")
def non_auth():
    return '''
<!doctype html>
<html>
    <body>
        401. Не авторизован
    </body>
</html>''',401

@lab1.route("/lab1/no_rights")
def no_rights():
    return '''
<!doctype html>
<html>
    <body>
        403. Запрещено, нет прав
    </body>
</html>''',403
@lab1.route("/lab1/no_methods")
def no_methods():
    return '''
<!doctype html>
<html>
    <body>
        405. Метод не поддерживается
    </body>
</html>''',405
@lab1.route("/lab1/teapot")
def teapot():
    return '''
<!doctype html>
<html>
    <body>
        418. Я - чайник(шуточный код)
    </body>
</html>
''',418
@lab1.route("/lab1/works")
def works():
    global count
    return count/0
