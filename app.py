from flask import Flask, url_for, request, redirect
import datetime
app = Flask(__name__)

@app.route("/lab1/web")
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
@app.route("/lab1/author")
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
@app.route("/lab1/image")
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
</html>'''
count = 0
@app.route("/lab1/counter")
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
@app.route("/lab1/info")
def info():
    return redirect("/lab1/author")
@app.route("/lab1/created")
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
@app.errorhandler(404)
def not_found(err):
    return 'нет такой страницы',404
@app.route("/lab1/clear_counter")
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
@app.route("/")
@app.route("/index")
def main():
    return '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>НГТУ, ФБ, Лабораторные работы</title>
    <link rel="stylesheet" href="main.css">
</head>
<body>
    <header>
        НГТУ, ФБ, WEB-программирование, часть 2. Список лабораторных        
        <hr>
    </header>
        <main>
            <a href="/lab1">Первая лабораторная</a>
        </main>
    <footer>
        <hr>
        &copy; Писарев Максим Иванович, ФБИ-31, 3 курс, 2025
    </footer>
</body>
</html>
'''
@app.route('/lab1')
def lab1():
    return '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Лабораторная 1</title>
    <link rel="stylesheet" href="main.css">
</head>
<body>
    Flask &ndash; фреймворк для создания веб-приложений на языке
    программирования Python, использующий набор инструментов
    Werkzeug, а также шаблонизатор Jinja2. Относится к категории так
    называемых микрофреймворков &ndash; минималистичных каркасов
    веб-приложений, сознательно предоставляющих лишь самые базовые возможности.
    <hr>
    <a href = "/">*ссылка*</a>
</body>
</html>
'''