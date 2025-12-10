function fillFilmList() {
    fetch('/lab7/rest-api/films/')
    .then(function (response) {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(function (films){
        let tbody = document.getElementById('film-list');
        tbody.innerHTML = '';
        
        for (let i = 0; i < films.length; i++) {
            let tr = document.createElement('tr');
            
            // Русское название
            let tdTitleRus = document.createElement('td');
            tdTitleRus.innerText = films[i].title_ru || 'Без названия';
            
            // Оригинальное название
            let tdTitle = document.createElement('td');
            let originalTitle = films[i].title || '';
            
            if (originalTitle && originalTitle !== films[i].title_ru) {
                let span = document.createElement('span');
                span.className = 'original-title';
                span.innerText = `(${originalTitle})`;
                tdTitle.appendChild(span);
            } else {
                tdTitle.innerHTML = '<span class="original-title" style="color: #999;">—</span>';
            }
            
            // Год
            let tdYear = document.createElement('td');
            tdYear.innerText = films[i].year || '—';
            
            // Действия
            let tdActions = document.createElement('td');
            
            let editButton = document.createElement('button');
            editButton.innerText = 'редактировать';
            editButton.onclick = function(){
                editFilm(films[i].id); // Используем ID из БД
            };

            let delButton = document.createElement('button');
            delButton.innerText = 'удалить';
            delButton.onclick = function() {
                deleteFilm(films[i].id, films[i].title_ru || 'этот фильм');
            }

            tdActions.append(editButton);
            tdActions.append(delButton);
            
            // Порядок колонок
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
    if (!confirm(`Вы точно хотите удалить фильм "${title}"?`))
        return;
    fetch(`/lab7/rest-api/films/${id}`, {method: 'DELETE'})
    .then(function (){
        fillFilmList();
    })
    .catch(function(error) {
        console.error('Error deleting film:', error);
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
    const film = {
        title: document.getElementById('title').value,
        title_ru: document.getElementById('title-ru').value,
        year: parseInt(document.getElementById('year').value),
        description: document.getElementById('description').value
    };
    
    // Определяем URL и метод
    const url = id === '' ? '/lab7/rest-api/films/' : `/lab7/rest-api/films/${id}`;
    const method = id === '' ? 'POST' : 'PUT';
    
    fetch(url, {
        method: method,
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(film)
    })
    .then(function(resp) {
        if(resp.ok) {
            fillFilmList();
            hideModal();
            return {};
        }
        return resp.json();
    })
    .then(function(errors) {
        if(errors && errors.description) {
            document.getElementById('description-error').innerText = errors.description;
        }
        if(errors && errors.title_ru) {
            document.getElementById('title-ru-error').innerText = errors.title_ru;
        }
        if(errors && errors.year) {
            document.getElementById('year-error').innerText = errors.year;
        }
    })
    .catch(function(error) {
        console.error('Error:', error);
    });
}

function editFilm(id){
    fetch(`/lab7/rest-api/films/${id}`)
    .then(function(data) {
        return data.json();
    })
    .then(function (film) {
        document.getElementById('id').value = film.id;
        document.getElementById('title').value = film.title;
        document.getElementById('title-ru').value = film.title_ru;
        document.getElementById('year').value = film.year;
        document.getElementById('description').value = film.description;
        document.getElementById('description-error').innerText = '';
        showModal();
    })
    .catch(function(error) {
        console.error('Error loading film:', error);
    });
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, filling film list...');
    fillFilmList();
});