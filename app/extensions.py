from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()
jwt = JWTManager()
login_manager = LoginManager()
