from flask import Blueprint, render_template, request, redirect, session, flash
from db import db
from db.models import users, articles
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_

lab8 = Blueprint('lab8', __name__)

@lab8.route('/lab8/')
def main():
    return render_template('/lab8/lab8.html')

@lab8.route('/lab8/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab8/login.html')
    
    login_form = request.form.get('login')
    password_form = request.form.get('password')
    remember = request.form.get('remember') == 'on'
    
    if not login_form or login_form.strip() == '':
        return render_template('lab8/login.html',
                               error='Имя пользователя не может быть пустым')
    if not password_form or password_form.strip() == '':
        return render_template('lab8/login.html',
                               error='Пароль не может быть пустым')
    
    user = users.query.filter_by(login=login_form).first()
    
    if user:
        if check_password_hash(user.password, password_form):
            login_user(user, remember=remember)
            return redirect('/lab8/')
    
    return render_template('/lab8/login.html',
                           error='Ошибка входа: логин и/или пароль неверны')

@lab8.route('/lab8/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab8/register.html')
    
    login_form = request.form.get('login')
    password_form = request.form.get('password')
    
    if not login_form or login_form.strip() == '':
        return render_template('lab8/register.html',
                               error='Имя пользователя не может быть пустым')
    
    if not password_form or password_form.strip() == '':
        return render_template('lab8/register.html',
                               error='Пароль не может быть пустым')
    
    login_exists = users.query.filter_by(login=login_form).first()
    if login_exists:
        return render_template('lab8/register.html', 
                               error='Такой пользователь уже существует')
    
    password_hash = generate_password_hash(password_form)
    new_user = users(login=login_form, password=password_hash)
    db.session.add(new_user)
    db.session.commit()
    
    # Автоматический логин после регистрации
    login_user(new_user, remember=False)
    return redirect('/lab8/')

@lab8.route('/lab8/logout')
@login_required
def logout():
    logout_user()
    return redirect('/lab8')

@lab8.route('/lab8/articles')
def articles_list():
    # Показываем публичные статьи всем, а свои - только авторизованным
    public_articles = articles.query.filter_by(is_public=True).all()
    
    if current_user.is_authenticated:
        user_articles = articles.query.filter_by(login_id=current_user.id).all()
        all_articles = list(set(public_articles + user_articles))
    else:
        all_articles = public_articles
    
    return render_template('lab8/articles.html', articles=all_articles)

@lab8.route('/lab8/create', methods=['GET', 'POST'])
@login_required
def create_article():
    if request.method == 'GET':
        return render_template('lab8/create.html')
    
    title = request.form.get('title')
    article_text = request.form.get('article_text')
    is_favorite = request.form.get('is_favorite') == 'on'
    is_public = request.form.get('is_public') == 'on'
    
    if not title or not article_text:
        return render_template('lab8/create.html', 
                               error='Заголовок и текст статьи не могут быть пустыми')
    
    new_article = articles(
        login_id=current_user.id,
        title=title,
        article_text=article_text,
        is_favorite=is_favorite,
        is_public=is_public,
        likes=0
    )
    
    db.session.add(new_article)
    db.session.commit()
    
    return redirect('/lab8/articles')

@lab8.route('/lab8/edit/<int:article_id>', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    article = articles.query.filter_by(id=article_id, login_id=current_user.id).first()
    
    if not article:
        return "Статья не найдена или у вас нет прав на её редактирование", 404
    
    if request.method == 'GET':
        return render_template('lab8/edit.html', article=article)
    
    title = request.form.get('title')
    article_text = request.form.get('article_text')
    is_favorite = request.form.get('is_favorite') == 'on'
    is_public = request.form.get('is_public') == 'on'
    
    if not title or not article_text:
        return render_template('lab8/edit.html', 
                               article=article,
                               error='Заголовок и текст статьи не могут быть пустыми')
    
    article.title = title
    article.article_text = article_text
    article.is_favorite = is_favorite
    article.is_public = is_public
    
    db.session.commit()
    return redirect('/lab8/articles')

@lab8.route('/lab8/delete/<int:article_id>')
@login_required
def delete_article(article_id):
    article = articles.query.filter_by(id=article_id, login_id=current_user.id).first()
    
    if article:
        db.session.delete(article)
        db.session.commit()
    
    return redirect('/lab8/articles')

@lab8.route('/lab8/search')
def search_articles():
    query = request.args.get('q', '')
    
    if not query:
        return redirect('/lab8/articles')
    
    # Регистронезависимый поиск
    search_pattern = f"%{query}%"
    
    # Ищем в заголовке и тексте статьи
    found_articles = articles.query.filter(
        or_(
            articles.title.ilike(search_pattern),
            articles.article_text.ilike(search_pattern)
        ),
        or_(
            articles.is_public == True,
            articles.login_id == current_user.id if current_user.is_authenticated else False
        )
    ).all()
    
    return render_template('lab8/articles.html', 
                           articles=found_articles, 
                           search_query=query)