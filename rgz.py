from flask import Blueprint, request, render_template, session, jsonify, current_app, redirect
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from os import path
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

rgz = Blueprint('rgz', __name__)

# Функции для работы с БД
def db_connect():
    if current_app.config['DB_TYPE'] == 'postgres':
        # Подключение к уже созданной базе данных
        conn = psycopg2.connect(
            host="127.0.0.1",
            database='maxim_pisarev_book_collection',  
            user='maxim_pisarev_book_collection',          
            password='123' 
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
    else:
        # Для SQLite (если DB_TYPE != 'postgres')
        dir_path = path.dirname(path.realpath(__file__))
        db_path = path.join(dir_path, "rgz_books.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
    return conn, cur

def db_close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()

# Проверка авторизации администратора
def is_admin_logged_in():
    return session.get('admin_logged_in') == True

# Проверка и создание администратора по умолчанию (если нужно)
def ensure_admin_exists():
    """Проверяет наличие администратора, если нет - создаёт"""
    try:
        conn, cur = db_connect()
        
        if current_app.config['DB_TYPE'] == 'postgres':
            # Проверяем, есть ли таблица admins
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'admins'
                );
            """)
            table_exists = cur.fetchone()['exists']
            
            if not table_exists:
                # Создаём таблицу admins
                cur.execute("""
                    CREATE TABLE admins (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password_hash VARCHAR(200) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            
            cur.execute("SELECT id FROM admins WHERE username = %s;", ('admin',))
        else:
            cur.execute("SELECT id FROM admins WHERE username = ?;", ('admin',))
        
        admin_exists = cur.fetchone()
        
        if not admin_exists:
            # Создаём администратора с паролем admin123
            password_hash = generate_password_hash('admin123')
            
            if current_app.config['DB_TYPE'] == 'postgres':
                cur.execute("INSERT INTO admins (username, password_hash) VALUES (%s, %s);", 
                          ('admin', password_hash))
            else:
                cur.execute("INSERT INTO admins (username, password_hash) VALUES (?, ?);", 
                          ('admin', password_hash))
            
            print("Создан администратор по умолчанию: admin / admin123")
        
        db_close(conn, cur)
        
    except Exception as e:
        print(f"Ошибка при проверке администратора: {e}")

# Удаляем вызов ensure_admin_exists() на уровне модуля
# Он будет вызываться внутри контекста приложения

# ============ РОУТЫ ============

@rgz.route('/rgz/')
def main():
    """Главная страница с фильтрацией книг"""
    # Вызываем здесь, когда есть контекст приложения
    ensure_admin_exists()
    return render_template('rgz/main.html', is_admin=is_admin_logged_in())

@rgz.route('/rgz/admin/login')
def admin_login_page():
    """Страница входа администратора"""
    ensure_admin_exists()
    return render_template('rgz/admin_login.html')

@rgz.route('/rgz/admin/books')
def admin_books_page():
    """Админ-панель управления книгами"""
    ensure_admin_exists()
    if not is_admin_logged_in():
        return redirect('/rgz/admin/login')
    return render_template('rgz/admin_books.html', is_admin=True)

@rgz.route('/rgz/admin/logout')
def admin_logout():
    """Выход администратора"""
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    return redirect('/rgz/')

# JSON-RPC API обработчик (упрощённая версия)
@rgz.route('/rgz/json-rpc-api/', methods=['POST'])
def json_rpc_api():
    """Основной JSON-RPC обработчик"""
    # Вызываем здесь, когда есть контекст приложения
    ensure_admin_exists()
    
    data = request.get_json()
    
    if not data:
        return jsonify({
            'jsonrpc': '2.0',
            'error': {'code': -32700, 'message': 'Parse error'},
            'id': None
        })
    
    method = data.get('method')
    params = data.get('params', {})
    request_id = data.get('id')
    
    # Методы доступные всем
    if method == 'get_books':
        return get_books_handler(params, request_id)
    elif method == 'get_filters':
        return get_filters_handler(request_id)
    elif method == 'login_admin':
        return login_admin_handler(params, request_id)
    
    # Методы только для администратора
    if not is_admin_logged_in():
        return jsonify({
            'jsonrpc': '2.0',
            'error': {'code': -32001, 'message': 'Unauthorized'},
            'id': request_id
        })
    
    if method == 'add_book':
        return add_book_handler(params, request_id)
    elif method == 'update_book':
        return update_book_handler(params, request_id)
    elif method == 'delete_book':
        return delete_book_handler(params, request_id)
    elif method == 'get_book':
        return get_book_handler(params, request_id)
    elif method == 'logout_admin':
        session.pop('admin_logged_in', None)
        return jsonify({
            'jsonrpc': '2.0',
            'result': {'success': True},
            'id': request_id
        })
    
    # Метод не найден
    return jsonify({
        'jsonrpc': '2.0',
        'error': {'code': -32601, 'message': 'Method not found'},
        'id': request_id
    })

# ============ ОБРАБОТЧИКИ МЕТОДОВ ============

def get_books_handler(params, request_id):
    """Получение книг с фильтрацией и пагинацией"""
    try:
        conn, cur = db_connect()
        
        # Параметры
        page = int(params.get('page', 1))
        per_page = 20
        offset = (page - 1) * per_page
        
        title_filter = params.get('title', '')
        author_filter = params.get('author', '')
        publisher_filter = params.get('publisher', '')
        min_pages = params.get('min_pages')
        max_pages = params.get('max_pages')
        sort_by = params.get('sort_by', 'id')
        sort_order = params.get('sort_order', 'asc')
        
        # Построение запроса
        query = "SELECT id, title, author, pages, publisher, cover_image, year, genre FROM books WHERE 1=1"
        query_params = []
        
        if title_filter:
            if current_app.config['DB_TYPE'] == 'postgres':
                query += " AND title ILIKE %s"
            else:
                query += " AND title LIKE ?"
            query_params.append(f"%{title_filter}%")
        
        if author_filter:
            if current_app.config['DB_TYPE'] == 'postgres':
                query += " AND author ILIKE %s"
            else:
                query += " AND author LIKE ?"
            query_params.append(f"%{author_filter}%")
        
        if publisher_filter:
            if current_app.config['DB_TYPE'] == 'postgres':
                query += " AND publisher ILIKE %s"
            else:
                query += " AND publisher LIKE ?"
            query_params.append(f"%{publisher_filter}%")
        
        if min_pages:
            if current_app.config['DB_TYPE'] == 'postgres':
                query += " AND pages >= %s"
            else:
                query += " AND pages >= ?"
            query_params.append(int(min_pages))
        
        if max_pages:
            if current_app.config['DB_TYPE'] == 'postgres':
                query += " AND pages <= %s"
            else:
                query += " AND pages <= ?"
            query_params.append(int(max_pages))
        
        # Сортировка
        valid_sort = ['id', 'title', 'author', 'pages', 'publisher', 'year']
        if sort_by not in valid_sort:
            sort_by = 'id'
        
        sort_order = 'ASC' if sort_order.lower() == 'asc' else 'DESC'
        query += f" ORDER BY {sort_by} {sort_order}"
        
        # Общее количество (упрощенный запрос)
        count_query = query.replace("SELECT id, title, author, pages, publisher, cover_image, year, genre", 
                                   "SELECT COUNT(*) as total")
        
        # Убираем ORDER BY и LIMIT для подсчета
        if "ORDER BY" in count_query:
            count_query = count_query.split("ORDER BY")[0]
        
        cur.execute(count_query, query_params)
        total_result = cur.fetchone()
        total = total_result['total'] if total_result else 0
        
        # Пагинация
        if current_app.config['DB_TYPE'] == 'postgres':
            query += " LIMIT %s OFFSET %s"
        else:
            query += " LIMIT ? OFFSET ?"
        query_params.extend([per_page, offset])
        
        cur.execute(query, query_params)
        books = cur.fetchall()
        
        db_close(conn, cur)
        
        # Форматирование результата
        books_list = []
        for book in books:
            books_list.append({
                'id': book['id'],
                'title': book['title'],
                'author': book['author'],
                'pages': book['pages'],
                'publisher': book['publisher'],
                'cover_image': book['cover_image'] or 'https://via.placeholder.com/150x200?text=No+Cover',
                'year': book['year'],
                'genre': book['genre']
            })
        
        return jsonify({
            'jsonrpc': '2.0',
            'result': {
                'books': books_list,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page if total > 0 else 0
            },
            'id': request_id
        })
        
    except Exception as e:
        print(f"Error in get_books: {e}")
        return jsonify({
            'jsonrpc': '2.0',
            'error': {'code': -32000, 'message': str(e)},
            'id': request_id
        })

def get_filters_handler(request_id):
    """Получение фильтров"""
    try:
        conn, cur = db_connect()
        
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT DISTINCT publisher FROM books ORDER BY publisher;")
            publishers = [p['publisher'] for p in cur.fetchall()]
            
            cur.execute("SELECT MIN(pages) as min, MAX(pages) as max FROM books;")
            pages_range = cur.fetchone()
        else:
            cur.execute("SELECT DISTINCT publisher FROM books ORDER BY publisher;")
            publishers = [p['publisher'] for p in cur.fetchall()]
            
            cur.execute("SELECT MIN(pages) as min, MAX(pages) as max FROM books;")
            pages_range = cur.fetchone()
        
        db_close(conn, cur)
        
        return jsonify({
            'jsonrpc': '2.0',
            'result': {
                'publishers': publishers,
                'min_pages': pages_range['min'] if pages_range and pages_range['min'] else 0,
                'max_pages': pages_range['max'] if pages_range and pages_range['max'] else 1000
            },
            'id': request_id
        })
        
    except Exception as e:
        print(f"Error in get_filters: {e}")
        return jsonify({
            'jsonrpc': '2.0',
            'result': {'publishers': [], 'min_pages': 0, 'max_pages': 1000},
            'id': request_id
        })

def login_admin_handler(params, request_id):
    """Авторизация администратора"""
    username = params.get('username')
    password = params.get('password')
    
    print(f"Попытка входа: username='{username}', password='{password}'")  # ДЕБАГ
    
    if not username or not password:
        return jsonify({
            'jsonrpc': '2.0',
            'error': {'code': -32602, 'message': 'Invalid params'},
            'id': request_id
        })
    
    try:
        conn, cur = db_connect()
        
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT id, password_hash FROM admins WHERE username = %s;", (username,))
        else:
            cur.execute("SELECT id, password_hash FROM admins WHERE username = ?;", (username,))
        
        admin = cur.fetchone()
        db_close(conn, cur)
        
        print(f"Найден администратор: {admin}")  # ДЕБАГ
        
        if not admin:
            print(f"Администратор '{username}' не найден в базе данных")  # ДЕБАГ
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': -32003, 'message': 'Invalid credentials'},
                'id': request_id
            })
        
        print(f"Хэш из БД: {admin['password_hash']}")  # ДЕБАГ
        
        # Сгенерируем хэш для введенного пароля для сравнения
        from werkzeug.security import generate_password_hash
        test_hash = generate_password_hash(password)
        print(f"Хэш для введенного пароля: {test_hash}")  # ДЕБАГ
        
        if check_password_hash(admin['password_hash'], password):
            print("Пароль верный! Устанавливаем сессию...")  # ДЕБАГ
            session['admin_logged_in'] = True
            session['admin_username'] = username
            return jsonify({
                'jsonrpc': '2.0',
                'result': {'success': True},
                'id': request_id
            })
        else:
            print("Пароль неверный!")  # ДЕБАГ
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': -32003, 'message': 'Invalid credentials'},
                'id': request_id
            })
            
    except Exception as e:
        print(f"Error in login_admin: {e}")  # ДЕБАГ
        import traceback
        traceback.print_exc()  # ДЕБАГ - полный стек ошибки
        return jsonify({
            'jsonrpc': '2.0',
            'error': {'code': -32000, 'message': 'Server error'},
            'id': request_id
        })

