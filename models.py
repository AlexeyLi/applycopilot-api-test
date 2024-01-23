# models.py
from flask_login import UserMixin, LoginManager
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
bcrypt = Bcrypt()

login_manager = LoginManager()

# Define the user_loader function
@login_manager.user_loader
def load_user(user_id):
    # This function is used to load a user from the user ID stored in the session
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    hashed_password = db.Column(db.String(255), nullable=False)

    def check_password(self, password):
        # Verify if the provided password matches the stored password hash
        return bcrypt.check_password_hash(self.hashed_password, password)

    def get_id(self):
        return str(self.id)


class UserProfile(db.Model):
    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(255))
    date_of_birth = db.Column(db.Date)
    address = db.Column(db.String(255))
