from flask import Flask, render_template, request, jsonify
import mysql.connector

app = Flask(__name__)  

@app.route('/user_register', methods=['POST'])
def user_register(): 
    req = request.get_json()
    
    if not req or not all(k in req for k in ('name', 'email', 'password')):
        return jsonify({'result': False, 'error': 'Заполните все поля'}), 400

    name = req['name']
    login = req['email']
    password = req['password']
    
    try:
        cnx = mysql.connector.connect(host="185.114.247.43", port=3306, database="sch688_vvedenie", user="sch688_vvedenie", password="Qwerty123")
        cur = cnx.cursor(buffered=True)
        
        sql = 'INSERT INTO `users` (`username`, `email`, `password_hash`) VALUES (%s, %s, %s)'
        user_data = (name, login, password) 
        
        cur.execute(sql, user_data)
        cnx.commit()
        
        user_id = cur.lastrowid 
        
        return jsonify({
            'result': True, 
            'user': {
                'id': user_id,
                'name': name,
                'email': login
            }
        })

    except mysql.connector.Error as err:
        print(f"Database error: {err}") 
        if err.errno == 1062:
            return jsonify({'result': False, 'error': 'Этот email уже зарегистрирован'}), 400
        return jsonify({'result': False, 'error': 'Ошибка базы данных'}), 500
        
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cur.close()
            cnx.close()


# 2. РОУТ ДЛЯ АВТОРИЗАЦИИ (ВХОД В СИСТЕМУ) — ТОТ САМЫЙ КУСОК
@app.route('/user_login', methods=['POST'])
def user_login():
    req = request.get_json()
    if not req or 'email' not in req or 'password' not in req:
        return jsonify({'result': False, 'error': 'Заполните все поля'}), 400

    login = req['email']
    password = req['password']

    try:
        cnx = mysql.connector.connect(host="185.114.247.43", port=3306, database="sch688_vvedenie", user="sch688_vvedenie", password="Qwerty123")
        cur = cnx.cursor(dictionary=True) 
        
        sql = 'SELECT * FROM `users` WHERE `email` = %s AND `password_hash` = %s'
        cur.execute(sql, (login, password))
        user = cur.fetchone() 
        
        if user:
            return jsonify({'result': True, 'user': {'name': user['username'], 'email': user['email']}})
        else:
            return jsonify({'result': False, 'error': 'Неверная почта или пароль'}), 401

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return jsonify({'result': False, 'error': 'Ошибка базы данных'}), 500
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cur.close()
            cnx.close()



@app.route("/")
def registration():
    return render_template('registration.html')

@app.route("/login")
def login():
    return render_template('login.html')


@app.route("/dashboard")
def dashboard():
    return "Добро пожаловать в личный кабинет!"



if __name__ == '__main__':
    app.run(debug=True)
