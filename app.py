from flask import Flask, url_for, request, redirect, abort, render_template
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
</html>''',{
    'Content-Language':'ru',
    'From':'maksim.pisarev.1986@mail.ru',
    'Accept-Charset': 'utf-8'
}
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
access_log = []
@app.errorhandler(404)
def not_found(err):
    global count,access_log
    count += 1
    path = url_for("static",filename = '404.jpg')
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
@app.route("/lab1/not_query")
def not_query():
    return '''
<!doctype html>
<html>
    <body>
        400. Неправильный, некорректный запрос
    </body>
</html>
''',400
@app.route("/lab1/non_auth")
def non_auth():
    return '''
<!doctype html>
<html>
    <body>
        401. Не авторизован
    </body>
</html>''',401

@app.route("/lab1/no_rights")
def no_rights():
    return '''
<!doctype html>
<html>
    <body>
        403. Запрещено, нет прав
    </body>
</html>''',403
@app.route("/lab1/no_methods")
def no_methods():
    return '''
<!doctype html>
<html>
    <body>
        405. Метод не поддерживается
    </body>
</html>''',405
@app.route("/lab1/teapot")
def teapot():
    return '''
<!doctype html>
<html>
    <body>
        418. Я - чайник(шуточный код)
    </body>
</html>
''',418
@app.route("/lab1/works")
def works():
    global count
    return count/0
@app.errorhandler(500)
def in_errors(err):
    return '500. Внутренняя ошибка сервера.'

@app.route('/lab2/a/')
def a():
    return 'ok'

@app.route('/lab2/a')
def a_mod():
    return 'not ok'

flower_list = ['Роза', 'Тюльпан', 'Незабудка', 'Ромашка']

@app.route('/lab2/flowers/<int:flower_id>')
def flowers(flower_id):
    if 0 < flower_id >= len(flower_list):
        abort(404)
    else:
        return f'''
        <!doctype html>
        <html>
        <body>
            <h1>{flower_list[flower_id]}</h1>
            <p>Место в списке:{flower_id+1}</p>
            <a href="/lab2/all_flowers/">Смотреть все цветы</a>
        </body>
    </html>
    '''
    
@app.route('/lab2/add_flower/<name>')
def add_flower(name):
    flower_list.append(name)
    
    return f'''
<!doctype html>
<html>
    <body>
    <h1>Добавлен новый цветок</h1>
    <p>Название нового цветка:  {name} </p>
    <p>Всего цветов: {len(flower_list)}</p>
    <p>Полный список: {flower_list}</p>
    </body>
</html>
'''
@app.route('/lab2/add_flower/')
def add_flower_no_name():
    abort(400, 'вы не задали имя цветка')

@app.route('/lab2/all_flowers/')
def all_flower():
    return f'''
    <!doctype html>
    <html>
        <body>
            <h1>Все цветы</h1>
            <p>Количество цветов: {len(flower_list)}</p>
            <ul>
                {"".join(f"<li>{flower}</li>" for flower in flower_list)}
            </ul>
            <a href="/lab2/clear_flowers/">Очистить список</a>
        </body>
    </html>
    '''

@app.route('/lab2/clear_flowers/')
def clear_flowers():
    flower_list.clear()
    return redirect('/lab2/all_flowers/')

@app.route('/lab2/example')
def example():
    name = 'Максим Писарев'
    lab = 2
    group = 31
    course = 3
    fruits = [
        {'name': 'яблоки', 'price': 100},
        {'name': 'груши', 'price': 120},
        {'name': 'aпельcины', 'price': 80},
        {'name': 'мандарины', 'price': 95},
        {'name': 'Mангo', 'price': 321}
    ]
    return render_template('example.html',name=name,lab=lab,group=group,course=course,fruits=fruits)
@app.route('/lab2/')
def lab2():
    return render_template('lab2.html')

@app.route('/lab2/filters')
def filters():
    phrase = "О <b>сколько</b> <u>нам</u> <i>открытий</i> чудных..."
    return render_template('filter.html', phrase = phrase)