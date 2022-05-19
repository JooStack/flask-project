from flask import Flask, render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt


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

class LoginForm(Form) :
    username = StringField("Username")
    password = StringField("Parola")


app = Flask(__name__)
app.secret_key = "myblog"

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

# Register
@app.route("/register", methods = ["GET", "POST"])
def register() :
    form = RegisterForm(request.form)
    if request.method == "POST" and form.validate() :
        name = form.name.data
        username = form.username.data
        email = form.email.data

        password = sha256_crypt.encrypt(form.password.data)
        cursor = mysql.connection.cursor()

        sorgu = "Insert into users(name,email,username,password) VALUES(%s,%s,%s,%s)"
        cursor.execute(sorgu,(name,email,username,password))

        mysql.connection.commit()
        cursor.close()

        flash("Successful Registration...","success")
        return redirect(url_for("login"))
    else :
        return render_template("register.html", form = form)

@app.route("/article/<string:id>")
def detail(id) :
    return "Article Id : " + id

# Login
@app.route("/login", methods = ["GET","POST"])
def login() :
    form = LoginForm(request.form)
    if request.method == "POST" :
        username = form.username.data 
        password_entered = form.password.data 

        cursor = mysql.connection.cursor() 

        sorgu = "Select * From users where username = %s "

        result = cursor.execute(sorgu, (username,))

        if result > 0 :
            data = cursor.fetchone()
            real_password = data["password"]
            if sha256_crypt.verify(password_entered,real_password) :
                flash("Successfully logged in...","success")
                
                session["login_in"] = True
                session["username"] = username
                
                return redirect(url_for("index"))
            else :
                flash("Invalid password..","danger")
                return redirect(url_for("login"))
                
        else :
            flash("Such a user is not registered..","danger")
            return redirect(url_for("login"))


    return render_template("login.html", form = form)


if __name__ == "__main__" :
    app.run(debug=True)

    