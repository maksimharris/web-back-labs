from flask import Blueprint, request, render_template, make_response,redirect

lab3  = Blueprint('lab3',__name__)

@lab3.route('/lab3')

def lab():
    name = request.cookies.get('name')
    name_color = request.cookies.get('name_color')
    return render_template('/lab3/lab3.html',name=name,name_color=name_color)
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
