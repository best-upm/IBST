from flask import Blueprint

bp = Blueprint('login_blueprint', __name__, url_prefix='', template_folder='templates')

from app.login import login
