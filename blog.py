from flask import Flask, render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed


# User Registration Form
class RegisterForm(Form):
    name = StringField("Name Surname", validators=[validators.Length(min = 4, max = 25)])
    username = StringField("Username", validators=[validators.Length(min = 5, max = 35)])
    email = StringField("Email Address", validators=[validators.Email(message="Please enter valid Email address! ")])
    password = PasswordField("Password : ", validators=[
        validators.DataRequired(message = "Please enter password"),
        validators.EqualTo(fieldname = "confirm", message="Your password does not match")
    ])
    confirm = PasswordField("Confirm your password")

app = Flask(__name__)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "myblog"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)



@app.route("/")
def index() :
    articles = [
        {"id":1,"title":"Deneme1","content":"Deneme1 içerik"},
        {"id":2,"title":"Deneme2","content":"Deneme2 içerik"},
        {"id":3,"title":"Deneme3","content":"Deneme3 içerik"}
    ]
    return render_template("index.html",answer="evet", articles = articles)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/article/<string:id>")
def detail(id) :
    return "Article Id : " + id


if __name__ == "__main__" :
    app.run(debug=True)

    