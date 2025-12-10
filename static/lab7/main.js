function fillFilmList() {
    fetch('/lab7/rest-api/films/')
    .then(function (response) {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(function (films){
        console.log('Films received:', films); // Для отладки
        
        let tbody = document.getElementById('film-list');
        if (!tbody) {
            console.error('Element #film-list not found!');
            return;
        }
        
        tbody.innerHTML = '';
        
        if (films.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4">Нет фильмов</td></tr>';
            return;
        }
        
        for (let i = 0; i < films.length; i++) {
            let tr = document.createElement('tr');
            
            let tdTitle = document.createElement('td');
            let tdTitleRus = document.createElement('td');
            let tdYear = document.createElement('td');
            let tdActions = document.createElement('td');

            // ИСПРАВЛЕНО: показываем оригинальное название всегда
            tdTitle.innerText = films[i].title || '';
            tdTitleRus.innerText = films[i].title_ru || '';
            tdYear.innerText = films[i].year || '';

            let editButton = document.createElement('button');
            editButton.innerText = 'редактировать';
            editButton.onclick = function(){
                editFilm(i);
            };

            let delButton = document.createElement('button');
            delButton.innerText = 'удалить';
            delButton.onclick = function() {
                deleteFilm(i, films[i].title_ru || 'Без названия');
            }

            tdActions.append(editButton);
            tdActions.append(delButton);

            tr.append(tdTitle);
            tr.append(tdTitleRus);
            tr.append(tdYear);
            tr.append(tdActions);

            tbody.append(tr);
        }
    })
    .catch(function(error) {
        console.error('Error loading films:', error);
        let tbody = document.getElementById('film-list');
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="4">Ошибка загрузки фильмов</td></tr>';
        }
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