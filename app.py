from functools import wraps
from io import BytesIO
from flask import Flask, render_template, redirect, url_for, flash, abort, make_response, send_file

from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from datetime import datetime
from PIL import Image, ImageDraw
import random

from database.database import db
from database.models.post import BlogPost
from database.models.user import User
from database.models.comment import Comment
from forms.create_post import CreatePostForm
from forms.login import LoginForm
from forms.register import RegistrationForm
from forms.create_comment import CreateCommentForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'TITILAYOMI'
ckeditor = CKEditor(app)
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db.init_app(app)

with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Error creating tables: {e}")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.context_processor
def inject_current_date():
    current_date = datetime.now()
    return {'current_date': current_date}


@app.context_processor
def inject_blog_owner():
    owner = User.query.filter_by(id=1).first()
    print(owner.to_dict())
    return {'owner': owner.to_dict()}


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            if current_user.id != 1:
                return abort(403)
        else:
            return abort(401)  # Unauthorized

        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for("login"))
        if check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("get_all_posts"))
        else:
            flash("Password incorrect, please try again.")
            return redirect(url_for("login"))
    return render_template("login.html", form=form, current_user=current_user)


@app.route('/register', methods=["GET", "POST"])
def register():
    register_form = RegistrationForm()
    if register_form.validate_on_submit():
        name = register_form.name.data
        email = register_form.email.data
        password = register_form.password.data
        hash_password = generate_password_hash(password=password, method="pbkdf2:sha256", salt_length=8)

        if not check_account_exists(email):
            new_user = User(name=name, email=email, password=hash_password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("get_all_posts"))
        else:
            flash("You already have an account with that email, log in instead")
            return redirect(url_for('login'))
    return render_template("register.html", form=register_form, current_user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    comment_form = CreateCommentForm()
    requested_post = BlogPost.query.where(BlogPost.id == post_id).first()
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        new_comment = Comment(
            text=comment_form.comment.data,
            comment_author=current_user,
            parent_post=requested_post
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("show_post", post_id=post_id))

    return render_template("post.html", post=requested_post, current_user=current_user, form=comment_form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.where(BlogPost.id == post_id).first()
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        body=post.body,
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, isEdit=True, current_user=current_user)


@app.route("/about")
def about():
    return render_template("about.html", current_user=current_user)


@app.route("/contact")
def contact():
    return render_template("contact.html", current_user=current_user)


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        date = datetime.now().strftime("%B %d, %Y")
        new_post = BlogPost(
            title=form.title.data,
            date=date,
            body=form.body.data,
            author=current_user,
            author_id=int(current_user.id),
            img_url=form.img_url.data,
            subtitle=form.subtitle.data,
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, isEdit=False, current_user=current_user)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("get_all_posts"))


def check_account_exists(email) -> bool:
    """
    This function checks if the user already has an account
    :param email:
    :return: bool
    """
    user_count = User.query.filter_by(email=email).count()
    if user_count == 0:
        return False
    else:
        return True


def generate_random_avatar(size=100):
    # Create a blank image with a solid background color
    image = Image.new('RGB', (size, size), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    draw = ImageDraw.Draw(image)

    # Ensure that x0 is less than or equal to x1 and y0 is less than or equal to y1
    for _ in range(random.randint(5, 10)):
        x0, x1 = sorted([random.randint(0, size), random.randint(0, size)])
        y0, y1 = sorted([random.randint(0, size), random.randint(0, size)])
        draw.rectangle([x0, y0, x1, y1], fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

    return image


@app.route('/random_avatar')
def random_avatar():
    avatar = generate_random_avatar()
    avatar_io = BytesIO()
    avatar.save(avatar_io, 'PNG')
    avatar_io.seek(0)
    response = make_response(send_file(avatar_io, mimetype='image/png'))
    return response


if __name__ == '__main__':
    app.run(debug=True)
