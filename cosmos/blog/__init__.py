from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,UserMixin
import os
import platform

dirpath = os.getcwd()
if platform.system()=='Linux':
    db_path = dirpath + '/blog/database/database.db'
else:
    db_path = dirpath + '\\blog\\database\\database.db'
print('database path: ',db_path,'****')

if not os.path.exists('blog/templates/blog/assets/images/uploads'):
    os.makedirs('blog/templates/blog/assets/images/uploads')
    print('Uploads directory created')
else:
    print('Uploads directory already exists')


UPLOAD_FOLDER = '../cosmos/blog/templates/blog/assets/images/uploads/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__, template_folder='../blog/templates/blog', static_folder='../blog/templates/blog/assets')
app.config['SECRET_KEY'] = "estodebeserunsecreto!"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+db_path
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
Bootstrap(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


from blog import routes

