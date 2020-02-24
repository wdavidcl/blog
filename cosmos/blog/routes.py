from flask import render_template, redirect, url_for, request
from sqlalchemy import desc
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from datetime import datetime
from blog import app,login_manager
from blog.models import *
import os

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def check_session():
    try:
        data = {'username': current_user.username, 'name': current_user.name, 'lastname': current_user.lastname}
        head = {'url1': 'admindashboard', 'url2': 'logout', 'text1': 'Dashboard', 'text2': 'Logout'}
    except Exception as e:
        data = {'username': '', 'name': 'Guest', 'lastname': 'User'}
        head = {'url1':'signup', 'url2': 'login', 'text1': 'Sign up', 'text2': 'Login'}
    return [head,data]
#Render the home page if the user request the "http://xxx.xxx.xxx.xxx/"
@app.route('/')
@app.route('/index')
def index():
    [head,data] = check_session()
    articles = Article.query.order_by(desc(Article.timestamp)).all()
    categories=[]
    for article in articles:
        tags =str(article.tags).split(';')
        for tag in tags:
            categories.append(tag)
    seen = set()
    list = []
    for x in categories:
        if x not in seen:
            list.append(x)
            seen.add(x)
    page = request.args.get('page', 1, type=int)
    articles = Article.query.order_by(Article.timestamp.desc()).paginate(page=page, per_page=5)

    return render_template('index.html', head=head, articles=articles, tags=list,  title='Home')

#Render the home page if the user request the "/about"
@app.route('/about')
def about():
    [head,data] = check_session()
    return render_template('about.html', head=head,  title='About')


@app.route('/contact')
def contact():
    [head,data] = check_session()
    return render_template('contact.html', head=head,  title='Contact')


@app.route('/bloglist')
def bloglist():
    order = request.args.get('tag','newer',type=str)
    page = request.args.get('page', 1, type=int)
    # print(order)
    [head,data] = check_session()
    if order == "newer":
        articles = Article.query.order_by(Article.timestamp.desc()).paginate(page=page, per_page=5)
    elif order == "older":
        articles = Article.query.paginate(page=page, per_page=5)
    else:
        articles = Article.query.filter(Article.tags.ilike("%" + order + "%")).paginate(page=page)

    return render_template('bloglist.html', head=head, articles=articles, tags=list,  title='Blogs '+order,order_tag=order)


@app.route('/detail', methods=['GET', 'POST'])
def detail():
    id_article = request.args.get('id')
    form = CommentForm()
    message = ''
    if request.method == "POST":
        if form.validate_on_submit():
            #print('++++ validado')
            now = datetime.now()
            try:
                if current_user.access > 0:
                    allow = True
                else:
                    allow = False
                new_comment = Comment(id=current_user.id,id_article=id_article, name=current_user.name, lastname=current_user.lastname,
                                      comment=form.comment__.data, timestamp=now, allow=allow)
                db.session.add(new_comment)
                db.session.commit()
            except Exception as e:
                new_comment = Comment(id=0, id_article=id_article, name=form.name__.data, lastname=form.lastname.data,
                                      comment=form.comment__.data, timestamp=now, allow=False)
                db.session.add(new_comment)
                db.session.commit()
                message = 'The comment was saved an it is waiting for approval'

    # Checking for logging
    [head,data] = check_session()
    # Retrieving article and author
    try:
        article = Article.query.filter_by(id_article=id_article).first()
        user = User.query.filter_by(id=article.id).first()
    except Exception as e:
        print(e)
    articles = Article.query.filter_by().all()
    categories = []
    for art in articles:
        tags =str(art.tags).split(';')
        for tag in tags:
            categories.append(tag)
    seen = set()
    list = []
    for x in categories:
        if x not in seen:
            list.append(x)
            seen.add(x)

    try:
        id = current_user.id
        logged = False
    except:
        logged = True

    comments = Comment.query.filter_by(id_article=id_article).all()
    n_comments = Comment.query.filter_by(id_article=id_article, allow=True).all()
    number=len(n_comments)
    return render_template('detail.html', user=user, article=article, head=head, data=data, comments=comments,
                           number=number, tags=list, form=form, logged=logged, message=message)


