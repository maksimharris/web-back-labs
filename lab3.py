from flask import Blueprint, request, render_template, make_response,redirect

lab3  = Blueprint('lab3',__name__)

@lab3.route('/lab3')

def lab():
    
    name = request.cookies.get('name')
    name_color = request.cookies.get('name_color')
    age = request.cookies.get('age')
    
    return render_template('/lab3/lab3.html',name=name,name_color=name_color,age=age)
@lab3.route('/lab3/cookies')
def cookies():
    resp = make_response(redirect('/lab3'))
    resp.set_cookie('name','Alex',max_age=5)
    resp.set_cookie('age','20')
    resp.set_cookie('name_color','magenta')
    return resp
@lab3.route('/lab3/del_cookies')
def del_cookies():
    resp = make_response(redirect('/lab3'))
    resp.delete_cookie('name')

    resp.delete_cookie('age')

    resp.delete_cookie('name_color')

    resp.delete_cookie('color')

    resp.delete_cookie('background-color')

    resp.delete_cookie('font-size')

    resp.delete_cookie('border-style')
    return resp
@lab3.route('/lab3/form1')
def form1():
    errors = {}
    user = request.args.get('user')
    if user == '':
        errors['user'] = 'Заполнить поле!'
    age = request.args.get('age')
    if age == '':
        errors['age'] = 'Заполнить поле!'
    sex = request.args.get('sex')
    return render_template('/lab3/form1.html',user = user,
                                            age=age,
                                            sex=sex,
                                            errors = errors)
@lab3.route('/lab3/order')
def order():
    return render_template('/lab3/order.html')
price = 0
@lab3.route('/lab3/pay')
def pay():
    global price
    drink = request.args.get('drink')
    if drink == "coffee":
        price = 120
    elif drink == "black-tea":
        price = 80
    else:
        price = 70
    if request.args.get('milk') == "on":
        price +=30
    elif request.args.get('sugar') == "on":
        price +=10
    return render_template('/lab3/pay.html',price = price)
@lab3.route('/lab3/success')
def success():
    global price
    return render_template('/lab3/success.html',price = price)
@lab3.route('/lab3/settings')
def settings():
    color = request.args.get('color')
    b_color = request.args.get('background-color')
    f_size = request.args.get('font-size')
    border_style = request.args.get('border-style')
    
    if color or b_color or f_size or border_style:
        resp = make_response(redirect('/lab3/settings'))
        if color:
            resp.set_cookie('color', color)
        if b_color:
            resp.set_cookie('background-color', b_color)
        if f_size:
            resp.set_cookie('font-size', f_size)
        if border_style:
            resp.set_cookie('border-style', border_style)  # Сохраняем выбранное значение
        return resp
    
    color = request.cookies.get('color')
    b_color = request.cookies.get('background-color')
    f_size = request.cookies.get('font-size')
    border_style = request.cookies.get('border-style')  # Получаем для отображения в форме
    
    return render_template('/lab3/settings.html', 
                          color=color, 
                          b_color=b_color, 
                          f_size=f_size, 
                          border_style = border_style)
@lab3.route('/lab3/ticket')
def ticket():
    errors = {}
    # Получаем данные из формы
    fio = request.args.get('fio')
    shelf = request.args.get('shelf')
    linen = request.args.get('linen')
    baggage = request.args.get('baggage')
    age = request.args.get('age')
    departure = request.args.get('departure')
    destination = request.args.get('destination')
    date = request.args.get('date')
    insurance = request.args.get('insurance')
    # Проверяем, была ли форма отправлена
    form_submitted = any([fio, shelf, linen, baggage, age, departure, destination, date, insurance])
    if form_submitted:
        # Валидация полей
        if not fio or fio.strip() == '':
            errors['fio'] = 'Заполните ФИО пассажира'
        elif len(fio.strip()) < 2:
            errors['fio'] = 'ФИО должно содержать минимум 2 символа'
        
        if not shelf:
            errors['shelf'] = 'Выберите тип полки'
            
        if not linen:
            errors['linen'] = 'Укажите наличие белья'
            
        if not baggage:
            errors['baggage'] = 'Укажите наличие багажа'
            
        if not age:
            errors['age'] = 'Заполните возраст'
        else:
            try:
                age_int = int(age)
                if age_int < 1 or age_int > 120:
                    errors['age'] = 'Возраст должен быть от 1 до 120 лет'
            except ValueError:
                errors['age'] = 'Возраст должен быть числом'
        
        if not departure or departure.strip() == '':
            errors['departure'] = 'Заполните пункт выезда'
            
        if not destination or destination.strip() == '':
            errors['destination'] = 'Заполните пункт назначения'
            
        if not date:
            errors['date'] = 'Выберите дату поездки'
            
        if not insurance:
            errors['insurance'] = 'Укажите необходимость страховки'
    
    # Если форма отправлена и нет ошибок - показываем билет
    if form_submitted and not errors:
        # Рассчитываем стоимость
        base_price = 700 if int(age) < 18 else 1000
        ticket_type = "Детский билет" if int(age) < 18 else "Взрослый билет"
        
        total_price = base_price
        
        # Доплаты
        if shelf in ['lower', 'lower-side']:
            total_price += 100
            
        if linen == 'yes':
            total_price += 75
            
        if baggage == 'yes':
            total_price += 250
            
        if insurance == 'yes':
            total_price += 150
        
        return render_template('/lab3/ticket_result.html',
                             fio=fio, shelf=shelf, linen=linen, baggage=baggage,
                             age=age, departure=departure, destination=destination,
                             date=date, insurance=insurance, ticket_type=ticket_type,
                             total_price=total_price)
    
    # Иначе показываем форму
    return render_template('/lab3/ticket_form.html',
                         fio=fio or '', shelf=shelf or '', linen=linen or '',
                         baggage=baggage or '', age=age or '', departure=departure or '',
                         destination=destination or '', date=date or '', insurance=insurance or '',
                         errors=errors)