def add_book_handler(params, request_id):
    """Добавление книги"""
    try:
        # Валидация
        required = ['title', 'author', 'pages', 'publisher']
        for field in required:
            if not params.get(field):
                return jsonify({
                    'jsonrpc': '2.0',
                    'error': {'code': -32602, 'message': f'Missing {field}'},
                    'id': request_id
                })
        
        conn, cur = db_connect()
        
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("""
                INSERT INTO books (title, author, pages, publisher, cover_image, description, year, genre)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (
                params['title'],
                params['author'],
                int(params['pages']),
                params['publisher'],
                params.get('cover_image'),
                params.get('description'),
                params.get('year'),
                params.get('genre')
            ))
            book_id = cur.fetchone()['id']
        else:
            cur.execute("""
                INSERT INTO books (title, author, pages, publisher, cover_image, description, year, genre)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                params['title'],
                params['author'],
                int(params['pages']),
                params['publisher'],
                params.get('cover_image'),
                params.get('description'),
                params.get('year'),
                params.get('genre')
            ))
            book_id = cur.lastrowid
        
        db_close(conn, cur)
        
        return jsonify({
            'jsonrpc': '2.0',
            'result': {'id': book_id, 'success': True},
            'id': request_id
        })
        
    except Exception as e:
        print(f"Error in add_book: {e}")
        return jsonify({
            'jsonrpc': '2.0',
            'error': {'code': -32000, 'message': str(e)},
            'id': request_id
        })

