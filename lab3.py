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
