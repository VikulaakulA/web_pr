from flask import Flask
import os
from flask import render_template
from flask import request, redirect
from data.users import User
from data.classes import Class
from data.lessons import Lesson
from data import db_session
from flask_login import current_user, LoginManager, login_required, login_user, logout_user
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/blogs.db")
    app.run(port=8080, host='127.0.0.1')


# начальная страница
@app.route('/')
def best_site():
    return render_template('first.html')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


# api - рандомная генерация пароля
@app.route('/random_password')
def random_password():
    user_request = "http://randomuser.me/api/"
    response = requests.get(user_request)
    if response:
        json_response = response.json()
        password = json_response['results'][0]['login']['password']
        return password
    else:
        print("Ошибка выполнения запроса:")
        print(user_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        return 'error'


# разлогиниться
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# регистрация
@app.route('/registration', methods=['POST', "GET"])
def registration():
    if request.method == 'GET':
        return render_template('registration.html')
    elif request.method == 'POST':
        if request.form["password2"] != request.form["password1"]:
            return render_template('registration.html')
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == request.form["email"]).first():
            return render_template('registration.html')
        # добавление пользователя в бд
        user = User()
        user.first_name = request.form["firstName"]
        user.second_name = request.form["lastName"]
        user.email = request.form["email"]
        user.phone = request.form["telephone_number"]
        user.set_password(request.form["password2"])
        user.about = 'student'
        photo = request.files['file']
        # обязательно приложить фоторгафию
        if photo:
            user.photo = photo.filename
            photo.save(os.path.join('static/new_files', photo.filename))
            db_sess.add(user)
            db_sess.commit()
            login_user(user, remember=True)
            return redirect('/home')
        else:
            return render_template('registration.html')


# вход в учётную запись
@app.route('/join', methods=['POST', "GET"])
def join():
    if request.method == 'GET':
        return render_template('join.html')
    elif request.method == 'POST':
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == request.form['email']).first()
        if user and user.check_password(request.form['password']):
            login_user(user, remember=True)
            return redirect('/home')
        return render_template('join.html')


# вход учителем
@app.route('/teacher_home', methods=['POST', "GET"])
@login_required
def teacher_home():
    if request.method == 'GET':
        return render_template('teacher_home.html')
    elif request.method == 'POST':
        db_sess = db_session.create_session()
        lesson = Lesson()
        lesson.name = request.form["name"]
        lesson.cost = request.form["cost"]
        lesson.date = request.form["date"]
        lesson.time = request.form["time"]
        lesson.user_id = current_user.id
        db_sess.add(lesson)
        db_sess.commit()
        return redirect('/home')


# личный кабинет
@app.route('/home', methods=['POST', "GET"])
@login_required
def home():
    is_lesson = []
    counts = []
    db_sess = db_session.create_session()
    all_lessons = db_sess.query(Lesson).all()
    photo = db_sess.query(User.photo).filter(User.id == current_user.id).first()[0]
    if request.method == 'GET':
        for i in range(len(all_lessons)):
            d = db_sess.query(Class.lesson_id).filter(Class.user_id == current_user.id, Class.done == 0).all()
            count = d.count(db_sess.query(Lesson.id).filter(Lesson.name == all_lessons[i].name).first())
            if count == 0:
                lesson = 1
            else:
                lesson = 0
            is_lesson.append(lesson)
            counts.append(count)
        return render_template("home.html", lesson_spisok=all_lessons, counts=counts, is_lesson=is_lesson, about=current_user.about, photo=photo)
    elif request.method == 'POST':
        return render_template('pay.html', lesson_spisok=all_lessons)


# покупка уроков и занесение операции в бд
@app.route('/pay/<lesson_type>')
@login_required
def pay(lesson_type):
    db_sess = db_session.create_session()
    classes = Class()
    classes.user_id = current_user.id
    classes.lesson_id = db_sess.query(Lesson.id).filter(Lesson.name == lesson_type)
    classes.done = 0
    db_sess.add(classes)
    db_sess.commit()
    return redirect('/home')


# если посмотрели урок, количество дотступных уроков меньше
@app.route('/lesson/<lesson_type>', methods=['POST', "GET"])
@login_required
def lesson(lesson_type):
    if request.method == 'GET':
        return render_template('lesson.html')
    elif request.method == 'POST':
        db_sess = db_session.create_session()
        id = db_sess.query(Lesson.id).filter(Lesson.name == lesson_type).first()
        d = db_sess.query(Class).filter(Class.user_id == current_user.id, Class.done == 0, Class.lesson_id == id.id).all()
        d[0].done = 1
        db_sess.commit()
        return redirect('/home')


if __name__ == '__main__':
    main()