def update_book_handler(params, request_id):
    """Обновление книги"""
    try:
        book_id = params.get('id')
        if not book_id:
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': -32602, 'message': 'Missing ID'},
                'id': request_id
            })
        
        conn, cur = db_connect()
        
        # Проверка существования
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT id FROM books WHERE id = %s;", (book_id,))
        else:
            cur.execute("SELECT id FROM books WHERE id = ?;", (book_id,))
        
        if not cur.fetchone():
            db_close(conn, cur)
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': -32004, 'message': 'Book not found'},
                'id': request_id
            })
        
        # Обновление
        fields = []
        values = []
        
        field_mappings = {
            'title': 'title',
            'author': 'author',
            'pages': 'pages',
            'publisher': 'publisher',
            'cover_image': 'cover_image',
            'description': 'description',
            'year': 'year',
            'genre': 'genre'
        }
        
        for param_name, db_field in field_mappings.items():
            if param_name in params and params[param_name] is not None:
                fields.append(f"{db_field} = ?" if current_app.config['DB_TYPE'] != 'sqlite3' else f"{db_field} = %s")
                values.append(params[param_name])
        
        if fields:
            values.append(book_id)
            query = f"UPDATE books SET {', '.join(fields)} WHERE id = ?"
            if current_app.config['DB_TYPE'] == 'postgres':
                query = query.replace('?', '%s')
            
            cur.execute(query, values)
        
        db_close(conn, cur)
        
        return jsonify({
            'jsonrpc': '2.0',
            'result': {'success': True},
            'id': request_id
        })
        
    except Exception as e:
        print(f"Error in update_book: {e}")
        return jsonify({
            'jsonrpc': '2.0',
            'error': {'code': -32000, 'message': str(e)},
            'id': request_id
        })

