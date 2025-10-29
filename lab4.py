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
    error = None
    login_value = ""  # Для сохранения введенного логина
    
    if request.method == 'POST':
        login_value = request.form.get('login', '')
        password = request.form.get('password', '')
        
        # Проверка на пустые значения
        if not login_value:
            error = 'Не введён логин'
        elif not password:
            error = 'Не введён пароль'
        else:
            # Проверка существования пользователя и пароля
            if login_value in users and users[login_value]['password'] == password:
                # Успешная авторизация
                session['login'] = login_value
                session['user_name'] = users[login_value]['name']
                return redirect('/lab4/welcome')
            else:
                error = 'Неверный логин или пароль'
    
    return render_template('login.html', error=error, login_value=login_value)
@lab4.route('/lab4/welcome')
def welcome():
    if 'login' in session:
        authorized = True
        user_name = session.get('user_name', session['login'])  # Используем имя, если есть
    else:
        authorized = False
        user_name = ""
    
    return render_template('welcome.html', authorized=authorized, user_name=user_name)
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