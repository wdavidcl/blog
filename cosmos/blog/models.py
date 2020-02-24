from flask_wtf import FlaskForm
from wtforms import  StringField,PasswordField,BooleanField,TextField
from wtforms.validators import InputRequired, Email, Length
from blog import db,UserMixin

class Article(db.Model):
    id_article = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer)
    title = db.Column(db.String(40))
    tags = db.Column(db.String(20))
    article = db.Column(db.String(600))
    url_image = db.Column(db.String(300))
    data = db.Column(db.LargeBinary)
    timestamp = db.Column(db.DateTime)
    allow = db.Column(db.Boolean)
    author = db.Column(db.String(30))

class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15))
    name = db.Column(db.String(15))
    lastname = db.Column(db.String(15))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80), unique=True)
    access = db.Column(db.Integer)
    role = db.Column(db.Integer)
    allow = db.Column(db.Boolean)

class Comment(db.Model):
    id_comment = db.Column(db.Integer, primary_key=True)
    id_article = db.Column(db.Integer)
    id = db.Column(db.Integer)
    name = db.Column(db.String(15))
    lastname = db.Column(db.String(15))
    comment = db.Column(db.String(300))
    timestamp = db.Column(db.DateTime)
    allow = db.Column(db.Boolean)

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(),Length(min=4,max=15)])
    password = PasswordField('password',validators=[InputRequired(),Length(min=8,max=80)])
    remember = BooleanField('remember me')

class RegistrationForm(FlaskForm):
    username = StringField('Username *', validators=[InputRequired(),Length(min=4,max=15)])
    email__ = StringField('Email *', validators=[InputRequired(),Email('Invalid email')])
    password = PasswordField('Password *',validators=[InputRequired(),Length(min=8,max=80)])
    name__ = StringField('Name *', validators=[InputRequired(),Length(min=4,max=15)])
    lastname = StringField('Lastname *', validators=[InputRequired(),Length(min=4,max=15)])
    remember = BooleanField('remember me')

class BlogForm(FlaskForm):
    title = StringField('Article Title', validators=[InputRequired("Please enter a title"),Length(min=1,max=100)])
    tags = StringField('Tags (separate tags with ;)', validators=[InputRequired("Tag1;Tags2;...")])
    article  = StringField('Content',validators=[InputRequired(),Length(min=10,max=6000)])

class CommentForm(FlaskForm):
    name__ = StringField('Name ', validators=[Length(min=0, max=15)])
    lastname = StringField('Lastname ', validators=[Length(min=0,max=15)])
    comment__  = StringField('Comment this article *',validators=[Length(min=2,max=300)])