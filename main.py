from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
# Import your forms from the forms.py
from forms import CreatePostForm, RegistrationForm, LoginForm, CommentForm
from flask_migrate import Migrate
from functools import wraps
from flask import abort




'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['CKEDITOR_PKG_TYPE'] = 'basic'
app.config['CKEDITOR_CDN'] = 'https://cdn.ckeditor.com/4.25.1-lts/basic/ckeditor.js'

ckeditor = CKEditor(app)
Bootstrap5(app)

# TODO: Configure Flask-Login


# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)
migrate = Migrate(app, db)


## Section for initiating flask-login related classes
login_manager = LoginManager() # Flask login class
login_manager.init_app(app)
login_manager.login_view = 'login' # Redirect to login page if @login_required fails
login_manager.login_message = "You must be logged in to access this page."

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# CONFIGURE TABLES
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    # author: Mapped[str] = mapped_column(String(250), nullable=False) ## Use the other author below for relational DB
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    # comment: Mapped[str] = mapped_column(String(250), nullable=True)

    # ✅ Set up relationship to comments
    comments: Mapped[list["Comments"]] = relationship("Comments", back_populates="post") 

    # ✅ Set up relationship to User
    author: Mapped["User"] = relationship("User", back_populates="posts_author")

     # ✅ Foreign key that links this blog post to a user
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False) ## "users in users.id"  is from the __tablename__




class Comments(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(String(1000), nullable=True)

    # ✅ Set up relationship to BlogPost.  "post" is the name for relationship purposes..to comments in BlogPost
    post: Mapped["BlogPost"] = relationship("BlogPost", back_populates="comments") 

    # ✅ Set up relationship to User.  "author" is the name for relationship purposes..to user_comments in User
    author: Mapped["User"] = relationship("User", back_populates="user_comments")    

    # ✅ Foreign key that links this comment to a User
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # ✅ Foreign key that links this comment to a BlogPost
    blog_id: Mapped[int] = mapped_column(ForeignKey("blog_posts.id"), nullable=False)




# TODO: Create a User table for all your registered users. 
class User(UserMixin, db.Model): # Add UserMixin
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))

    # ✅ Set up relationship to User
    posts_author: Mapped[list["BlogPost"]] = relationship("BlogPost", back_populates="author")
    user_comments: Mapped[list["Comments"]] = relationship("Comments", back_populates="author")

with app.app_context():
    db.create_all()



## Section for Decorators  ####

# def admin_only(func):
#     def wrapper_function():
#         if current_user.is_authenticated and current_user.id == 1:
#             func()
#         else:
#             # return render_template("404_forbidden.html")
#             print("this user is not allowed.....!!!!!")
#     return wrapper_function

def admin_only(func):
    @wraps(func)
    def wrapper_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.id == 1:
            return func(*args, **kwargs)
        else:
            # Option 1: Abort with 403 Forbidden
            abort(403)

            # Option 2: Show custom forbidden page
            # return render_template("403_forbidden.html"), 403
    return wrapper_function


# TODO: Use Werkzeug to hash the user's password when creating a new user.
@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = db.session.scalar(db.select(User).where(User.email == request.form["email"]))
        if existing_user:
            flash("You've already signed up with that email, login instead!", "warning")
            return redirect(url_for('login'))

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        secure_password = generate_password_hash(password=password, method="pbkdf2:sha256:600000", salt_length=8)
        
        new_user = User(name=name, email=email, password=secure_password)
        db.session.add(new_user)
        db.session.commit()
        
        # Log in and authenticate user after adding details to database.
        login_user(new_user)
        flash("Registration successful! You are now logged in.", "success")
        return redirect(url_for("get_all_posts"))
    return render_template("register.html", logged_in=current_user.is_authenticated, form = form)



# TODO: Retrieve a user from the database based on their email. 
@app.route('/login', methods=["POST", "GET"])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = db.session.scalar(db.select(User).where(User.email==email))
        
        if not user:
            flash("That email does not exist, please try again.", 'danger')
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.', 'danger')
            return redirect(url_for('login'))
        else:
            login_user(user) # Uncommented this line
            flash('Login successful!', 'success')

            # Redirect to a page after successful login, e.g., 'secrets' or 'home'
            return redirect(url_for('get_all_posts'))
            
    # print("Form errors:", form.errors)
    return render_template("login.html", form=form, logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    # try:
    #  print(current_user.name)  ##################################################################### TEST ###################
    #  print(current_user.id)  ##################################################################### TEST ###################
    # except AttributeError:
    #     print("No_user_logged_in")
    return render_template("index.html", all_posts=posts)


# # TODO: Allow logged-in users to comment on posts
# @app.route("/post/<int:post_id>")
# def show_post(post_id):
#     requested_post = db.get_or_404(BlogPost, post_id)
#     return render_template("post.html", post=requested_post)



# TODO: Allow logged-in users to comment on posts #####################################################################
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    comment_form = CommentForm()
    add_post = Comments()
    if comment_form.validate_on_submit():
        add_post.content = comment_form.comment.data 
        add_post.user_id = current_user.id
        add_post.blog_id = post.id
        db.session.add(add_post)
        db.session.commit()
    post = db.get_or_404(BlogPost, post_id)
    result = db.session.execute(db.select(Comments))
    comments = result.scalars().all()
    return render_template("post.html", post=post, form = comment_form, comments = comments,  logged_in=current_user.is_authenticated)



# TODO: Use a decorator so only an admin user can create a new post
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


# TODO: Use a decorator so only an admin user can edit a post
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


# TODO: Use a decorator so only an admin user can delete a post
@admin_only
@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5002)