def delete_book_handler(params, request_id):
    """Удаление книги"""
    try:
        book_id = params.get('id')
        if not book_id:
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': -32602, 'message': 'Missing ID'},
                'id': request_id
            })
        
        conn, cur = db_connect()
        
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("DELETE FROM books WHERE id = %s;", (book_id,))
        else:
            cur.execute("DELETE FROM books WHERE id = ?;", (book_id,))
        
        deleted = cur.rowcount > 0
        db_close(conn, cur)
        
        if not deleted:
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': -32004, 'message': 'Book not found'},
                'id': request_id
            })
        
        return jsonify({
            'jsonrpc': '2.0',
            'result': {'success': True},
            'id': request_id
        })
        
    except Exception as e:
        print(f"Error in delete_book: {e}")
        return jsonify({
            'jsonrpc': '2.0',
            'error': {'code': -32000, 'message': str(e)},
            'id': request_id
        })

def get_book_handler(params, request_id):
    """Получение одной книги"""
    try:
        book_id = params.get('id')
        if not book_id:
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': -32602, 'message': 'Missing ID'},
                'id': request_id
            })
        
        conn, cur = db_connect()
        
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT * FROM books WHERE id = %s;", (book_id,))
        else:
            cur.execute("SELECT * FROM books WHERE id = ?;", (book_id,))
        
        book = cur.fetchone()
        db_close(conn, cur)
        
        if not book:
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': -32004, 'message': 'Book not found'},
                'id': request_id
            })
        
        # Преобразуем в словарь
        book_dict = dict(book)
        
        return jsonify({
            'jsonrpc': '2.0',
            'result': book_dict,
            'id': request_id
        })
        
    except Exception as e:
        print(f"Error in get_book: {e}")
        return jsonify({
            'jsonrpc': '2.0',
            'error': {'code': -32000, 'message': str(e)},
            'id': request_id
        })

# ============ УТИЛИТЫ ============