@app.route('/blogform', methods=['GET', 'POST'])
@login_required
def blogfrom():
    [head,data] = check_session()
    form = BlogForm()
    if current_user.access > 1:
        if form.validate_on_submit():
            now = datetime.now()
            url_image = ''
            new_article = Article(id=current_user.id, title=form.title.data, tags=form.tags.data, article=form.article.data,
                               url_image=url_image, timestamp=now, allow=False, author=str(current_user.name)+' '+str(current_user.lastname))
            db.session.add(new_article)
            db.session.commit()
            last_post = Article.query.filter_by(id=current_user.id).order_by(desc(Article.timestamp)).first()
            return redirect(url_for('select_image', id=last_post.id_article))
        return render_template('blog-form.html', head=head, form=form)
    else:
        return redirect(url_for('dashboard'))


@app.route('/select', methods=['GET', 'POST'])
@login_required
def select_image():
    head=check_session()
    id_article = request.args.get('id')
    if request.method == 'POST':
        f = request.files['inputFile']


        f.save(os.path.join(app.config['UPLOAD_FOLDER'], 'img'+str(id_article)+'.jpg'))

        return redirect(url_for('detail',id=id_article))
    return render_template('select.html',id_article=id_article,head=head)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    [head,data] = check_session()
    message=""
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            hashed_password = generate_password_hash(form.password.data, method='sha256')
            new_user = User(username=form.username.data, email=form.email__.data, password=hashed_password, access=0,
                            allow=False, name=form.name__.data, lastname=form.lastname.data, role=1)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            message = "Please complete the form properly"
    return render_template('signup.html', message=message, head=head, form=form,  title='Sign up')


@app.route('/login', methods=['GET', 'POST'])
def login():
    [head,data] = check_session()
    form = LoginForm()
    message = ""
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                if user.access == 3:
                    return redirect(url_for('admindashboard'))
                else:
                    return redirect(url_for('dashboard'))
        message= "Invalid Username or Password"
    return render_template('login.html', message=message, head=head, form=form, title='Login')


@app.route('/admindashboard')
@login_required
def admindashboard():
    [head,data] = check_session()
    data = {'username': current_user.username, 'name': current_user.name, 'lastname': current_user.lastname}
    if current_user.access < 3:
        return redirect(url_for('dashboard'))
    elif current_user.access == 0:
        return redirect(url_for('index'))
    return render_template('admindashboard.html', data=data, head=head, title='Welcome')


@app.route('/dashboard')
@login_required
def dashboard():
    [head,data] = check_session()
    data = {'username': current_user.username, 'name': current_user.name, 'lastname': current_user.lastname}
    if current_user.access == 3:
        return redirect(url_for('admindashboard'))
    return render_template('dashboard.html', data=data, head=head)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/admin-blog-list', methods=['GET', 'POST'])
@login_required
def adminbloglist():
    [head, data] = check_session()
    if current_user.access > 2:
        articles = Article.query.filter_by().all()
        return render_template('admin-blog-list.html', articles=articles, head=head)
    elif current_user.access > 1:
        articles = Article.query.filter_by(id=current_user.id).all()
        return render_template('admin-blog-list.html', articles=articles, head=head)
    else:
        return redirect(url_for('dashboard'))


@app.route('/comment')
@login_required
def comment():
    [head,data] = check_session()
    if current_user.access > 2:
        comments = Comment.query.filter_by(allow=False).all()
    elif current_user.access == 2:
        articles = Article.query.filter_by(id=current_user.id).all()
        comments = []
        for article in articles:
            comment=Comment.query.filter_by(allow=False, id_article=article.id_article).all()
            for c in comment:
                comments.append(c)
    return render_template('comment.html', comments=comments, head=head)


