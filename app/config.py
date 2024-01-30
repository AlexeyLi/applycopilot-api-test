import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL').replace("://", "ql://", 1)
    SESSION_TYPE = 'filesystem'
    PROPAGATE_EXCEPTIONS = True
