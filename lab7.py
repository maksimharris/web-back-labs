from flask import Blueprint, request, render_template, session, redirect, abort, jsonify, current_app
import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from os import path

lab7 = Blueprint('lab7', __name__)

# Функции для работы с БД
def db_connect():
    if current_app.config['DB_TYPE'] == 'postgres':
        # Используем вашу базу данных maxim_pisarev_film_base
        conn = psycopg2.connect(
            host="127.0.0.1",
            database='maxim_pisarev_film_base',
            user='maxim_pisarev_film_base',
            password='123'
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
    else:
        # SQLite для локальной разработки
        dir_path = path.dirname(path.realpath(__file__))
        db_path = path.join(dir_path, "database.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
    return conn, cur

def db_close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()

@lab7.route('/lab7/')
def main():
    return render_template('lab7/lab7.html')

def validate_film_data(film):
    """Функция для валидации данных фильма"""
    errors = {}
    current_year = datetime.datetime.now().year
    
    # Проверка русского названия
    title_ru = film.get('title_ru', '').strip()
    if not title_ru:
        errors['title_ru'] = 'Русское название обязательно'
    
    # Проверка оригинального названия
    title = film.get('title', '').strip()
    if not title and not title_ru:
        errors['title'] = 'Заполните хотя бы одно название'
    elif not title and title_ru:
        # Если оригинальное пустое, а русское есть - используем русское
        film['title'] = title_ru
    
    # Проверка года
    year = film.get('year')
    if not isinstance(year, int):
        errors['year'] = 'Год должен быть числом'
    elif year < 1895:
        errors['year'] = f'Год должен быть не ранее 1895 (год создания первого фильма)'
    elif year > current_year + 1:
        errors['year'] = f'Год должен быть не позднее {current_year + 1}'
    
    # Проверка описания
    description = film.get('description', '').strip()
    if not description:
        errors['description'] = 'Описание обязательно'
    elif len(description) > 2000:
        errors['description'] = f'Описание должно быть не более 2000 символов (сейчас {len(description)})'
    
    return errors, film

# GET всех фильмов
@lab7.route('/lab7/rest-api/films/', methods=['GET'])
def get_films():
    conn, cur = db_connect()
    
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id, title, title_ru, year, description FROM films ORDER BY id;")
    else:
        cur.execute("SELECT id, title, title_ru, year, description FROM films ORDER BY id;")
    
    films_data = cur.fetchall()
    db_close(conn, cur)
    
    # Преобразуем в список словарей для фронтенда
    films_list = []
    for film in films_data:
        films_list.append({
            'id': film['id'],
            'title': film['title'],
            'title_ru': film['title_ru'],
            'year': film['year'],
            'description': film['description']
        })
    
    return jsonify(films_list)

# GET одного фильма по ID
@lab7.route('/lab7/rest-api/films/<int:id>', methods=['GET'])
def get_film(id):
    conn, cur = db_connect()
    
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id, title, title_ru, year, description FROM films WHERE id = %s;", (id,))
    else:
        cur.execute("SELECT id, title, title_ru, year, description FROM films WHERE id = ?;", (id,))
    
    film = cur.fetchone()
    db_close(conn, cur)
    
    if not film:
        abort(404)
    
    return {
        'id': film['id'],
        'title': film['title'],
        'title_ru': film['title_ru'],
        'year': film['year'],
        'description': film['description']
    }

# DELETE фильма
@lab7.route('/lab7/rest-api/films/<int:id>', methods=['DELETE'])
def del_film(id):
    conn, cur = db_connect()
    
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("DELETE FROM films WHERE id = %s;", (id,))
    else:
        cur.execute("DELETE FROM films WHERE id = ?;", (id,))
    
    deleted = cur.rowcount > 0
    db_close(conn, cur)
    
    if not deleted:
        abort(404)
    
    return '', 204

# PUT (обновление) фильма
@lab7.route('/lab7/rest-api/films/<int:id>', methods=['PUT'])
def put_film(id):
    film = request.get_json()
    
    if not film:
        return {"error": "No data provided"}, 400
    
    # Валидация данных
    errors, validated_film = validate_film_data(film)
    if errors:
        return errors, 400
    
    conn, cur = db_connect()
    
    # Проверяем существует ли фильм
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id FROM films WHERE id = %s;", (id,))
    else:
        cur.execute("SELECT id FROM films WHERE id = ?;", (id,))
    
    if not cur.fetchone():
        db_close(conn, cur)
        abort(404)
    
    # Обновляем фильм в БД
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("""
            UPDATE films 
            SET title = %s, title_ru = %s, year = %s, description = %s 
            WHERE id = %s;
        """, (
            validated_film['title'],
            validated_film['title_ru'],
            validated_film['year'],
            validated_film['description'],
            id
        ))
    else:
        cur.execute("""
            UPDATE films 
            SET title = ?, title_ru = ?, year = ?, description = ? 
            WHERE id = ?;
        """, (
            validated_film['title'],
            validated_film['title_ru'],
            validated_film['year'],
            validated_film['description'],
            id
        ))
    
    db_close(conn, cur)
    
    # Возвращаем обновленные данные
    return {
        'id': id,
        'title': validated_film['title'],
        'title_ru': validated_film['title_ru'],
        'year': validated_film['year'],
        'description': validated_film['description']
    }

# POST (добавление) нового фильма
@lab7.route('/lab7/rest-api/films/', methods=['POST'])
@lab7.route('/lab7/rest-api/films/', methods=['POST'])
def add_film():
    film = request.get_json()
    
    if not film:
        return {"error": "No data provided"}, 400
    
    # Валидация данных
    errors, validated_film = validate_film_data(film)
    if errors:
        return errors, 400
    
    conn, cur = db_connect()
    
    try:
        # Добавляем фильм в БД БЕЗ указания id (PostgreSQL сам сгенерирует)
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("""
                INSERT INTO films (title, title_ru, year, description) 
                VALUES (%s, %s, %s, %s) 
                RETURNING id;
            """, (
                validated_film['title'],
                validated_film['title_ru'],
                validated_film['year'],
                validated_film['description']
            ))
            result = cur.fetchone()
            new_id = result['id'] if result else None
        else:
            # Для SQLite
            cur.execute("""
                INSERT INTO films (title, title_ru, year, description) 
                VALUES (?, ?, ?, ?);
            """, (
                validated_film['title'],
                validated_film['title_ru'],
                validated_film['year'],
                validated_film['description']
            ))
            new_id = cur.lastrowid
        
        db_close(conn, cur)
        
        if new_id is None:
            return {"error": "Failed to create film"}, 500
            
        return {"index": new_id}, 201
        
    except Exception as e:
        if conn:
            conn.rollback()
            cur.close()
            conn.close()
        print(f"Database error: {e}")
        return {"error": "Database error occurred"}, 500

# Функция для заполнения БД начальными данными (опционально)
def populate_initial_films():
    """Заполняет БД начальными данными о фильмах"""
    initial_films = [
        {
            "title": "The Shawshank Redemption",
            "title_ru": "Побег из Шоушенка",
            "year": 1994,
            "description": "Бухгалтер Энди Дюфрейн обвинён в убийстве собственной жены и её любовника. Оказавшись в тюрьме под названием Шоушенк, он сталкивается с жестокостью и беззаконием, царящими по обе стороны решётки. Каждый, кто попадает в эти стены, становится их рабом до конца жизни. Но Энди, обладающий живым умом и доброй душой, находит подход как к заключённым, так и к охранникам, добиваясь их особого к себе расположения."
        },
        # ... другие фильмы
    ]
    
    conn, cur = db_connect()
    
    inserted_count = 0
    for film in initial_films:
        try:
            errors, validated_film = validate_film_data(film)
            if errors:
                print(f"Ошибка валидации: {errors}")
                continue
            
            # Проверяем, нет ли уже такого фильма
            if current_app.config['DB_TYPE'] == 'postgres':
                cur.execute("SELECT id FROM films WHERE title = %s AND title_ru = %s AND year = %s;", 
                          (validated_film['title'], validated_film['title_ru'], validated_film['year']))
            else:
                cur.execute("SELECT id FROM films WHERE title = ? AND title_ru = ? AND year = ?;", 
                          (validated_film['title'], validated_film['title_ru'], validated_film['year']))
            
            if not cur.fetchone():
                # Вставка БЕЗ указания id
                if current_app.config['DB_TYPE'] == 'postgres':
                    cur.execute("""
                        INSERT INTO films (title, title_ru, year, description) 
                        VALUES (%s, %s, %s, %s)
                        RETURNING id;
                    """, (
                        validated_film['title'],
                        validated_film['title_ru'],
                        validated_film['year'],
                        validated_film['description']
                    ))
                    result = cur.fetchone()
                    print(f"Добавлен фильм с ID {result['id']}: {validated_film['title_ru']}")
                else:
                    cur.execute("""
                        INSERT INTO films (title, title_ru, year, description) 
                        VALUES (?, ?, ?, ?);
                    """, (
                        validated_film['title'],
                        validated_film['title_ru'],
                        validated_film['year'],
                        validated_film['description']
                    ))
                    print(f"Добавлен фильм: {validated_film['title_ru']}")
                
                inserted_count += 1
                
        except Exception as e:
            print(f"Ошибка при добавлении фильма {validated_film['title_ru']}: {e}")
            conn.rollback()
            continue
    
    conn.commit()
    db_close(conn, cur)
    print(f"Добавлено {inserted_count} фильмов из {len(initial_films)}")