from flask import Blueprint, request, render_template, session, redirect, jsonify, current_app, url_for
from flask_login import current_user, login_required
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from os import path
from datetime import datetime
import random
import json
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
from db.models import users, articles
from flask_login import login_user, login_required, current_user, logout_user




lab9 = Blueprint('lab9', __name__)

# Конфигурация
CONGRATULATIONS = [
    "С Новым годом! Пусть все мечты сбудутся! 🎄",
    "Желаю счастья, здоровья и удачи! ✨",
    "Пусть новый год принесёт радость и улыбки! 🎁",
    "Желаю мира, добра и тепла! ❄️",
    "Пусть ангел-хранитель оберегает вас! 😇",
    "Желаю новых достижений и успехов! 🚀",
    "Пусть каждый день будет счастливым! ☀️",
    "Желаю финансового благополучия! 💰",
    "Пусть любовь живет в вашем сердце! 💖",
    "Желаю ярких впечатлений и моментов! 🎉"
]

# Первые 5 подарков - для всех, остальные 5 - только для авторизованных
PUBLIC_GIFTS_COUNT = 5
TOTAL_GIFTS = 10

@lab9.route('/lab9/')
def main():
    return render_template('lab9/main.html')


def get_gift_positions():
    """Получает или генерирует позиции подарков (хранятся в сессии)"""
    if 'gift_positions' not in session:
        # Генерируем случайные позиции для 10 подарков
        positions = []
        for i in range(TOTAL_GIFTS):
            positions.append({
                'id': i + 1,
                'x': random.randint(5, 85),
                'y': random.randint(10, 80),
                'box_image': f'i ({43 + i}).webp',  # i (43) to i (52)
                'gift_image': f'i ({53 + i}).webp',  # i (53) to i (62)
                'congratulation': CONGRATULATIONS[i % len(CONGRATULATIONS)],
                'requires_auth': i >= PUBLIC_GIFTS_COUNT,  # Последние 5 требуют авторизации
                'is_opened': False,
                'opened_by': None,
                'opened_at': None
            })
        session['gift_positions'] = positions
        session.modified = True
    
    return session['gift_positions']

@lab9.route('/lab9/get_gifts')
def get_gifts():
    """Получение информации о подарках"""
    try:
        # Получаем позиции подарков
        gift_positions = get_gift_positions()
        
        # Получаем открытые подарки из сессии пользователя
        user_opened = session.get('user_gifts_opened', [])
        
        # Подготавливаем данные для фронтенда
        gifts_data = []
        total_unopened = 0
        
        for gift in gift_positions:
            gift_id = gift['id']
            is_opened = gift['is_opened']
            requires_auth = gift['requires_auth']
            opened_by_user = gift_id in user_opened
            
            # Проверяем, может ли пользователь открыть этот подарок
            can_user_open = True
            if requires_auth and not current_user.is_authenticated:
                can_user_open = False
            
            # Считаем неоткрытые подарки (для всех)
            if not is_opened:
                total_unopened += 1
            
            gifts_data.append({
                'id': gift_id,
                'x': gift['x'],
                'y': gift['y'],
                'box_image': gift['box_image'],
                'box_image_url': url_for('static', filename=f'lab9/{gift["box_image"]}'),
                'gift_image': gift['gift_image'],
                'gift_image_url': url_for('static', filename=f'lab9/{gift["gift_image"]}'),
                'congratulation': gift['congratulation'],
                'is_opened': is_opened,
                'requires_auth': requires_auth,
                'can_user_open': can_user_open,
                'opened_by_user': opened_by_user
            })
        
        return jsonify({
            'gifts': gifts_data,
            'total_unopened': total_unopened,
            'opened_count': len(user_opened),
            'max_gifts': 3,
            'user_authenticated': current_user.is_authenticated,
            'is_santa': False  # Пока отключим функционал Деда Мороза для простоты
        })
        
    except Exception as e:
        print(f"Error in get_gifts: {str(e)}")  # Для отладки
        return jsonify({'error': str(e)}), 500

