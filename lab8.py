from flask import Blueprint, render_template, abort, request, session, redirect, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from os import path

lab8 = Blueprint('lab8', __name__)

@lab8.route('/lab8/')
def main():
    return render_template('/lab8/lab8.html')

@lab8.route('/lab8/login')
def login():
    return "Страница входа (lab8)"

@lab8.route('/lab8/register')
def register():
    return "Страница регистрации (lab8)"

@lab8.route('/lab8/articles')
def articles():
    return "Список статей (lab8)"

@lab8.route('/lab8/create')
def create():
    return "Создать статью (lab8)"