from flask import Blueprint, request, render_template, session, redirect
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from os import path
from flask import current_app

lab6 = Blueprint('lab6', __name__)

def db_connect():
    if current_app.config['DB_TYPE'] == 'postgres':
        conn = psycopg2.connect(
            host="127.0.0.1",
            database='maxim_pisarev_knowledge_base',
            user='maxim_pisarev_knowledge_base',
            password='123'
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
    else:
        dir_path = path.dirname(path.realpath(__file__))
        db_path = path.join(dir_path, "databse.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
    return conn, cur

def db_close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()

@lab6.route('/lab6/')
def main():
    return render_template('/lab6/lab6.html')

@lab6.route('/lab6/json-rpc-api/', methods=['POST'])
def api():
    data = request.json
    id = data['id']
    
    if data['method'] == 'info': 
        conn, cur = db_connect()
        
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT number, tenant, price FROM offices ORDER BY number;")
        else:
            cur.execute("SELECT number, tenant, price FROM offices ORDER BY number;")
        
        offices_data = cur.fetchall()
        db_close(conn, cur)
        
        # Преобразуем в формат, ожидаемый фронтендом
        offices_list = []
        for office in offices_data:
            offices_list.append({
                'number': office['number'],
                'tenant': office['tenant'] if office['tenant'] else "",
                'price': office['price']
            })
        
        return {
            'jsonrpc': '2.0',
            'result': offices_list,
            'id': id
        }
    
    # проверка авторизации и выдача ошибки в случае отсутствия логина
    login = session.get('login')
    if not login:
        return {
            'jsonrpc': '2.0',
            'error': {
                'code': 1,
                'message': 'Unauthorized'
            },
            'id': id
        }
    
    if data['method'] == 'booking':  # booking - бронирование кабинета (по номеру)
        office_number = data['params']
        conn, cur = db_connect()
        
        # Проверяем, не забронировал ли уже пользователь другой офис
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT number FROM offices WHERE tenant = %s;", (login,))
        else:
            cur.execute("SELECT number FROM offices WHERE tenant = ?;", (login,))
        
        user_has_office = cur.fetchone()
        if user_has_office:
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 5,
                    'message': 'You already have a booked office'
                },
                'id': id
            }
        
        # Проверяем, свободен ли выбранный офис
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT number FROM offices WHERE number = %s AND tenant IS NULL;", (office_number,))
        else:
            cur.execute("SELECT number FROM offices WHERE number = ? AND tenant IS NULL;", (office_number,))
        
        office_available = cur.fetchone()
        if not office_available:
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 2,
                    'message': 'Already booked'
                },
                'id': id
            }
        
        # Бронируем офис
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("UPDATE offices SET tenant = %s WHERE number = %s;", (login, office_number))
        else:
            cur.execute("UPDATE offices SET tenant = ? WHERE number = ?;", (login, office_number))
        
        db_close(conn, cur)
        return {
            'jsonrpc': '2.0',
            'result': 'success',
            'id': id
        }
    
    if data['method'] == 'cancellation':  # отмена
        office_number = data['params']
        conn, cur = db_connect()
        
        # Проверяем, существует ли офис и принадлежит ли он текущему пользователю
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT tenant FROM offices WHERE number = %s;", (office_number,))
        else:
            cur.execute("SELECT tenant FROM offices WHERE number = ?;", (office_number,))
        
        office = cur.fetchone()
        if not office:
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 4,
                    'message': 'Office not found'
                },
                'id': id
            }
        
        if office['tenant'] != login:
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 3,
                    'message': 'You are not the tenant of this office'
                },
                'id': id
            }
        
        # Освобождаем офис
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("UPDATE offices SET tenant = NULL WHERE number = %s;", (office_number,))
        else:
            cur.execute("UPDATE offices SET tenant = NULL WHERE number = ?;", (office_number,))
        
        db_close(conn, cur)
        return {
            'jsonrpc': '2.0',
            'result': 'cancellation successful',
            'id': id
        }
    
    # возвращаем ошибку, если метод нам неизвестен
    return {
        'jsonrpc': '2.0',
        'error': {
            'code': -32601,
            'message': 'Method not found'
        },
        'id': id
    }

@lab6.route('/lab6/check-user', methods=['POST'])
def check_user():
    data = request.json
    tenant_login = data.get('tenant')
    current_login = session.get('login')
    
    return {
        'is_current_user': tenant_login == current_login
    }

@lab6.route('/lab6/logout', methods=['POST'])
def logout():
    # Офисы остаются забронированными даже после выхода пользователя
    session.clear()
    return redirect('/lab5/login')