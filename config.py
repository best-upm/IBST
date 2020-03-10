import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    BASE_URL = os.environ.get('BASE_URL') or 'localhost:5000'
    IMGUR_API_ID = os.environ.get('IMGUR_API_ID') or '99bb3e4c28d3b12'
    IMGUR_API_SECRET = os.environ.get('IMGUR_API_SECRET') or 'c7cf052e456a1fa708f82437c0a990130f46a6f2'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    USER_EMAIL_SENDER_EMAIL = os.environ.get('USER_EMAIL_SENDER_EMAIL') or 'coordiit@bestmadrid.org'
    #MAIL CONFIG
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'alerta.talentum@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'gdanietz'
    MAIL_DEFAULT_SENDER = 'flask@example.com'
    #REDIS Config
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'