@app.route('/newuser', methods=['GET', 'POST'])
@login_required
def newuser():
    [head,data] = check_session()
    if current_user.access>2:
        users = User.query.filter_by().all()
        users = users[1:]
        return render_template('newuser.html', users=users, head=head)
    else:
        return redirect(url_for('dashboard'))

# ***************************************************************
# URL endpoints for editing database
# ***************************************************************
@app.route('/api/delete_comment')
@login_required
def delete_comment():
    id_comment = request.args.get('id')
    Comment.query.filter_by(id_comment=id_comment).delete()
    db.session.commit()
    return redirect(url_for('comment'))

@app.route('/api/accept_comment')
@login_required
def accept_comment():
    id_comment = request.args.get('id')
    comment = Comment.query.filter_by(id_comment=id_comment).first()
    comment.allow = True
    db.session.commit()
    return redirect(url_for('comment'))

@app.route('/api/author')
@login_required
def become_author():
    id_user = int(request.args.get('id'))
    if current_user.access>2:
        user = User.query.filter_by(id=id_user).first()
        user.access = 2
        user.role = 2
        db.session.commit()
        return redirect(url_for('newuser'))
    else:
        return redirect(url_for('dashboard'))


@app.route('/api/delete')
@login_required
def become_non_user():
    id_user = int(request.args.get('id'))
    if current_user.access>2:
        user = User.query.filter_by(id=id_user).first()
        if user.access == 0:
            User.query.filter_by(id=id_user).delete()
        else:
            user.role = user.access
        db.session.commit()
        return redirect(url_for('newuser'))
    else:
        return redirect(url_for('dashboard'))


@app.route('/api/user')
@login_required
def become_user():
    id_user = int(request.args.get('id'))
    if current_user.access > 2:
        user = User.query.filter_by(id=id_user).first()
        user.access = 1
        user.role = 1
        db.session.commit()
        return redirect(url_for('newuser'))
    else:
        return redirect(url_for('dashboard'))


@app.route('/api/admin')
@login_required
def become_admin():
    id_user = int(request.args.get('id'))
    if current_user.access > 2:
        user = User.query.filter_by(id=id_user).first()
        user.access = 3
        user.role = 3
        db.session.commit()
        return redirect(url_for('newuser'))
    else:
        return redirect(url_for('dashboard'))


@app.route('/api/edit_article')
@login_required
def edit_article():
    [head,data] = check_session()
    id_article = int(request.args.get('id'))
    article = Article.query.filter_by(id_article=id_article).first()
    return render_template('edit.html', article=article, head=head)


@app.route('/api/delete_article')
@login_required
def delete_article():
    id_article = int(request.args.get('id'))
    if current_user.access >= 2:
        Comment.query.filter_by(id_article=id_article).delete()
        Article.query.filter_by(id_article=id_article).delete()
        db.session.commit()
        return redirect(url_for('adminbloglist'))
    else:
        return redirect(url_for('index'))


@app.route('/api/edit_post', methods=['GET', 'POST'])
@login_required
def edit():
    [head,data] = check_session()
    id_article = request.args.get('id')
    tags = str(request.form['tags'])
    title = str(request.form['title'])
    content = str(request.form['article'])

    if request.form['edit'] == 'Edit':
        article = Article.query.filter_by(id_article=id_article).first()
        article.title = title
        article.article = content
        article.tags = tags
        db.session.commit()
        return render_template('select.html', id_article=id_article,head=head)
    else:
        article = Article.query.filter_by(id_article=id_article).first()
        article.title = title
        article.article = content
        article.tags = tags
        db.session.commit()
        return redirect(url_for('adminbloglist'))


@app.route('/change_role',methods=['GET', 'POST'])
@login_required
def change_role():
    [head,data] = check_session()
    if request.method == 'POST':
        user = User.query.filter_by(id=current_user.id).first()
        user.role = str(request.form['choice'])
        db.session.commit()
    return render_template('change_role.html', head=head, name=current_user.name, level=current_user.access)


@app.errorhandler(404)
def error404(error):
    return render_template('404_error.html', title='Invalid')