@rgz.route('/rgz/init-demo')
def init_demo_books():
    """Добавление демо-книг (100+ штук)"""
    if not is_admin_logged_in():
        return "Требуется авторизация"
    
    # Вызываем ensure_admin_exists() перед работой с БД
    ensure_admin_exists()
    
    books = [
        {"title": "Вишнёвый сад", "author": "Антон Чехов", "pages": 128, "publisher": "Знание", "year": 1904, "genre": "Пьеса","cover_image":"rgz/vish.jpg"},
        {"title": "Процесс", "author": "Франц Кафка", "pages": 256, "publisher": "Kurt Wolff Verlag", "year": 1925, "genre": "Роман","cover_image":"rgz/proc.webp"},
        {"title": "Скотный двор", "author": "Джордж Оруэлл", "pages": 112, "publisher": "Secker & Warburg", "year": 1945, "genre": "Сатира","cover_image":"rgz/orig.webp"},
        {"title": "Хоббит", "author": "Дж. Р. Р. Толкин", "pages": 310, "publisher": "Allen & Unwin", "year": 1937, "genre": "Фэнтези","cover_image":"i (8).webp"},
        {"title": "Война и мир", "author": "Лев Толстой", "pages": 1225, "publisher": "Эксмо", "year": 1869, "genre": "Роман","cover_image":"rgz/orig (1).webp"},
        {"title": "Преступление и наказание", "author": "Фёдор Достоевский", "pages": 671, "publisher": "Азбука", "year": 1866, "genre": "Роман","cover_image":"rgz/i (9).webp"},
        {"title": "Мастер и Маргарита", "author": "Михаил Булгаков", "pages": 480, "publisher": "АСТ", "year": 1967, "genre": "Роман","cover_image":"rgz/orig (2).webp"},
        {"title": "Анна Каренина", "author": "Лев Толстой", "pages": 864, "publisher": "Эксмо", "year": 1877, "genre": "Роман","cover_image":"rgz/orig (3).webp"},
        {"title": "Братья Карамазовы", "author": "Фёдор Достоевский", "pages": 824, "publisher": "Азбука", "year": 1880, "genre": "Роман","cover_image":"rgz/i (10).webp"},
        {"title": "Евгений Онегин", "author": "Александр Пушкин", "pages": 320, "publisher": "АСТ", "year": 1833, "genre": "Поэма","cover_image":"rgz/orig (4).webp"},
        {"title": "Отцы и дети", "author": "Иван Тургенев", "pages": 288, "publisher": "Эксмо", "year": 1862, "genre": "Роман","cover_image":"rgz/i (11).webp"},
        {"title": "Доктор Живаго", "author": "Борис Пастернак", "pages": 592, "publisher": "Азбука", "year": 1957, "genre": "Роман","cover_image":"rgz/i (12).webp"},
        {"title": "Тихий Дон", "author": "Михаил Шолохов", "pages": 1504, "publisher": "АСТ", "year": 1940, "genre": "Роман","cover_image":"rgz/i (13).webp"},
        {"title": "Мёртвые души", "author": "Николай Гоголь", "pages": 352, "publisher": "Эксмо", "year": 1842, "genre": "Поэма","cover_image":"rgz/i (14).webp"},
        {"title": "1984", "author": "Джордж Оруэлл", "pages": 328, "publisher": "Penguin", "year": 1949, "genre": "Антиутопия","cover_image":"rgz/i (15).webp"},
        {"title": "Гордость и предубеждение", "author": "Джейн Остин", "pages": 432, "publisher": "Macmillan", "year": 1813, "genre": "Роман","cover_image":"rgz/i (16).webp"},
        {"title": "Улисс", "author": "Джеймс Джойс", "pages": 730, "publisher": "Penguin", "year": 1922, "genre": "Модернизм","cover_image":"rgz/46e34f4a09ea6850.jpg"},
        {"title": "Великий Гэтсби", "author": "Фрэнсис Фицджеральд", "pages": 218, "publisher": "Scribner", "year": 1925, "genre": "Роман","cover_image":"rgz/orig (5).webp"},
        {"title": "Над пропастью во ржи", "author": "Джером Сэлинджер", "pages": 234, "publisher": "Little, Brown", "year": 1951, "genre": "Роман","cover_image":"rgz/i (17).webp"},
        {"title": "Гарри Поттер и философский камень", "author": "Дж. К. Роулинг", "pages": 320, "publisher": "Bloomsbury", "year": 1997, "genre": "Фэнтези","cover_image":"rgz/orig (6).webp"},
        {"title": "Властелин колец", "author": "Дж. Р. Р. Толкин", "pages": 1178, "publisher": "Allen & Unwin", "year": 1954, "genre": "Фэнтези","cover_image":"rgz/i (18).webp"},
        {"title": "Маленький принц", "author": "Антуан де Сент-Экзюпери", "pages": 96, "publisher": "Gallimard", "year": 1943, "genre": "Философия","cover_image":"rgz/i (19).webp"},
        {"title": "Алиса в Стране чудес", "author": "Льюис Кэрролл", "pages": 200, "publisher": "Macmillan", "year": 1865, "genre": "Сказка","cover_image":"rgz/orig (7).webp"},
        {"title": "Моби Дик", "author": "Герман Мелвилл", "pages": 635, "publisher": "Harper & Brothers", "year": 1851, "genre": "Роман","cover_image":"rgz/i (20).webp"},
        {"title": "Убийство в Восточном экспрессе", "author": "Агата Кристи", "pages": 256, "publisher": "Collins Crime Club", "year": 1934, "genre": "Детектив","cover_image":"rgz/7043067861.jpg"},
        {"title": "Шерлок Холмс: Сборник рассказов", "author": "Артур Конан Дойл", "pages": 480, "publisher": "George Newnes", "year": 1892, "genre": "Детектив","cover_image":"rgz/i (21).webp"},
        {"title": "Десять негритят", "author": "Агата Кристи", "pages": 272, "publisher": "Collins Crime Club", "year": 1939, "genre": "Детектив","cover_image":"rgz/i (22).webp"},
        {"title": "Молчание ягнят", "author": "Томас Харрис", "pages": 338, "publisher": "St. Martin's Press", "year": 1988, "genre": "Триллер","cover_image":"rgz/i (23).webp"},
        {"title": "Код да Винчи", "author": "Дэн Браун", "pages": 454, "publisher": "Doubleday", "year": 2003, "genre": "Детектив","cover_image":"rgz/i (24).webp"},
        {"title": "Игра престолов", "author": "Джордж Мартин", "pages": 694, "publisher": "Bantam Spectra", "year": 1996, "genre": "Фэнтези","cover_image":"rgz/i (25).webp"},
        {"title": "Девушка с татуировкой дракона", "author": "Стиг Ларссон", "pages": 465, "publisher": "Norstedts", "year": 2005, "genre": "Детектив","cover_image":"rgz/orig (8).webp"},
        {"title": "Оно", "author": "Стивен Кинг", "pages": 1138, "publisher": "Viking", "year": 1986, "genre": "Ужасы","cover_image":"rgz/i (26).webp"},
        {"title": "Сияние", "author": "Стивен Кинг", "pages": 447, "publisher": "Doubleday", "year": 1977, "genre": "Ужасы","cover_image":"rgz/i (27).webp"},
        {"title": "Дюна", "author": "Фрэнк Герберт", "pages": 412, "publisher": "Chilton Books", "year": 1965, "genre": "Фантастика","cover_image":"rgz/i (28).webp"},
        {"title": "Основание", "author": "Айзек Азимов", "pages": 255, "publisher": "Gnome Press", "year": 1951, "genre": "Фантастика","cover_image":"rgz/7044921995.jpg"},
        {"title": "Солярис", "author": "Станислав Лем", "pages": 204, "publisher": "Wydawnictwo Literackie", "year": 1961, "genre": "Фантастика","cover_image":"rgz/6589069784.jpg"},
        {"title": "О дивный новый мир", "author": "Олдос Хаксли", "pages": 268, "publisher": "Chatto & Windus", "year": 1932, "genre": "Антиутопия","cover_image":"rgz/7278712806.jpg"},
        {"title": "451° по Фаренгейту", "author": "Рэй Брэдбери", "pages": 158, "publisher": "Ballantine", "year": 1953, "genre": "Антиутопия","cover_image":"rgz/6728802857.jpg"},
        {"title": "Мечтают ли андроиды об электроовцах?", "author": "Филип К. Дик", "pages": 210, "publisher": "Doubleday", "year": 1968, "genre": "Фантастика","cover_image":"rgz/1.webp"},
        {"title": "Гиперион", "author": "Дэн Симмонс", "pages": 482, "publisher": "Doubleday", "year": 1989, "genre": "Фантастика","cover_image":"rgz/74b60ddcfd3fdf1b42c4cfe3b8e0fda3.jpg"},
        {"title": "Пикник на обочине", "author": "Аркадий и Борис Стругацкие", "pages": 224, "publisher": "Молодая гвардия", "year": 1972, "genre": "Фантастика","cover_image":"rgz/1008862422.jpg"},
        {"title": "Марсианские хроники", "author": "Рэй Брэдбери", "pages": 222, "publisher": "Doubleday", "year": 1950, "genre": "Фантастика","cover_image":"rgz/i (29).webp"},
        {"title": "Нейромант", "author": "Уильям Гибсон", "pages": 271, "publisher": "Ace", "year": 1984, "genre": "Киберпанк","cover_image":"rgz/orig (9).webp"},
        {"title": "Три товарища", "author": "Эрих Мария Ремарк", "pages": 448, "publisher": "Kiepenheuer & Witsch", "year": 1936, "genre": "Роман","cover_image":"rgz/i (30).webp"},
        {"title": "Сто лет одиночества", "author": "Габриэль Гарсиа Маркес", "pages": 417, "publisher": "Editorial Sudamericana", "year": 1967, "genre": "Магический реализм","cover_image":"rgz/i (31).webp"},
        {"title": "Портрет Дориана Грея", "author": "Оскар Уайльд", "pages": 254, "publisher": "Lippincott's", "year": 1890, "genre": "Роман","cover_image":"rgz/orig (10).webp"},
        {"title": "Лолита", "author": "Владимир Набоков", "pages": 336, "publisher": "Olympia Press", "year": 1955, "genre": "Роман","cover_image":"rgz/63815173013534.jpg"},
        {"title": "На западном фронте без перемен", "author": "Эрих Мария Ремарк", "pages": 296, "publisher": "Propyläen Verlag", "year": 1929, "genre": "Роман","cover_image":"rgz/i (32).webp"},
        {"title": "Старик и море", "author": "Эрнест Хемингуэй", "pages": 127, "publisher": "Scribner", "year": 1952, "genre": "Повесть","cover_image":"rgz/6862252466.jpg"},
        {"title": "Унесённые ветром", "author": "Маргарет Митчелл", "pages": 1037, "publisher": "Macmillan", "year": 1936, "genre": "Роман","cover_image":"rgz/orig (11).webp"},
        {"title": "Атлант расправил плечи", "author": "Айн Рэнд", "pages": 1168, "publisher": "Random House", "year": 1957, "genre": "Философия","cover_image":"rgz/126327.jpg"},
        {"title": "Фауст", "author": "Иоганн Вольфганг Гёте", "pages": 480, "publisher": "Cotta", "year": 1808, "genre": "Трагедия","cover_image":"rgz/orig (12).webp"},
        {"title": "Грозовой перевал", "author": "Эмили Бронте", "pages": 342, "publisher": "Thomas Cautley Newby", "year": 1847, "genre": "Роман","cover_image":"rgz/orig (13).webp"},
        {"title": "Джейн Эйр", "author": "Шарлотта Бронте", "pages": 500, "publisher": "Smith, Elder & Co.", "year": 1847, "genre": "Роман","cover_image":"rgz/i (33).webp"},
        {"title": "Робинзон Крузо", "author": "Даниель Дефо", "pages": 320, "publisher": "W. Taylor", "year": 1719, "genre": "Приключения","cover_image":"rgz/0f4729135ff7de9ef87f6d603c3c408b.jpg"},
        {"title": "Путешествия Гулливера", "author": "Джонатан Свифт", "pages": 240, "publisher": "Benjamin Motte", "year": 1726, "genre": "Сатира","cover_image":"rgz/1 (1).webp"},
        {"title": "Дон Кихот", "author": "Мигель де Сервантес", "pages": 863, "publisher": "Francisco de Robles", "year": 1605, "genre": "Роман","cover_image":"rgz/i (34).webp"},
        {"title": "Божественная комедия", "author": "Данте Алигьери", "pages": 798, "publisher": "Various", "year": 1320, "genre": "Поэма","cover_image":"rgz/orig (14).webp"},
        {"title": "Илиада", "author": "Гомер", "pages": 560, "publisher": "Various", "year": -750, "genre": "Поэма","cover_image":"rgz/i (35).webp"},
        {"title": "Одиссея", "author": "Гомер", "pages": 541, "publisher": "Various", "year": -720, "genre": "Поэма","cover_image":"rgz/64189039869982.jpg"},
        {"title": "Гамлет", "author": "Уильям Шекспир", "pages": 342, "publisher": "Various", "year": 1603, "genre": "Трагедия","cover_image":"rgz/i (36).webp"},
        {"title": "Ромео и Джульетта", "author": "Уильям Шекспир", "pages": 283, "publisher": "Various", "year": 1597, "genre": "Трагедия","cover_image":"rgz/orig (15).webp"},
        {"title": "Макбет", "author": "Уильям Шекспир", "pages": 249, "publisher": "Various", "year": 1606, "genre": "Трагедия","cover_image":"rgz/i (37).webp"},
        {"title": "Король Лир", "author": "Уильям Шекспир", "pages": 310, "publisher": "Various", "year": 1608, "genre": "Трагедия","cover_image":"rgz/1020911703.jpg"},
        {"title": "Отелло", "author": "Уильям Шекспир", "pages": 314, "publisher": "Various", "year": 1604, "genre": "Трагедия","cover_image":"rgz/i (38).webp"},
        {"title": "Сон в летнюю ночь", "author": "Уильям Шекспир", "pages": 156, "publisher": "Various", "year": 1600, "genre": "Комедия","cover_image":"rgz/orig (16).webp"},
        {"title": "Венецианский купец", "author": "Уильям Шекспир", "pages": 212, "publisher": "Various", "year": 1600, "genre": "Комедия","cover_image":"rgz/100026624046b0.webp"},
        {"title": "Буря", "author": "Уильям Шекспир", "pages": 187, "publisher": "Various", "year": 1611, "genre": "Комедия","cover_image":"rgz/776a4014ec7d231aea42e7b4ae600f16.jpg"},
        {"title": "Двенадцатая ночь", "author": "Уильям Шекспир", "pages": 204, "publisher": "Various", "year": 1602, "genre": "Комедия","cover_image":"rgz/1 (2).webp"},
        {"title": "Генрих V", "author": "Уильям Шекспир", "pages": 276, "publisher": "Various", "year": 1599, "genre": "Историческая драма","cover_image":"rgz/d992ef9249eb219da682b8883ba86cee.jpg"},
        {"title": "Ричард III", "author": "Уильям Шекспир", "pages": 298, "publisher": "Various", "year": 1597, "genre": "Историческая драма","cover_image":"rgz/6900960916.jpg"},
        {"title": "Юлий Цезарь", "author": "Уильям Шекспир", "pages": 210, "publisher": "Various", "year": 1599, "genre": "Трагедия","cover_image":"rgz/orig (17).webp"},
        {"title": "Антоний и Клеопатра", "author": "Уильям Шекспир", "pages": 268, "publisher": "Various", "year": 1607, "genre": "Трагедия","cover_image":"rgz/6025761971.jpg"},
        {"title": "Троил и Крессида", "author": "Уильям Шекспир", "pages": 224, "publisher": "Various", "year": 1602, "genre": "Трагедия","cover_image":"rgz/i (39).webp"},
        {"title": "Тит Андроник", "author": "Уильям Шекспир", "pages": 192, "publisher": "Various", "year": 1594, "genre": "Трагедия","cover_image":"rgz/7479195728.jpg"},
        {"title": "Мера за меру", "author": "Уильям Шекспир", "pages": 188, "publisher": "Various", "year": 1604, "genre": "Комедия","cover_image":"rgz/i (40).webp"},
        {"title": "Виндзорские насмешницы", "author": "Уильям Шекспир", "pages": 156, "publisher": "Various", "year": 1602, "genre": "Комедия","cover_image":"rgz/RGUB-BIBL-0000263197-large.jpg"},
        {"title": "Укрощение строптивой", "author": "Уильям Шекспир", "pages": 178, "publisher": "Various", "year": 1594, "genre": "Комедия","cover_image":"rgz/6918975451.jpg"},
        {"title": "Много шума из ничего", "author": "Уильям Шекспир", "pages": 198, "publisher": "Various", "year": 1600, "genre": "Комедия","cover_image":"rgz/700.jpg"},
        {"title": "Как вам это понравится", "author": "Уильям Шекспир", "pages": 204, "publisher": "Various", "year": 1600, "genre": "Комедия","cover_image":"rgz/7327859070.jpg"},
        {"title": "Всё хорошо, что хорошо кончается", "author": "Уильям Шекспир", "pages": 192, "publisher": "Various", "year": 1605, "genre": "Комедия","cover_image":"rgz/6040114905.jpg"},
        {"title": "Перикл", "author": "Уильям Шекспир", "pages": 176, "publisher": "Various", "year": 1609, "genre": "Трагедия","cover_image":"rgz/7814bf0a-1cd5-4d73-9c7f-3d0da87196ba.jpg"},
        {"title": "Зимняя сказка", "author": "Уильям Шекспир", "pages": 198, "publisher": "Various", "year": 1611, "genre": "Комедия","cover_image":"rgz/6025761859.jpg"},
        {"title": "Цимбелин", "author": "Уильям Шекспир", "pages": 212, "publisher": "Various", "year": 1611, "genre": "Трагедия","cover_image":"rgz/i (41).webp"},
        {"title": "Генрих IV, часть 1", "author": "Уильям Шекспир", "pages": 256, "publisher": "Various", "year": 1597, "genre": "Историческая драма","cover_image":"rgz/7133251634.jpg"},
        {"title": "Генрих IV, часть 2", "author": "Уильям Шекспир", "pages": 248, "publisher": "Various", "year": 1600, "genre": "Историческая драма","cover_image":"rgz/018ede48-ea64-73f2-902c-4b2b4fae5afb.webp"},
        {"title": "Генрих VI, часть 1", "author": "Уильям Шекспир", "pages": 232, "publisher": "Various", "year": 1591, "genre": "Историческая драма","cover_image":"rgz/81LB6wfJmsL.jpg"},
        {"title": "Генрих VI, часть 2", "author": "Уильям Шекспир", "pages": 244, "publisher": "Various", "year": 1591, "genre": "Историческая драма","cover_image":"rgz/s-l640.jpg"},
        {"title": "Генрих VI, часть 3", "author": "Уильям Шекспир", "pages": 238, "publisher": "Various", "year": 1591, "genre": "Историческая драма","cover_image":"rgz/orig (18).webp"},
        {"title": "Генрих VIII", "author": "Уильям Шекспир", "pages": 220, "publisher": "Various", "year": 1613, "genre": "Историческая драма","cover_image":"rgz/6895625593.jpg"},
        {"title": "Эдуард III", "author": "Уильям Шекспир", "pages": 168, "publisher": "Various", "year": 1596, "genre": "Историческая драма","cover_image":"rgz/i (42).webp"},
        {"title": "Томас Мор и его утопия", "author": "Карл Каутский", "pages": 152, "publisher": "Various", "year": 1905, "genre": "Историческая драма","cover_image":"rgz/713134-tomas-mor-i-ego-utopiya.webp"},
        {"title": "Два знатных родича", "author": "Уильям Шекспир", "pages": 164, "publisher": "Various", "year": 1634, "genre": "Трагедия","cover_image":"rgz/books-9780199537457.jpg"},
        {"title": "Кармен", "author": "Проспер Мериме", "pages": 128, "publisher": "Various", "year": 1845, "genre": "Новелла","cover_image":"rgz/1022889283.jpg"},
        {"title": "Граф Монте-Кристо", "author": "Александр Дюма", "pages": 1276, "publisher": "Various", "year": 1844, "genre": "Приключения","cover_image":"rgz/6008887473.jpg"},
        {"title": "Три мушкетёра", "author": "Александр Дюма", "pages": 704, "publisher": "Various", "year": 1844, "genre": "Приключения","cover_image":"rgz/orig (19).webp"},
        {"title": "Двадцать лет спустя", "author": "Александр Дюма", "pages": 768, "publisher": "Various", "year": 1845, "genre": "Приключения","cover_image":"rgz/100049168523b0.webp"},
        {"title": "Виконт де Бражелон", "author": "Александр Дюма", "pages": 2600, "publisher": "Various", "year": 1850, "genre": "Приключения","cover_image":"rgz/1 (3).webp"},
        {"title": "Королева Марго", "author": "Александр Дюма", "pages": 672, "publisher": "Various", "year": 1845, "genre": "Исторический роман","cover_image":"rgz/6659850391.jpg"},
        {"title": "Блич", "author": "Тайто Кубо", "pages": 710, "publisher": "Weekly Shonen Jump", "year": 2001, "genre": "Фантастика","cover_image":"rgz/809b134db16437a074a7064c0ba4126e.jpg"},
    ]
    
    conn, cur = db_connect()
    
    try:
        added = 0
        for book in books:
            try:
                # Проверяем, существует ли уже книга
                if current_app.config['DB_TYPE'] == 'postgres':
                    cur.execute("SELECT id FROM books WHERE title = %s AND author = %s;", 
                               (book['title'], book['author']))
                else:
                    cur.execute("SELECT id FROM books WHERE title = ? AND author = ?;", 
                               (book['title'], book['author']))
                
                if not cur.fetchone():
                    if current_app.config['DB_TYPE'] == 'postgres':
                        cur.execute("""
                            INSERT INTO books (title, author, pages, publisher, year, genre, cover_image)
                            VALUES (%s, %s, %s, %s, %s, %s, %s);
                        """, (
                            book['title'],
                            book['author'],
                            book['pages'],
                            book['publisher'],
                            book['year'],
                            book['genre'],
                            book.get('cover_image', '')
                        ))
                    else:
                        cur.execute("""
                            INSERT INTO books (title, author, pages, publisher, year, genre, cover_image)
                            VALUES (?, ?, ?, ?, ?, ?, ?);
                        """, (
                            book['title'],
                            book['author'],
                            book['pages'],
                            book['publisher'],
                            book['year'],
                            book['genre'],
                            book.get('cover_image', '')
                        ))
                    added += 1
            except Exception as e:
                print(f"Ошибка добавления {book['title']}: {e}")
        
        conn.commit()
        return f"Добавлено {added} книг"
        
    except Exception as e:
        conn.rollback()
        return f"Ошибка: {str(e)}"
    finally:
        cur.close()
        conn.close()

@rgz.route('/rgz/check')
def check_database():
    """Проверка подключения к БД"""
    try:
        # Вызываем ensure_admin_exists() для создания таблиц если нужно
        ensure_admin_exists()
        
        conn, cur = db_connect()
        
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT COUNT(*) as count FROM books;")
        else:
            cur.execute("SELECT COUNT(*) as count FROM books;")
        
        books_count = cur.fetchone()['count']
        
        cur.close()
        conn.close()
        
        return jsonify({
            'status': 'ok',
            'db_type': current_app.config['DB_TYPE'],
            'books_count': books_count,
            'admin_logged_in': is_admin_logged_in()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'db_type': current_app.config['DB_TYPE']
        })