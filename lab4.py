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
users = [
    {'login':'alex','password':'123'},
    {'login':'bob','password':'555'},
    {'login':'max','password':'473'},
    {'login':'roma','password':'163'}
]
@lab4.route('/lab4/login', methods = ['GET','POST'])
def login():
    if request.method == 'GET':
        if 'login' in session:
            authorized = True
            login = session['login']
        else:
            login = ''
            authorized =  False
        return render_template('/lab4/login.html', authorized = authorized, login = login)
    login = request.form.get('login')
    password = request.form.get('password')
    for user in users:
        if login == user['login'] and password == user['password']:
            session['login'] = login
            return redirect('/lab4/login')
    error = 'Неверные логин и/или пароль' 
    return render_template('/lab4/login.html', error = error, authorized = False)
@lab4.route('/lab4/logout', methods = ['POST'])
def logout():
    session.pop('login', None)
    return redirect('/lab4/login')