import os
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Настройки путей, чтобы стили и картинки из assets и data больше не пропадали
app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')
app.config['SECRET_KEY'] = 'SUPER_SECRET_KEY_12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project_database.db'
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    history = db.relationship('History', backref='user', lazy=True)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

# --- МАРШРУТЫ (ROUTES) ---

@app.route('/')
@login_required
def index():
    return render_template('index.html', user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error_msg = ""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        error_msg = "Неверный логин или пароль!"
        
    return f'''
        <!DOCTYPE html>
        <html lang="ru">
        <head><meta charset="UTF-8"><title>Вход</title></head>
        <body style="font-family: sans-serif; background: #f4f4f4; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0;">
            <div style="background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); width: 300px;">
                <h2 style="text-align: center; margin-top: 0;">Вход</h2>
                <p style="color: red; text-align: center;">{error_msg}</p>
                <form method="POST">
                    <label>Логин:</label><br>
                    <input type="text" name="username" style="width: 100%; padding: 8px; margin: 5px 0 15px 0; box-sizing: border-box;" required><br>
                    <label>Пароль:</label><br>
                    <input type="password" name="password" style="width: 100%; padding: 8px; margin: 5px 0 15px 0; box-sizing: border-box;" required><br>
                    <button type="submit" style="width: 100%; padding: 10px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">Войти</button>
                </form>
                <p style="text-align: center; margin-top: 15px; font-size: 14px;">Нет аккаунта? <a href="/register">Регистрация</a></p>
            </div>
        </body>
        </html>
    '''

@app.route('/register', methods=['GET', 'POST'])
def register():
    error_msg = ""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            error_msg = "Этот логин уже занят!"
        else:
            hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
            is_first = User.query.count() == 0
            new_user = User(username=username, password=hashed_pw, is_admin=is_first)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
            
    return f'''
        <!DOCTYPE html>
        <html lang="ru">
        <head><meta charset="UTF-8"><title>Регистрация</title></head>
        <body style="font-family: sans-serif; background: #f4f4f4; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0;">
            <div style="background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); width: 300px;">
                <h2 style="text-align: center; margin-top: 0;">Регистрация</h2>
                <p style="color: red; text-align: center;">{error_msg}</p>
                <form method="POST">
                    <label>Придумайте логин:</label><br>
                    <input type="text" name="username" style="width: 100%; padding: 8px; margin: 5px 0 15px 0; box-sizing: border-box;" required><br>
                    <label>Придумайте пароль:</label><br>
                    <input type="password" name="password" style="width: 100%; padding: 8px; margin: 5px 0 15px 0; box-sizing: border-box;" required><br>
                    <button type="submit" style="width: 100%; padding: 10px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold;">Создать аккаунт</button>
                </form>
                <p style="text-align: center; margin-top: 15px; font-size: 14px;">Уже есть аккаунт? <a href="/login">Войти</a></p>
            </div>
        </body>
        </html>
    '''

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        return "Доступ запрещен", 403
    users = User.query.all()
    all_history = History.query.all()
    
    users_list = ""
    for u in users:
        role = "Админ" if u.is_admin else "Юзер"
        users_list += f"<li><b>{u.username}</b> (ID: {u.id}) [ {role} ]</li>"
        
    history_list = ""
    for h in all_history:
        history_list += f"<li>Юзер <b>{h.user.username}</b>: {h.action}</li>"
    
    if not history_list:
        history_list = "<li>Действий пока нет.</li>"
    
    return f'''
        <!DOCTYPE html>
        <html lang="ru">
        <head><meta charset="UTF-8"><title>Панель админа</title></head>
        <body style="font-family: sans-serif; padding: 20px; color: #333;">
            <div style="max-width: 800px; margin: 0 auto;">
                <h2>Панель администратора</h2>
                <p><a href="/logout" style="color: red;">Выйти из системы</a> | <a href="/">На главную</a></p>
                <hr>
                <h3>Пользователи:</h3>
                <ul>{users_list}</ul>
                <hr>
                <h3>История логов:</h3>
                <ul>{history_list}</ul>
            </div>
        </body>
        </html>
    '''

@app.route('/save_history', methods=['POST'])
@login_required
def save_history():
    data = request.get_json()
    action_text = data.get('action')
    if action_text:
        new_log = History(action=action_text, user_id=current_user.id)
        db.session.add(new_log)
        db.session.commit()
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 400

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=8000, debug=True)
