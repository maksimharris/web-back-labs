from flask import Blueprint, request, render_template, make_response,redirect, session

lab6  = Blueprint('lab6',__name__)

#Генерация информации для каждого офиса             
offices = []
for i in range(1,11):
    offices.append({'number':i, #номер офиса
                    'tenant': ""} #арендатор
    )

@lab6.route('/lab6/')
def main():
    return render_template('/lab6/lab6.html')
@lab6.route('/lab6/json-rpc-api/',methods = ['POST'])
 #API JSON-RPC - протокол удалённого вызова процедур (RPC), использующий JSON для кодирования сообщений. 
def api():
   data = request.json
   id = data['id']
   if data['method'] == 'info': 
        return {
        'jsonrpc':'2.0',
        'result':offices,
        'id':id
        } # - возвращаем при методе info информацию о офисах
   #проверка авторизации и выдача ошибки в случае отстутсвия логина
   login = session.get('login')
   if not login:
       return {
           'jsonrpc':'2.0',
           'error':{
               'code':1,
               'message':'Unauthorized'
           },
           'id':id
       }
   if data['method'] == 'booking': #booking - бронирование кабинета (по номеру)
      office_number = data['params']
      for office in offices:
          if office['number'] == office_number:
              if office['tenant'] != '':
                  return {
                      'jsonrpc':'2.0',
                      'error':{
                          'code':2,
                          'message':'Already booked'
                      },
                      'id':id
                  }
              office['tenant'] = login
              return {
                  'jsonrpc':'2.0',
                  'result':'success',
                  'id':id
              }
   #возвращаем ошибку, если метод нам неизвестен
   return {
      'jsonrpc':'2.0',
      'error': {
         'code':-32601,
         'message':'not found'
      },
      'id':id
   }



