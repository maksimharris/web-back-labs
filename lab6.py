from flask import Blueprint, request, render_template, session, redirect

lab6 = Blueprint('lab6', __name__)

# Генерация информации для каждого офиса с разной стоимостью             
offices = []
for i in range(1, 11):
    # Разная стоимость в зависимости от номера офиса
    price = 900 + (i % 3) * 200  # 900, 1100, 1300 руб.
    offices.append({
        'number': i,      # номер офиса
        'tenant': "",     # арендатор
        'price': price    # стоимость аренды
    })

@lab6.route('/lab6/')
def main():
    return render_template('/lab6/lab6.html')

@lab6.route('/lab6/json-rpc-api/', methods=['POST'])
def api():
    data = request.json
    id = data['id']
    
    if data['method'] == 'info': 
        return {
            'jsonrpc': '2.0',
            'result': offices,
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
        
        # Проверяем, не забронировал ли уже пользователь другой офис
        user_has_office = any(office['tenant'] == login for office in offices)
        if user_has_office:
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 5,
                    'message': 'You already have a booked office'
                },
                'id': id
            }
        
        for office in offices:
            if office['number'] == office_number:
                if office['tenant'] != '':
                    return {
                        'jsonrpc': '2.0',
                        'error': {
                            'code': 2,
                            'message': 'Already booked'
                        },
                        'id': id
                    }
                office['tenant'] = login
                return {
                    'jsonrpc': '2.0',
                    'result': 'success',
                    'id': id
                }
        
        # Если офис не найден
        return {
            'jsonrpc': '2.0',
            'error': {
                'code': 4,
                'message': 'Office not found'
            },
            'id': id
        }
    
    if data['method'] == 'cancellation':  # отмена
        office_number = data['params']
        office_found = False
        for office in offices:
            if office['number'] == office_number:
                office_found = True
                if office['tenant'] == login:
                    office['tenant'] = ""
                    return {
                        'jsonrpc': '2.0',
                        'result': 'cancellation successful',
                        'id': id
                    }
                else:
                    return {
                        'jsonrpc': '2.0',
                        'error': {
                            'code': 3,
                            'message': 'You are not the tenant of this office'
                        },
                        'id': id
                    }
        
        # Если офис не найден
        if not office_found:
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 4,
                    'message': 'Office not found'
                },
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

@lab6.route('/lab6/logout', methods=['POST'])
def logout():
    # Офисы остаются забронированными даже после выхода пользователя
    session.clear()  # Очищаем сессию
    return redirect('/lab5/login')