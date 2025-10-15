from flask import Blueprint, request, render_template, make_response,redirect

lab4  = Blueprint('lab4',__name__)

def lab():
    return render_template('/lab4/lab4.html',name=name,name_color=name_color,age=age)