# Список товаров (смартфоны)
products = [
    {"id": 1, "name": "iPhone 15 Pro", "brand": "Apple", "price": 99990, "color": "Титановый", "storage": "128GB"},
    {"id": 2, "name": "Samsung Galaxy S24", "brand": "Samsung", "price": 79990, "color": "Черный", "storage": "256GB"},
    {"id": 3, "name": "Xiaomi 14", "brand": "Xiaomi", "price": 59990, "color": "Белый", "storage": "256GB"},
    {"id": 4, "name": "Google Pixel 8", "brand": "Google", "price": 54990, "color": "Серый", "storage": "128GB"},
    {"id": 5, "name": "OnePlus 12", "brand": "OnePlus", "price": 48990, "color": "Зеленый", "storage": "256GB"},
    {"id": 6, "name": "iPhone 14", "brand": "Apple", "price": 69990, "color": "Синий", "storage": "128GB"},
    {"id": 7, "name": "Samsung Galaxy A54", "brand": "Samsung", "price": 29990, "color": "Фиолетовый", "storage": "128GB"},
    {"id": 8, "name": "Xiaomi Redmi Note 13", "brand": "Xiaomi", "price": 19990, "color": "Черный", "storage": "64GB"},
    {"id": 9, "name": "Realme 11 Pro", "brand": "Realme", "price": 24990, "color": "Золотой", "storage": "128GB"},
    {"id": 10, "name": "iPhone SE", "brand": "Apple", "price": 39990, "color": "Красный", "storage": "64GB"},
    {"id": 11, "name": "Samsung Galaxy Z Flip5", "brand": "Samsung", "price": 89990, "color": "Сиреневый", "storage": "256GB"},
    {"id": 12, "name": "Google Pixel 7a", "brand": "Google", "price": 34990, "color": "Белый", "storage": "128GB"},
    {"id": 13, "name": "Xiaomi Poco X6", "brand": "Xiaomi", "price": 27990, "color": "Синий", "storage": "128GB"},
    {"id": 14, "name": "Nothing Phone 2", "brand": "Nothing", "price": 45990, "color": "Белый", "storage": "256GB"},
    {"id": 15, "name": "iPhone 15", "brand": "Apple", "price": 84990, "color": "Розовый", "storage": "128GB"},
    {"id": 16, "name": "Samsung Galaxy S23 FE", "brand": "Samsung", "price": 49990, "color": "Кремовый", "storage": "128GB"},
    {"id": 17, "name": "Xiaomi 13T", "brand": "Xiaomi", "price": 44990, "color": "Черный", "storage": "256GB"},
    {"id": 18, "name": "Motorola Edge 40", "brand": "Motorola", "price": 37990, "color": "Зеленый", "storage": "128GB"},
    {"id": 19, "name": "Honor 90", "brand": "Honor", "price": 32990, "color": "Серебристый", "storage": "256GB"},
    {"id": 20, "name": "Asus Zenfone 10", "brand": "Asus", "price": 59990, "color": "Красный", "storage": "128GB"}
]

@lab3.route('/lab3/products')
def products_search():
    # Получаем минимальную и максимальную цены из всех товаров
    min_price_all = min(product['price'] for product in products)
    max_price_all = max(product['price'] for product in products)
    
    # Получаем параметры из формы
    min_price_input = request.args.get('min_price')
    max_price_input = request.args.get('max_price')
    reset = request.args.get('reset')
    
    # Обработка сброса
    if reset == '1':
        resp = make_response(redirect('/lab3/products'))
        resp.set_cookie('min_price', '', expires=0)
        resp.set_cookie('max_price', '', expires=0)
        return resp
    
    # Получаем значения из куки, если форма не отправлена
    if not min_price_input and not max_price_input:
        min_price_input = request.cookies.get('min_price')
        max_price_input = request.cookies.get('max_price')
    
    # Инициализируем переменные
    min_price = None
    max_price = None
    filtered_products = products
    search_performed = False
    
    # Обработка введенных цен
    if min_price_input or max_price_input:
        search_performed = True
        
        try:
            if min_price_input:
                min_price = int(min_price_input)
            if max_price_input:
                max_price = int(max_price_input)
            
            # Исправляем если min > max
            if min_price is not None and max_price is not None and min_price > max_price:
                min_price, max_price = max_price, min_price
            
            # Фильтруем товары
            filtered_products = []
            for product in products:
                price = product['price']
                match_min = min_price is None or price >= min_price
                match_max = max_price is None or price <= max_price
                
                if match_min and match_max:
                    filtered_products.append(product)
            
            # Сохраняем в куки
            resp = make_response(render_template('/lab3/products.html',
                                               products=filtered_products,
                                               min_price=min_price_input,
                                               max_price=max_price_input,
                                               min_price_all=min_price_all,
                                               max_price_all=max_price_all,
                                               search_performed=search_performed,
                                               results_count=len(filtered_products)))
            
            if min_price_input:
                resp.set_cookie('min_price', min_price_input, max_age=60*60*24*30)
            if max_price_input:
                resp.set_cookie('max_price', max_price_input, max_age=60*60*24*30)
            
            return resp
            
        except ValueError:
            # Если введены некорректные значения
            filtered_products = products
    
    # Рендерим шаблон с текущими данными
    return render_template('/lab3/products.html',
                         products=filtered_products,
                         min_price=min_price_input or '',
                         max_price=max_price_input or '',
                         min_price_all=min_price_all,
                         max_price_all=max_price_all,
                         search_performed=search_performed,
                         results_count=len(filtered_products))
