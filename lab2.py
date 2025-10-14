from flask import Blueprint, url_for, request, redirect, abort, render_template
import datetime
lab2 = Blueprint('lab2',__name__)
@lab2.route('/lab2/a/')
def a():
    return 'ok'

@lab2.route('/lab2/a')
def a_mod():
    return 'not ok'

flower_list = ['Роза', 'Тюльпан', 'Незабудка', 'Ромашка']

@lab2.route('/lab2/flowers/<int:flower_id>')
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
    
@lab2.route('/lab2/add_flower/<name>')
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
@lab2.route('/lab2/add_flower/')
def add_flower_no_name():
    abort(400, 'вы не задали имя цветка')

@lab2.route('/lab2/all_flowers/')
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

@lab2.route('/lab2/clear_flowers/')
def clear_flowers():
    flower_list.clear()
    return redirect('/lab2/all_flowers/')

@lab2.route('/lab2/example')
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
    return render_template('lab2/example.html',name=name,lab=lab,group=group,course=course,fruits=fruits)
@lab2.route('/lab2/')
def lab():
    return render_template('lab2/lab2.html')

@lab2.route('/lab2/filters')
def filters():
    phrase = "О <b>сколько</b> <u>нам</u> <i>открытий</i> чудных..."
    return render_template('filter.html', phrase = phrase)
@lab2.route('/lab2/calc/<int:a>/<int:b>')
def calc(a, b):
    return render_template('lab2/calc.html', a=a, b=b)

@lab2.route('/lab2/calc/')
def calc_default():
    return redirect('/lab2/calc/1/1')

@lab2.route('/lab2/calc/<int:a>')
def calc_one(a):
    return redirect(f'/lab2/calc/{a}/1')
@lab2.route('/lab2/books')
def books():
    books = [
        {'author': 'Михаил Булгаков', 'title': 'Мастер и Маргарита', 'genre': 'Роман', 'pages': 480},
        {'author': 'Антуан де Сент-Экзюпери', 'title': 'Маленький принц', 'genre': 'Притча', 'pages': 96},
        {'author': 'Джоан Роулинг', 'title': 'Гарри Поттер и философский камень', 'genre': 'Фэнтези', 'pages': 399},
        {'author': 'Артур Конан Дойл', 'title': 'Шерлок Холмс: Сборник рассказов', 'genre': 'Детектив', 'pages': 307},
        {'author': 'Агата Кристи', 'title': 'Убийство в Восточном экспрессе', 'genre': 'Детектив', 'pages': 256},
        {'author': 'Рэй Брэдбери', 'title': '451° по Фаренгейту', 'genre': 'Антиутопия', 'pages': 256},
        {'author': 'Стивен Кинг', 'title': 'Оно', 'genre': 'Ужасы', 'pages': 1138},
        {'author': 'Пауло Коэльо', 'title': 'Алхимик', 'genre': 'Роман', 'pages': 208},
        {'author': 'Олдос Хаксли', 'title': 'О дивный новый мир', 'genre': 'Антиутопия', 'pages': 288},
        {'author': 'Айзек Азимов', 'title': 'Я, робот', 'genre': 'Научная фантастика', 'pages': 253}
    ]
    return render_template('/lab2/books.html', books=books)
@lab2.route('/lab2/cars')
def berries_route():
    cars = [
        {'brand': 'Toyota', 'description': 'Надежный и экономичный семейный автомобиль','image':'lab2/Toyota.webp'},
        {'brand': 'Ford', 'description': 'Мощный и практичный полноразмерный пикап','image':'lab2/Ford.webp'},
        {'brand': 'BMW', 'description': 'Роскошный SUV с отличными ходовыми качествами','image':'lab2/BMW.webp'},
        {'brand': 'Tesla', 'description': 'Инновационный электрокар с автопилотом','image':'lab2/Tesla.webp'},
        {'brand': 'Mercedes-Benz', 'description': 'Премиальный бизнес-класс с богатой отделкой','image':'lab2/Mercedes.webp'},
        {'brand': 'Audi', 'description': 'Стильный немецкий седан с полным приводом','image':'lab2/Audi.webp'},
        {'brand': 'Honda', 'description': 'Компактный кроссовер с просторным салоном','image':'lab2/Honda.jpg'},
        {'brand': 'Chevrolet', 'description': 'Легендарный американский маслкар','image':'lab2/Chevrolet.webp'},
        {'brand': 'Volkswagen', 'description': 'Культовый компактный хэтчбек','image':'lab2/Volkswagen.webp'},
        {'brand': 'Porsche', 'description': 'Знаменитый спортивный автомобиль','image':'lab2/Porsche.webp'},
        {'brand': 'Hyundai', 'description': 'Современный кроссовер с ярким дизайном','image':'lab2/Hyundai.webp'},
        {'brand': 'Nissan', 'description': 'Популярный городской кроссовер','image':'lab2/Nissan.webp'},
        {'brand': 'Kia', 'description': 'Стильный и технологичный SUV','image':'lab2/Kia.webp'},
        {'brand': 'Lexus', 'description': 'Роскошный японский внедорожник','image':'lab2/Lexus.webp'},
        {'brand': 'Subaru', 'description': 'Полноприводный универсал повышенной проходимости','image':'lab2/Subaru.webp'},
        {'brand': 'Mazda', 'description': 'Элегантный кроссовер с отличной управляемостью','image':'lab2/Mazda.webp'},
        {'brand': 'Volvo', 'description': 'Безопасный и комфортный семейный SUV','image':'lab2/Volvo.webp'},
        {'brand': 'Jeep', 'description': 'Легендарный внедорожник для бездорожья','image':'lab2/Jeep.png'},
        {'brand': 'Land Rover', 'description': 'Эталон роскошного внедорожника','image':'lab2/Land-Rover.png'},
        {'brand': 'Ferrari', 'description': 'Эксклюзивный итальянский суперкар','image':'lab2/Ferrari.jpg'}
    ]
    return render_template('/lab2/cars.html', cars=cars)