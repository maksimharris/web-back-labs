from flask import Blueprint, request, render_template, make_response,redirect, session

lab4  = Blueprint('lab4',__name__)
@lab4.route('/lab4')
def lab():
    return render_template('/lab4/lab4.html')
@lab4.route('/lab4/div-form')
def div_form():
    return render_template('/lab4/div-form.html')
@lab4.route('/lab4/div', methods = ['POST'])
def div():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    if x1 == '' and x2 == '':
        return render_template('/lab4/div.html', error = 'Оба поля должны быть заполнены!')
    x1 = int(x1)
    x2 = int(x2)
    if x2 == 0:
        return render_template('/lab4/div.html', error = 'На ноль делить нельзя!')
    result = x1/x2
    return render_template('/lab4/div.html', x1=x1,x2=x2,result = result)
@lab4.route('/lab4/sum-form')
def sum_form():
    return render_template('/lab4/sum-form.html')
@lab4.route('/lab4/sum', methods = ['POST'])
def sum():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    if x1 == '':
        x1 = 0
    if x2 == '':
        x2 = 0
    x1 = int(x1)
    x2 = int(x2)
    result = x1 + x2
    return render_template('/lab4/sum.html',x1 = x1, x2 = x2, result = result)
@lab4.route('/lab4/mp-form')
def mp_form():
    return render_template('/lab4/mp-form.html')
@lab4.route('/lab4/mp', methods = ['POST'])
def mp():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    if x1 == '':
        x1 = 1
    if x2 == '':
        x2 = 1
    x1 = int(x1)
    x2 = int(x2)
    result = x1 * x2
    return render_template('/lab4/mp.html',x1 = x1, x2 = x2, result = result)
@lab4.route('/lab4/minus-form')
def minus_form():
    return render_template('/lab4/minus-form.html')
@lab4.route('/lab4/minus', methods = ['POST'])
def minus():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    if x1 == '' and x2 == '':
        return render_template('/lab4/minus.html', error = 'Оба поля должны быть заполнены!')
    x1 = int(x1)
    x2 = int(x2)
    result = x1 - x2
    return render_template('/lab4/minus.html',x1 = x1, x2 = x2, result = result)

@lab4.route('/lab4/step-form')
def step_form():
    return render_template('/lab4/step-form.html')
@lab4.route('/lab4/step', methods = ['POST'])
def step():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    if x1 == '':
        return render_template('/lab4/step.html', error = 'Поле должны быть заполнено!')
    if x2 == '':
        x2 = 0
    x1 = int(x1)
    x2 = int(x2)
    result = x1 ** x2
    return render_template('/lab4/step.html',x1 = x1, x2 = x2, result = result)
tree_count = 0 
@lab4.route('/lab4/tree', methods = ['GET','POST'])
def tree():
    global tree_count
    if request.method == 'GET': #обработчик простого входа
        return render_template('lab4/tree.html',tree_count = tree_count)
    #if request.method == 'POST: - обработчик нажатия
        #operation = request.form.get('operation') - если метода будет больше, чем 2
    operation = request.form.get('operation')
    if operation == 'cut' and tree_count>0:
        tree_count -=1
    elif operation == 'plant':
        tree_count +=1
    return redirect('/lab4/tree')
# Список пользователей с дополнительной информацией
users = {
    'alex': {
        'password': '123',
        'name': 'Александр Петров',
        'gender': 'Мужской'
    },
    'bob': {
        'password': '555',
        'name': 'Боб Мёрфи', 
        'gender': 'Женский'
    },
    'max': {
        'password': '473',
        'name': 'Макс Писарев',
        'gender': 'Мужской'
    },
    'roma':{
        'password': '163',
        'name': 'Рима Горкунова',
        'gender': 'Женский'
    }
}

@lab4.route('/lab4/login', methods=['GET', 'POST'])
def login():
    error = ''
    login_value = ""
    
    if request.method == 'POST':
        login_value = request.form.get('login', '')
        password = request.form.get('password', '')
        
        if not login_value:
            error = 'Не введён логин'
        elif not password:
            error = 'Не введён пароль'
        else:
            if login_value in users and users[login_value]['password'] == password:
                session['login'] = login_value
                session['user_name'] = users[login_value]['name']
                return redirect('/lab4/welcome')
            else:
                error = 'Неверный логин или пароль'
    
    return render_template('/lab4/login.html', error=error, login_value=login_value, authorized=False)
@lab4.route('/lab4/welcome')
def welcome():
    if 'login' in session:
        authorized = True
        user_name = session.get('user_name', session['login'])  # Используем имя, если есть
    else:
        authorized = False
        user_name = ""
    
    return render_template('/lab4/welcome.html', authorized=authorized, user_name=user_name)
@lab4.route('/lab4/logout', methods = ['POST'])
def logout():
    session.pop('login', None)
    return redirect('/lab4/login')
@lab4.route('/lab4/fridge', methods=['GET', 'POST'])
def fridge():
    temperature = None
    message = ''
    snowflakes = 0
    error = ''
    
    if request.method == 'POST':
        temp_str = request.form.get('temperature')
        
        # Проверка на пустое значение
        if not temp_str:
            error = 'Ошибка: не задана температура'
        else:
            try:
                temperature = int(temp_str)
                
                # Проверка диапазонов температуры
                if temperature < -12:
                    error = 'Не удалось установить температуру — слишком низкое значение'
                elif temperature > -1:
                    error = 'Не удалось установить температуру — слишком высокое значение'
                elif -12 <= temperature <= -9:
                    message = f'Установлена температура: {temperature}°C'
                    snowflakes = 3
                elif -8 <= temperature <= -5:
                    message = f'Установлена температура: {temperature}°C'
                    snowflakes = 2
                elif -4 <= temperature <= -1:
                    message = f'Установлена температура: {temperature}°C'
                    snowflakes = 1
                    
            except ValueError:
                error = 'Ошибка: введите целое число'
    
    return render_template('/lab4/fridge.html', 
                         temperature=temperature,
                         message=message,
                         snowflakes=snowflakes,
                         error=error)
