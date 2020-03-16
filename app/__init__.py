from flask import Flask
#from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_avatars import Avatars
from config import Config
from flask_login import LoginManager
from redis import Redis
from flask_marshmallow import Marshmallow
import rq

app = Flask(__name__)
ma = Marshmallow(app)
avatars = Avatars(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view='login'
bootstrap = Bootstrap(app)
app.redis = Redis.from_url(app.config['REDIS_URL'])
app.task_queue = rq.Queue('BOSS-tasks', connection=app.redis)
from app.errors import bp as errors_bp
app.register_blueprint(errors_bp)
from app.polls import bp as polls_bp
app.register_blueprint(polls_bp)
from app.shortcut import bp as shortcut_bp
app.register_blueprint(shortcut_bp)
from app.api import bp as api_bp
app.register_blueprint(api_bp)
from app.admin import bp as admin_bp
app.register_blueprint(admin_bp)

#socketio = SocketIO(app)

from app import routes, models
