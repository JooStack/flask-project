import re
from flask import Flask, render_template,flash,redirect,url_for,session ,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps

# User Login Decarator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session :
            return f(*args, **kwargs)
        else :
            flash("Please login to view this page..", "danger")
            return redirect(url_for("login"))
    return decorated_function

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

# Article Page
@app.route("/articles")
def articles() :
    cursor = mysql.connection.cursor()
    
    sorgu = "Select * From articles"

    result = cursor.execute(sorgu)

    if result > 0 :
        articles = cursor.fetchall()
        return render_template("articles.html",articles = articles)

    else :

        return render_template("articles.html")


@app.route("/dashboard")
@login_required
def dashboard() :
    cursor = mysql.connection.cursor()

    sorgu = "Select * From articles where author = %s"
    
    result = cursor.execute(sorgu,(session["username"],))

    if result > 0 :
        articles = cursor.fetchall()
        return render_template("dashboard.html", articles = articles) 
    else :
        return render_template("dashboard.html")


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

# @app.route("/article/<string:id>")
# def detail(id) :
#     return "Article Id : " + id

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
                
                session["logged_in"] = True
                session["username"] = username
                return redirect(url_for("index"))
            else :
                flash("Invalid password..","danger")
                return redirect(url_for("login"))
                
        else :
            flash("Such a user is not registered..","danger")
            return redirect(url_for("login"))


    return render_template("login.html", form = form)

# Logout 
@app.route("/logout")
def logout() :
    session.clear()
    return redirect(url_for("index"))

# Detail 

@app.route("/article/<string:id>")
def article(id) :
    cursor = mysql.connection.cursor()
    sorgu = "Select * From articles where id = %s"
    result = cursor.execute(sorgu,(id,))
    if result > 0 :
        article = cursor.fetchone()
        return render_template("article.html", article = article)
    else :
        return render_template("article.html")

# Add Article
@app.route("/addarticle",methods = ["GET", "POST"])
def addarticle() :
    form = ArticleForm(request.form)
    if request.method == "POST" and form.validate() :
        title = form.title.data
        content = form.content.data

        cursor = mysql.connection.cursor()

        sorgu = "Insert into articles(title,author,content) VALUES(%s,%s,%s)"

        cursor.execute(sorgu,(title,session["username"],content))

        mysql.connection.commit()

        cursor.close()

        flash("Article successfully added","success")
        return redirect(url_for("dashboard"))

    return render_template("addarticle.html", form = form)

# Delete Article
@app.route("/delete/<string:id>")
@login_required
def delete(id) :
    cursor = mysql.connection.cursor()
    sorgu = "Select * from articles where author = %s and id = %s"
    result = cursor.execute(sorgu, (session["username"],id))

    if result > 0 :
        sorgu2 = "Delete from articles where id = %s"
        cursor.execute(sorgu2,(id,))
        mysql.connection.commit()
        return redirect(url_for("dashboard"))

    else :
        
        flash("There is no such article or you are not authorized to do this..","danger")
        return redirect(url_for("index"))

# Article Update
@app.route("/edit/<string:id>",methods = ["GET","POST"])
@login_required
def update(id) :
    if request.method == "GET" :
        cursor = mysql.connection.cursor()
        sorgu = "Select * from articles where id = %s and author = %s"
        result = cursor.execute(sorgu, (id,session["username"]))

        if result == 0 :
            flash("There is no such a article or you are not authorized to do this..")
            return redirect(url_for("index"))
        else :
            article = cursor.fetchone() 
            form = ArticleForm()

            form.title.data = article["title"]
            form.content.data = article["content"]
            return render_template("update.html", form = form)
    else :
        # Post Request
        form = ArticleForm(request.form)

        newTitle = form.title.data
        newContent = form.content.data

        sorgu2 = "Update articles Set title = %s, content = %s where id = %s"

        cursor = mysql.connection.cursor()

        cursor.execute(sorgu2,(newTitle, newContent, id))
        mysql.connection.commit()

        flash("Updating successful","success")

        return redirect(url_for("dashboard"))

# Article Form
class ArticleForm(Form) :
    title = StringField("Article Title",validators=[validators.Length(min=5,max=50)])
    content = TextAreaField("Article Content",validators=[validators.Length(min = 10)])


# Search
@app.route("/search",methods = ["GET","POST"])
def search() :
    if request.method == "GET" :
        return redirect(url_for("index"))
    else :
        keyword = request.form.get("keyword")
        cursor = mysql.connection.cursor()
        sorgu = "Select * from articles where title like '%" + keyword + "%'"
        result = cursor.execute(sorgu)

        if result == 0 :
            flash("No article found matching the search term..","warning")
            return redirect(url_for("articles"))
        else :
            articles = cursor.fetchall()
            return render_template("articles.html", articles = articles)        


if __name__ == "__main__" :
    app.run(debug=True)

# last

    