@lab4.route('/lab4/grain_order', methods=['GET', 'POST'])
def grain_order():
    grain_type = ''
    weight = ''
    message = ''
    error = ''
    total_price = 0
    discount = 0
    final_price = 0
    
    # Цены на зерно
    prices = {
        'ячмень': 12000,
        'овёс': 8500,
        'пшеница': 9000,
        'рожь': 15000
    }
    
    if request.method == 'POST':
        grain_type = request.form.get('grain_type')
        weight_str = request.form.get('weight')
        
        # Проверка на пустой вес
        if not weight_str:
            error = 'Ошибка: не указан вес заказа'
        else:
            try:
                weight = float(weight_str)
                
                # Проверка веса на положительное значение
                if weight <= 0:
                    error = 'Ошибка: вес должен быть положительным числом'
                elif weight > 100:
                    error = 'Извините, такого объёма сейчас нет в наличии'
                elif weight > 10:
                    # Расчет скидки 10% для заказов более 10 тонн
                    base_price = prices.get(grain_type, 0) * weight
                    discount = base_price * 0.1
                    final_price = base_price - discount
                    message = f'Заказ успешно сформирован. Вы заказали {grain_type}. Вес: {weight} т. Сумма к оплате: {final_price:,.0f} руб. Применена скидка за большой объём 10% ({discount:,.0f} руб).'
                else:
                    # Расчет без скидки
                    final_price = prices.get(grain_type, 0) * weight
                    message = f'Заказ успешно сформирован. Вы заказали {grain_type}. Вес: {weight} т. Сумма к оплате: {final_price:,.0f} руб.'
                    
            except ValueError:
                error = 'Ошибка: введите корректное число для веса'
    
    return render_template('/lab4/grain_order.html',
                         grain_type=grain_type,
                         weight=weight,
                         message=message,
                         error=error,
                         prices=prices)
def require_auth():
    """Проверка авторизации"""
    if 'login' not in session:
        return redirect('/lab4/login')

@lab4.route('/lab4/register', methods=['GET', 'POST'])
def register():
    error = ''
    success = ''
    login_value = ''
    name_value = ''
    
    if request.method == 'POST':
        login_value = request.form.get('login', '').strip()
        name_value = request.form.get('name', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Валидация
        if not login_value:
            error = 'Не введён логин'
        elif not name_value:
            error = 'Не введено имя'
        elif not password:
            error = 'Не введён пароль'
        elif not confirm_password:
            error = 'Не введено подтверждение пароля'
        elif password != confirm_password:
            error = 'Пароли не совпадают'
        elif login_value in users:
            error = 'Пользователь с таким логином уже существует'
        else:
            # Регистрация нового пользователя
            users[login_value] = {
                'password': password,
                'name': name_value,
                'gender': request.form.get('gender', 'Не указан')
            }
            success = 'Регистрация прошла успешно! Теперь вы можете войти.'
            login_value = ''
            name_value = ''
    
    return render_template('/lab4/register.html', 
                         error=error, 
                         success=success,
                         login_value=login_value,
                         name_value=name_value)

@lab4.route('/lab4/users')
def users_list():
    # Проверка авторизации
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    return render_template('/lab4/users.html', 
                         users=users, 
                         current_user=session.get('login'))

@lab4.route('/lab4/delete_user', methods=['POST'])
def delete_user():
    # Проверка авторизации
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    current_user = session.get('login')
    if current_user in users:
        del users[current_user]
        session.clear()
        return redirect('/lab4/login')
    
    return redirect('/lab4/users')

@lab4.route('/lab4/edit_user', methods=['GET', 'POST'])
def edit_user():
    # Проверка авторизации
    auth_check = require_auth()
    if auth_check:
        return auth_check
    
    current_user = session.get('login')
    error = ''
    success = ''
    
    if request.method == 'POST':
        new_login = request.form.get('login', '').strip()
        new_name = request.form.get('name', '').strip()
        new_password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Валидация
        if not new_login:
            error = 'Не введён логин'
        elif not new_name:
            error = 'Не введено имя'
        elif new_password and new_password != confirm_password:
            error = 'Пароли не совпадают'
        elif new_login != current_user and new_login in users:
            error = 'Пользователь с таким логином уже существует'
        else:
            # Обновление данных пользователя
            if new_login != current_user:
                # Если логин изменился, создаем новую запись и удаляем старую
                users[new_login] = users.pop(current_user)
                session['login'] = new_login
            
            # Обновление остальных данных
            users[new_login]['name'] = new_name
            if new_password:
                users[new_login]['password'] = new_password
            users[new_login]['gender'] = request.form.get('gender', 'Не указан')
            
            session['user_name'] = new_name
            success = 'Данные успешно обновлены!'
    
    # Получение текущих данных пользователя
    user_data = users.get(current_user, {})
    
    return render_template('/lab4/edit_user.html',
                         error=error,
                         success=success,
                         login_value=current_user,
                         name_value=user_data.get('name', ''),
                         gender_value=user_data.get('gender', ''))

# Обновленный login для использования session['user_name']
