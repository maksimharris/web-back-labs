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
