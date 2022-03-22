from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
from forms import CityForm, LoginForm, RegisterForm
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from brew_api import BrewApi
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///beer.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    posts = relationship("CommentPost", back_populates="author")


class CommentPost(db.Model):
    __tablename__ = "comment_posts"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)


db.create_all()

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function

@app.route("/", methods=["GET", "POST"])
def search():
    search_bar = CityForm()
    if search_bar.validate_on_submit():
        city_to_search = search_bar.city.data

        return redirect(url_for("results", city=city_to_search))

    return render_template("index.html", form=search_bar)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        if User.query.filter_by(email=form.email.data).first():
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )

        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("search"))

    return render_template("register.html", form=form, current_user=current_user)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.`
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('search'))
    return render_template("login.html", form=form, current_user=current_user)

@app.route("/results/<city>")
def results(city):
    brew = BrewApi(city)
    city_results = brew.search_city()
    for result in city_results:
        print(result)
    return render_template("results.html", results=city_results)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('search'))


@app.route("/review/<id_>")
def review(id_):
    listing_id_ = id_



if __name__ == "__main__":
    app.run(debug=True)

