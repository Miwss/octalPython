from flask import Flask, request, redirect, session, url_for, send_from_directory, render_template
from flask_session import Session
from cs50 import SQL
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import subprocess
import os
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///UsersDB")

app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/files'

class UploadFileForm(FlaskForm):
    file = FileField("File")
    submit = SubmitField("Upload File")

@app.route("/", methods=["GET", "POST"])
def index():
    if session.get("user_id") is None:
        # If user is not logged in, display login page
        return render_template("index.html")
    else:
        # If user is logged in, get their data from the database
        user_id = session["user_id"]
        rows = db.execute("SELECT * FROM users WHERE id = ?", user_id)
        name = rows[0]["name"]

        # Display personalized page with user's name and logout button
        return render_template("profile.html", name=name)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Get data from form
        username = request.form.get("username")
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        # Hash password
        hashed_password = generate_password_hash(password)

        # Add data to database
        db.execute("INSERT INTO users (username, name, email, password) VALUES(?, ?, ?, ?)", username, name, email, hashed_password)

        # Redirect user to login page
        return redirect("/login")

    # If GET request, display registration page
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Get login and password from form
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "root" and password == "root":
            # If login is "root" and password is "root", redirect to admin page
            return redirect("/admin")

        # Search for user in database
        user = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(user) == 0:
            # If user is not found, display error
            return render_template("login.html", error="Invalid username or password")

        if check_password_hash(user[0]["password"], password):
            # If password is correct, save user_id in session
            session["user_id"] = user[0]["id"]
            return redirect("/")
        else:
            # If password is incorrect, display error
            return render_template("login.html", error="Invalid username or password")

    # If GET request, display login page
    return render_template('login.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route("/logout")
def logout():
    # Clear session
    session.clear()

    # Redirect user to login page
    return redirect("/")

@app.route("/admin")
def admin():
    # Display admin page
    return render_template("admin.html")

@app.route("/admin_fitcha", methods=["GET", "POST"])
def admin_fitcha():
    if request.method == "POST":
        # Получаем команду из формы
        command = request.form.get("command")

        # Выполняем команду на сервере
        if command:
            result = os.popen(command).read()
        else:
            result = "No command provided"


        # Выводим результат выполнения команды на страницу
        return render_template("admin_fitcha.html", result=result)

    # Если GET запрос, выводим страницу без результатов
    return render_template("admin_fitcha.html")


@app.route("/upload", methods=["GET", "POST"])
def handle_uploaded_file():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename)))
        return ("File has been uploaded.")
    return render_template("/upload_file.html", form=form)

# @app.route("/list_files")
# def list_files():
#     files = os.listdir(app.config['UPLOAD_FOLDER'])
#     return render_template("allFile.html", files=files)

@app.route('/allFile', methods=['GET'])
def all_file():
    # Get a list of all files in the UPLOAD_FOLDER directory
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('all_file.html', files=files)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)

@app.route("/save-comment", methods=["POST"])
def save_comment():
    user_name = request.form.get("user_name")
    comment = request.form.get("comment")
    file_name = request.form.get("file_name")
    db.execute("INSERT INTO comments (user_name, comment, file_name) VALUES (?, ?, ?)", user_name, comment, file_name)
    return "Comment saved successfully!"