@lab9.route('/lab9/open_gift/<int:gift_id>', methods=['POST'])
def open_gift(gift_id):
    """Открытие подарка"""
    try:
        # Инициализируем сессию если нужно
        if 'user_gifts_opened' not in session:
            session['user_gifts_opened'] = []
        
        user_opened = session['user_gifts_opened']
        
        # Проверяем лимит
        if len(user_opened) >= 3:
            return jsonify({
                'success': False,
                'message': '❌ Вы уже открыли максимальное количество подарков (3)!'
            })
        
        # Проверяем, не открывали ли уже этот подарк
        if gift_id in user_opened:
            return jsonify({
                'success': False,
                'message': '🎁 Этот подарок уже открыт вами!'
            })
        
        # Получаем информацию о подарке
        gift_positions = get_gift_positions()
        gift_info = None
        
        for gift in gift_positions:
            if gift['id'] == gift_id:
                gift_info = gift
                break
        
        if not gift_info:
            return jsonify({
                'success': False,
                'message': '❌ Подарок не найден!'
            })
        
        # Проверяем, не открыт ли уже подарок (для всех пользователей)
        if gift_info['is_opened']:
            return jsonify({
                'success': False,
                'message': '🎁 Этот подарок уже кто-то открыл!'
            })
        
        # Проверяем, требуется ли авторизация
        if gift_info['requires_auth'] and not current_user.is_authenticated:
            return jsonify({
                'success': False,
                'message': '🔐 Этот подарок доступен только авторизованным пользователям!'
            })
        
        # Открываем подарок для пользователя
        user_opened.append(gift_id)
        session['user_gifts_opened'] = user_opened
        
        # Отмечаем подарок как открытый в общем списке
        for gift in gift_positions:
            if gift['id'] == gift_id:
                gift['is_opened'] = True
                gift['opened_by'] = request.remote_addr
                gift['opened_at'] = datetime.now().isoformat()
                break
        
        session['gift_positions'] = gift_positions
        session.modified = True
        
        # Обновляем общее количество неоткрытых подарков
        total_unopened = sum(1 for g in gift_positions if not g['is_opened'])
        
        return jsonify({
            'success': True,
            'congratulation': gift_info['congratulation'],
            'gift_image': gift_info['gift_image'],
            'gift_image_url': url_for('static', filename=f'lab9/{gift_info["gift_image"]}'),
            'box_image': gift_info['box_image'],
            'box_image_url': url_for('static', filename=f'lab9/{gift_info["box_image"]}'),
            'opened_count': len(user_opened),
            'remaining': 3 - len(user_opened),
            'total_unopened': total_unopened,
            'message': f'🎉 Вы открыли подарок! Осталось открыть: {3 - len(user_opened)}'
        })
        
    except Exception as e:
        print(f"Error in open_gift: {str(e)}")  # Для отладки
        return jsonify({
            'success': False,
            'message': f'❌ Ошибка сервера: {str(e)}'
        })

@lab9.route('/lab9/refill_gifts', methods=['POST'])
@login_required
def refill_gifts():
    """Дед Мороз наполняет коробки заново"""
    try:
        # Простая проверка - любой авторизованный пользователь может быть Дедом Морозом
        # В реальном приложении здесь должна быть проверка через БД
        
        # Сбрасываем все подарки
        if 'gift_positions' in session:
            session.pop('gift_positions')
        
        if 'user_gifts_opened' in session:
            session.pop('user_gifts_opened')
        
        # Генерируем новые позиции
        get_gift_positions()
        
        return jsonify({
            'success': True,
            'message': '🎅 Дед Мороз наполнил все коробки новыми подарками!',
            'refilled_by': current_user.login if hasattr(current_user, 'login') else 'Дед Мороз'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'❌ Ошибка: {str(e)}'
        })

@lab9.route('/lab9/reset')
def reset_gifts():
    """Сброс всех подарков (для тестирования)"""
    # Сбрасываем сессию
    if 'gift_positions' in session:
        session.pop('gift_positions')
    
    if 'user_gifts_opened' in session:
        session.pop('user_gifts_opened')
    
    return redirect('/lab9/')

@lab9.route('/lab9/reset_session')
def reset_session():
    """Сброс только сессии пользователя"""
    if 'user_gifts_opened' in session:
        session.pop('user_gifts_opened')
    
    return jsonify({'success': True, 'message': 'Ваши открытия сброшены'})
@lab9.route('/lab9/logout')
@login_required
def logout():
    logout_user()
    return redirect('/lab9')

@lab9.route('/lab9/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab9/login.html')
    
    login_form = request.form.get('login')
    password_form = request.form.get('password')
    remember = request.form.get('remember') == 'on'
    
    if not login_form or login_form.strip() == '':
        return render_template('lab9/login.html',
                               error='Имя пользователя не может быть пустым')
    if not password_form or password_form.strip() == '':
        return render_template('lab9/login.html',
                               error='Пароль не может быть пустым')
    
    user = users.query.filter_by(login=login_form).first()
    
    if user:
        if check_password_hash(user.password, password_form):
            login_user(user, remember=remember)
            return redirect('/lab9/')
    
    return render_template('/lab9/login.html',
                           error='Ошибка входа: логин и/или пароль неверны')

@lab9.route('/lab9/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab9/register.html')
    
    login_form = request.form.get('login')
    password_form = request.form.get('password')
    
    if not login_form or login_form.strip() == '':
        return render_template('lab9/register.html',
                               error='Имя пользователя не может быть пустым')
    
    if not password_form or password_form.strip() == '':
        return render_template('lab9/register.html',
                               error='Пароль не может быть пустым')
    
    login_exists = users.query.filter_by(login=login_form).first()
    if login_exists:
        return render_template('lab9/register.html', 
                               error='Такой пользователь уже существует')
    
    password_hash = generate_password_hash(password_form)
    new_user = users(login=login_form, password=password_hash)
    db.session.add(new_user)
    db.session.commit()
    
    # Автоматический логин после регистрации
    login_user(new_user, remember=False)
    return redirect('/lab9/')

@lab9.route('/lab9/stats')
def get_stats():
    """Получение статистики"""
    try:
        gift_positions = get_gift_positions()
        user_opened = session.get('user_gifts_opened', [])
        
        total_gifts = len(gift_positions)
        opened_total = sum(1 for g in gift_positions if g['is_opened'])
        
        return jsonify({
            'total_gifts': total_gifts,
            'opened_total': opened_total,
            'unopened_total': total_gifts - opened_total,
            'user_opened': len(user_opened),
            'user_remaining': 3 - len(user_opened),
            'is_santa': current_user.is_authenticated,  # Упрощённо
            'user_authenticated': current_user.is_authenticated
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500