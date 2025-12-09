from flask import Blueprint, request, render_template, session, redirect

lab7 = Blueprint('lab7',__name__)

@lab7.route('/lab7/')
def main():
    return render_template('lab7/index.html')