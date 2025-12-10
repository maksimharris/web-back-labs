function fillFilmList() {
    fetch('/lab7/rest-api/films/')
    .then(function (data) {
        return data.json();
    })
    .then(function (films){
        let tbody = document.getElementById('film-list');
        tbody.innerHTML = '';
        
        for (let i = 0; i < films.length; i++) {
            let tr = document.createElement('tr');
            
            // Первая колонка: русское название (главное)
            let tdTitleRus = document.createElement('td');
            tdTitleRus.innerText = films[i].title_ru || 'Без названия';
            
            // Вторая колонка: оригинальное название (второстепенное)
            let tdTitle = document.createElement('td');
            let originalTitle = films[i].title || '';
            
            if (originalTitle && originalTitle !== films[i].title_ru) {
                // Если есть оригинальное название и оно отличается от русского
                let span = document.createElement('span');
                span.className = 'original-title';
                span.innerText = `(${originalTitle})`;
                tdTitle.appendChild(span);
            } else {
                // Если оригинального нет или оно совпадает с русским
                tdTitle.innerHTML = '<span class="original-title" style="color: #999;">—</span>';
            }
            
            // Третья колонка: год
            let tdYear = document.createElement('td');
            tdYear.innerText = films[i].year || '—';
            
            // Четвертая колонка: действия
            let tdActions = document.createElement('td');
            
            let editButton = document.createElement('button');
            editButton.innerText = 'редактировать';
            editButton.onclick = function(){
                editFilm(i);
            };

            let delButton = document.createElement('button');
            delButton.innerText = 'удалить';
            delButton.onclick = function() {
                deleteFilm(i, films[i].title_ru || 'этот фильм');
            }

            tdActions.append(editButton);
            tdActions.append(delButton);
            
            // Добавляем колонки в правильном порядке:
            // 1. Русское название, 2. Оригинальное, 3. Год, 4. Действия
            tr.append(tdTitleRus);
            tr.append(tdTitle);
            tr.append(tdYear);
            tr.append(tdActions);

            tbody.append(tr);
        }
    })
    .catch(function(error) {
        console.error('Error loading films:', error);
    });
}


function deleteFilm(id, title){
    if (!confirm(`Вы точно хотите удалить фильм "${title}"?`)) {
        return;
    }
    
    fetch(`/lab7/rest-api/films/${id}`, {
        method: 'DELETE'
    })
    .then(function(response) {
        if (!response.ok) {
            throw new Error('Delete failed');
        }
        fillFilmList();
    })
    .catch(function(error) {
        console.error('Error deleting film:', error);
        alert('Не удалось удалить фильм');
    });
}

function showModal(){
    const modal = document.querySelector('div.modal');
    if (modal) {
        modal.style.display = 'block';
        document.getElementById('description-error').innerText = '';
    }
}

function hideModal(){
    const modal = document.querySelector('div.modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function cancel(){
    hideModal();
}

function addFilm(){
    document.getElementById('id').value = '';
    document.getElementById('title').value = '';
    document.getElementById('title-ru').value = '';
    document.getElementById('year').value = '';
    document.getElementById('description').value = '';
    document.getElementById('description-error').innerText = '';
    showModal();
}

function sendFilm() {
    const id = document.getElementById('id').value;
    const title = document.getElementById('title').value.trim();
    const title_ru = document.getElementById('title-ru').value.trim();
    const year = parseInt(document.getElementById('year').value);
    const description = document.getElementById('description').value.trim();
    
    // Валидация
    if (!title_ru) {
        alert('Введите русское название фильма');
        return;
    }
    
    if (!description) {
        document.getElementById('description-error').innerText = 'Заполните описание';
        return;
    }
    
    if (isNaN(year) || year < 1888 || year > new Date().getFullYear() + 1) {
        alert('Введите корректный год');
        return;
    }
    
    const film = {
        title: title || title_ru, // Если оригинальное пустое, используем русское
        title_ru: title_ru,
        year: year,
        description: description
    };
    
    console.log('Sending film:', film); // Для отладки
    
    const url = id === '' ? '/lab7/rest-api/films/' : `/lab7/rest-api/films/${id}`;
    const method = id === '' ? 'POST' : 'PUT';
    
    fetch(url, {
        method: method,
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(film)
    })
    .then(function(response) {
        console.log('Response status:', response.status); // Для отладки
        
        if (response.ok) {
            fillFilmList();
            hideModal();
            return null;
        }
        return response.json();
    })
    .then(function(errors) {
        if (errors) {
            console.log('Server errors:', errors); // Для отладки
            if (errors.description) {
                document.getElementById('description-error').innerText = errors.description;
            }
        }
    })
    .catch(function(error) {
        console.error('Error:', error);
        alert('Произошла ошибка при сохранении фильма');
    });
}

function editFilm(id){
    fetch(`/lab7/rest-api/films/${id}`)
    .then(function(response) {
        if (!response.ok) {
            throw new Error('Film not found');
        }
        return response.json();
    })
    .then(function (film) {
        document.getElementById('id').value = id;
        document.getElementById('title').value = film.title || '';
        document.getElementById('title-ru').value = film.title_ru || '';
        document.getElementById('year').value = film.year || '';
        document.getElementById('description').value = film.description || '';
        document.getElementById('description-error').innerText = '';
        showModal();
    })
    .catch(function(error) {
        console.error('Error loading film:', error);
        alert('Не удалось загрузить фильм для редактирования');
    });
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, filling film list...');
    fillFilmList();
});